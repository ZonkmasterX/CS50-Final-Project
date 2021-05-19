# IMPORTS
import math #https://docs.python.org/3/library/math.html
import numpy as np #https://numpy.org


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
    #constructs a function for scaling rating based on an input point
    matrix = np.array([[1, 1, 1, 1],[6, 5, 4, 3],[30, 20, 12, 6],[POINTX^6, POINTX^5, POINTX^4, POINTX^3]])
    return np.matmul(np.array([[1],[0],[0],[POINTY]]), np.linalg.inv(matrix))


def popularityCalc():
    return popularity_mp


def user_scoreCalc(rating, votes, meanVotes, uservalue, coefficients): #includes adjustment for vote count
    #adjust low vote count movies
    adjustedRating = (VOTEWEIGHT * meanVotes + votes * rating) / (VOTEWEIGHT + votes)

    #scale it by the function
    unscaled_mp = adjustedRating^3 * (coefficients[0] * adjustedRating^3 + coefficients[1] * adjustedRating^2 + coefficients[2] * adjustedRating + coefficients[3])

    #scale it by your Preferences
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



# Recreates movie_scores table
def redoTable():
    db.execute("DROP TABLE IF EXISTS movie_scores")
    db.execute("CREATE TABLE movie_scores (ID INT, imdb_id TEXT, title TEXT, final_score REAL, PRIMARY KEY (ID));"")
    db.execute("INSERT INTO movie_scores (imdb_id, title) SELECT imdb_id, title FROM movie_data")


# Generates final scores
def makeithappen(info):
    redoTable()
    # Count how many movies there are in the database
    movieCount = db.execute("SELECT COUNT(*) FROM movie_data")
    # Count the mean score (i.e. what the typical vote a user submits on a movie is)
    meanScore = db.execute("SELECT SUM(vote_average * vote_count) / SUM(vote_average) FROM movie_data")
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


        # TODO: Filter out by release year and MPAA rating


        # multiplies all multipliers together to find final score
        popularity_mp = popularityCalc()
        user_score_mp = user_scoreCalc(moviedata["vote_average"], moviedata["vote_count"], meanScore, preferences["uservalue"], coefficients)
        length_mp = lengthCalc(moviedata["runtime"], preferences["lengthvalue"], int(info["preferredlength"]))
        genres_mp = genresCalc(moviedata["genres"], info["genres"], preferences["genrevalue"])

        final_score = popularity_mp * user_score_mp * length_mp * genres_mp

        # Updates movie_scores table
        db.execute("UPDATE movie_scores SET final_score = ? WHERE ID = ?", final_score, i)
