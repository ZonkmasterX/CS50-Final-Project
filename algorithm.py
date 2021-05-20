# IMPORTS
import math #https://docs.python.org/3/library/math.html
import numpy as np #https://numpy.org
from cs50 import SQL

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")


# CONSTANT VARIABLES
RELPREFERENCEWEIGHT = 2
MINDEDUCTIONS = [0.5, 0.5, 0.5, 0.5]
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
    matrix = np.array([[1, 1, 1, 1],[6, 5, 4, 3],[30, 20, 12, 6],[POINTX^6, POINTX^5, POINTX^4, POINTX^3]])
    return np.matmul(np.array([[1],[0],[0],[POINTY]]), np.linalg.inv(matrix))


def popularityCalc(popularity, popularityvalue, medianPop, maxPop):
    # calculare coefficients
    A = (maxPop - medianPop) / (maxPop - 2 * medianPop)
    B = (A - 1) * maxPop

    # scale it by the function
    unscaled_mp = A * popularity / (popularity + B)

    # scale it by your preferences
    popularity_mp = (1 - uservalue * MINDEDUCTIONS[0]) + popularityvalue * MINDEDUCTIONS[0] * unscaled_mp

    return popularity_mp


def user_scoreCalc(rating, votes, meanVotes, uservalue, coefficients): #includes adjustment for vote count
    #adjust low vote count movies
    adjustedRating = (VOTEWEIGHT * meanVotes + votes * rating) / (VOTEWEIGHT + votes)

    #scale it by the function
    unscaled_mp = adjustedRating^3 * (coefficients[0] * adjustedRating^3 + coefficients[1] * adjustedRating^2 + coefficients[2] * adjustedRating + coefficients[3])

    #scale it by your preferences
    user_score_mp = (1 - uservalue * MINDEDUCTIONS[1]) + uservalue * MINDEDUCTIONS[1] * unscaled_mp

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
        length_mp = (1 - MINDEDUCTIONS[2]) + MINDEDUCTIONS[2] * (x^2 + 1) / ((x^4 + x^3 + x^2 + x + 1) * (x^4 - x^3 + x^2 - x + 1))

        return length_mp


def genresCalc(moviegenres, preferredgenres, genrevalue):
    matches = 0

    # iterate over genres to see if any/how many match
    for genre in moviegenres:
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
    movieCount = db.execute("SELECT COUNT(*) FROM movie_data")
    # Reset final scores
    db.execute("UPDATE movie_data SET final_score = 0")
    # Count the mean score (i.e. what the typical vote a user submits on a movie is)
    meanScore = db.execute("SELECT SUM(vote_average * vote_count) / SUM(vote_average) FROM movie_data")
    #Calculate the median and maximum popularity
    medianPop = db.execute("SELECT MEDIAN(popularity) FROM movie_data")
    maxPop = db.execute("SELECT MAX(popularity) FROM movie_data")
    #determine coefficients for user score function
    coefficients = matrixCalc()

    #adjust preferences
    preferences = {}
    psum = int(info["popularityvalue"]) + int(info["uservalue"]) + int(info["lengthvalue"])+ int(info["genrevalue"])
    for category in ["popularityvalue", "uservalue", "lengthvalue", "genrevalue"]:
        preferences[category] = (int(info[category]) / 10) + (int(info[category])/psum)

    # iterates over each movie
    for i in range(movieCount):
        moviedata = db.execute("SELECT release_year, runtime, popularity, vote_average, vote_count, rating, genres FROM movie_data where ID = ?", i)[0]

        # Filter out by release year and MPAA rating
        if isdigit(info["minyear"]):
            if moviedata["release_year"] <= int(info["minyear"]):
                continue
        if isdigit(info["maxyear"]):
            if moviedata["release_year"] >= int(info["maxyear"]):
                continue
        # MAKE SURE THAT MOVIEDATA RATINGS AND INFO RATINGS ARE IN THE SAME FORMAT!!!
        if info["rating"][moviedata["rating"]] == False:
            continue


        # multiplies all multipliers together to find final score
        popularity_mp = popularityCalc(moviedata["popularity"], int(info["popularityvalue"]), medianPop, maxPop)
        user_score_mp = user_scoreCalc(moviedata["vote_average"], moviedata["vote_count"], meanScore, preferences["uservalue"], coefficients)
        length_mp = lengthCalc(moviedata["runtime"], preferences["lengthvalue"], int(info["preferredlength"]))
        genres_mp = genresCalc(moviedata["genres"], info["genres"], preferences["genrevalue"])

        final_score = popularity_mp * user_score_mp * length_mp * genres_mp

        # Updates movie_scores table
        db.execute("UPDATE movie_data SET final_score = ? WHERE id = ?", final_score, i)

    # TODO: If any final scores are 0, [DO SOMETHING]
