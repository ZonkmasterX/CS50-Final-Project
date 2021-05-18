# IMPORTS
import math #https://docs.python.org/3/library/math.html


# CONSTANT VARIABLES



# IMPORTED PREFERENCES FROM INDEX.HTML




# FUNCTIONS
def popularityCalc():
    return popularity_mp

def user_scoreCalc(): #includes adjustment for vote count
    return user_score_mp

def lengthCalc():
    return length_mp

def genresCalc():
    return genres_mp



# Recreates movie_scores table
def redoTable():
    db.execute("DROP TABLE IF EXISTS movie_scores")
    db.execute("CREATE TABLE movie_scores (ID INT, imdb_id TEXT, title TEXT, final_score REAL, PRIMARY KEY (ID));"")
    db.execute("INSERT INTO movie_scores (imdb_id, title) SELECT imdb_id, title FROM movie_data")


# Generates final scores
def makeithappen():
    redoTable()
    # Count how many movies there are in the database
    movieCount = db.execute("SELECT COUNT(*) FROM movie_data")

    # iterates over each movie
    for i in range(movieCount):

        #multiplies all multipliers together to find final score
        popularity_mp = popularityCalc()
        user_score_mp = user_scoreCalc()
        length_mp = lengthCalc()
        genres_mp = genresCalc()

        final_score = popularity_mp * user_score_mp * length_mp * genres_mp

        # Updates movie_scores table
        db.execute("UPDATE movie_scores SET final_score = ? WHERE ID = ?", final_score, i)
