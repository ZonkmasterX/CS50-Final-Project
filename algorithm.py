# IMPORTS
import math #https://docs.python.org/3/library/math.html


# CONSTANT VARIABLES



# IMPORTED PREFERENCES FROM INDEX.HTML




# FUNCTIONS (all should return a multiplier in the form of [function name]_mp)
    # In application.py in index, for each movie, all multipliers will be
    # multiplied together to find the final score for each movie, and then
    # this score will be added to the SQL table (to be created) called "movie_scores"
    # with 3 columns: imdb_id, title, and final_score (final_score is the percent match)


def popularityCalc:
    return popularity_mp

def user_scoreCalc: #includes adjustment for vote count
    return user_score_mp

def lengthCalc:
    return length_mp

def genresCalc:
    return genres_mp
