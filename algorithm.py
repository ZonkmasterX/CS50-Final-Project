# IMPORTS
import math #https://docs.python.org/3/library/math.html
import numpy as np #https://numpy.org
from cs50 import SQL

# for debugging purposes
import logging

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")


# CONSTANT VARIABLES
RELPREFERENCEWEIGHT = 2
MAXDEDUCTIONS = [0.5, 0.5, 0.5, 0.5]
VOTEWEIGHT = 5
POINTX = 0.5
POINTY = 0.5
MINLENGTHDEV = 15
MAXGENREDEDUCTION = 0.5
MAXGENREADDITION = 0.05

# IMPORTED PREFERENCES FROM INDEX.HTML




# FUNCTIONS
def matrixCalc():
    """constructs a function for scaling rating based on an input point"""
    matrix = np.array([[1, 1, 1, 1],[6, 5, 4, 3],[30, 20, 12, 6],[POINTX**6, POINTX**5, POINTX**4, POINTX**3]])
    return np.matmul(np.linalg.inv(matrix), np.array([[1],[0],[0],[POINTY]]))


def popularityCalc(popularity, popularityvalue, medianPop, maxPop):
    # calculare coefficients
    A = (maxPop - medianPop) / (maxPop - 2 * medianPop)
    B = (A - 1) * maxPop

    # scale it by the function
    unscaled_mp = (A * popularity) / (popularity + B)

    # scale it by your preferences
    popularity_mp = (1 - popularityvalue * MAXDEDUCTIONS[0]) + popularityvalue * MAXDEDUCTIONS[0] * unscaled_mp

    # logging.debug(str(popularityvalue) + " " + str(MAXDEDUCTIONS[0]) + " " + str(popularity_mp) + " " + str(unscaled_mp))

    return popularity_mp


def user_scoreCalc(rating, votes, meanVotes, uservalue, coefficients): #includes adjustment for vote count
    #adjust low vote count movies
    adjustedRating = (VOTEWEIGHT * meanVotes + votes * rating) / (10 * (VOTEWEIGHT + votes))

    #scale it by the function from matrixCalc
    unscaled_mp = adjustedRating**3 * (coefficients[0] * adjustedRating**3 + coefficients[1] * adjustedRating**2 + coefficients[2] * adjustedRating + coefficients[3])

    #scale it by your preferences
    user_score_mp = (1 - uservalue * MAXDEDUCTIONS[1]) + uservalue * MAXDEDUCTIONS[1] * unscaled_mp

    return user_score_mp


def lengthCalc(runtime, lengthvalue, preferredlength):
    if lengthvalue == 0:
        return 1
    else:
        lengthdifference = preferredlength - runtime

        #adjust to unit deviations based on preference
        lengthdifference *= lengthvalue / MINLENGTHDEV

        #I don't want to type lengthdifference a million times here
        x = lengthdifference
        #scale multiplier by special function
        length_mp = (1 - MAXDEDUCTIONS[2]) + MAXDEDUCTIONS[2] * (x**2 + 1) / ((x**4 + x**3 + x**2 + x + 1) * (x**4 - x**3 + x**2 - x + 1))

        return length_mp


def genresCalc(moviegenres, preferredgenres, genrevalue):
    matches = 0

    # iterate over genres to see if any/how many match
    for genre in moviegenres:
        if genre in preferredgenres:
            if preferredgenres[genre] == True:
                matches += 1

    #determine multiplier
    if matches == 0:
        genres_mp = 1 - (MAXGENREDEDUCTION * genrevalue)
    else:
        genres_mp = 1 + (MAXGENREADDITION * genrevalue * (matches - 1))
    return genres_mp


def makeithappen(info):
    """Generates final scores"""

    # Count how many movies there are in the database
    movieCount = db.execute("SELECT COUNT(*) FROM movie_data")[0]["COUNT(*)"]
    # Reset final scores
    db.execute("UPDATE movie_data SET final_score = 0")
    # Count the mean score (i.e. what the typical vote a user submits on a movie is)
    meanScore = db.execute("SELECT SUM(vote_average * vote_count) / SUM(vote_count) FROM movie_data")[0]["SUM(vote_average * vote_count) / SUM(vote_count)"]
    #Calculate the median and maximum popularity


    # Median function does not exist, this is the workaround https://stackoverflow.com/questions/15763965/how-can-i-calculate-the-median-of-values-in-sqlite
    # Median actually ignores movies with minimum popularity of 0.6 because they comprise more than half the sample lol. We might need to completely change the popularity function
    medianPop = db.execute("SELECT AVG(popularity) FROM (SELECT popularity FROM movie_data ORDER BY popularity DESC LIMIT 2 - (SELECT COUNT(*) FROM movie_data) % 2 OFFSET (SELECT (COUNT(*) - 1) / 2 FROM movie_data WHERE popularity > 0.6))")[0]["AVG(popularity)"]
    maxPop = db.execute("SELECT MAX(popularity) FROM movie_data")[0]["MAX(popularity)"]
    # determine coefficients for user score function
    matrix = matrixCalc()
    coefficients = [matrix[0][0], matrix[1][0], matrix[2][0], matrix[3][0]]

    #adjust preferences
    preferences = {}
    psum = int(info["popularityvalue"]) + int(info["uservalue"]) + int(info["lengthvalue"])+ int(info["genrevalue"])
    if psum == 0:
        for category in ["popularityvalue", "uservalue", "lengthvalue", "genrevalue"]:
            preferences[category] = 0
    else:
        for category in ["popularityvalue", "uservalue", "lengthvalue", "genrevalue"]:
            preferences[category] = ((int(info[category]) / 10) + RELPREFERENCEWEIGHT * (int(info[category])/psum)) / (RELPREFERENCEWEIGHT + 1)

    # iterates over each movie, +1 bc ids appear to start at 1 rn? Might need to change if there's a possibility of skipping ids too
    for i in range(movieCount + 1):
        moviedata = db.execute("SELECT release_year, runtime, popularity, vote_average, vote_count, rating, genres FROM movie_data where ID = ?", i)

        # Make sure we found an actual movie
        if len(moviedata) == 0:
            continue

        moviedata = moviedata[0]

        # Filter out by release year and MPAA rating
        if info["minyear"]:
            if moviedata["release_year"] <= int(info["minyear"]):
                continue
        if info["maxyear"]:
            if moviedata["release_year"] >= int(info["maxyear"]):
                continue
        # Format should match up now, first line is to filter out NR movies and anything else weird to prevent keyerrors
        if moviedata["rating"] in ["G", "PG", "PG-13", "R"]:
            if info["ratings"][moviedata["rating"]] == False:
                continue


        # multiplies all multipliers together to find final score
        popularity_mp = popularityCalc(moviedata["popularity"], preferences["popularityvalue"], medianPop, maxPop)
        user_score_mp = user_scoreCalc(moviedata["vote_average"], moviedata["vote_count"], meanScore, preferences["uservalue"], coefficients)
        length_mp = lengthCalc(moviedata["runtime"], preferences["lengthvalue"], int(info["preferredlength"]))


        # hopefully the split works properly, also formatting should match up
        if moviedata["genres"]:
            genres_mp = genresCalc(moviedata["genres"].split(", "), info["genres"], preferences["genrevalue"])
        else:
            genres_mp = 1

        final_score = popularity_mp * user_score_mp * length_mp * genres_mp
        if final_score > 1:
            final_score = 1.0

        # Debug message
        #logging.debug(str(popularity_mp) + " " + str(moviedata["popularity"]) + " " + str(preferences["popularityvalue"]))

        # Updates debug table
        # db.execute("UPDATE debug SET final_score = ?, user_score = ?, user_score_p = ?, user_score_mp = ?, popularity = ? WHERE id = ?", float(final_score), moviedata["vote_average"], int(preferences["uservalue"]), float(user_score_mp), moviedata["popularity"], i)
        # db.execute("UPDATE debug SET popularity_p = ?, popularity_mp = ?, length = ?, length_p = ?, length_mp = ? WHERE id = ?", int(preferences["popularityvalue"]), float(popularity_mp), moviedata["runtime"], int(preferences["lengthvalue"]), float(length_mp), i)
        # db.execute("UPDATE debug SET genres_p = ?, genres_mp = ? WHERE id = ?", int(preferences["genrevalue"]), float(genres_mp), i)

        # Updates movie_scores table
        db.execute("UPDATE movie_data SET final_score = ? WHERE id = ?", float(final_score), i)
