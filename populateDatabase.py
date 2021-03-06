import os
import requests
import urllib.parse
from pprint import pprint
import re
from cs50 import SQL

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///project.db")


def lookup(IMDBID):
    """Look up movie."""

    # Contact API
    try:
        # api_key = os.environ.get("API_KEY")
        api_key = "3af3077f67aa942f64d1ef54c4b6ef59"
        url = f"https://api.themoviedb.org/3/movie/{urllib.parse.quote_plus(IMDBID)}?api_key={api_key}&append_to_response=release_dates"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        data = response.json()
        # ensure language is English
        if data["original_language"] != "en":
            return None
        # print(response.status_code)
        # pprint(data["release_dates"]["results"])

        # handle Rating
        # https://stackoverflow.com/a/4391978/6568837
        rating = ""
        for i, dic in enumerate(data["release_dates"]["results"]):
            if dic["iso_3166_1"] == "US":
                rating = data["release_dates"]["results"][i]["release_dates"][0]["certification"]

        # handle Genres
        genres = []
        for i in range(len(data["genres"])):
            genres.append(data["genres"][i]["name"])
        gString = ", ".join(genres)
        if gString == "":
            gString = "NA"

        return {
            "imdb_id": data["imdb_id"],
            "tmdb_id": data["id"],
            "title": data["title"],
            "release_year": int(data["release_date"][0:4]),
            "runtime": data["runtime"],
            "popularity": data["popularity"],
            "vote_average": data["vote_average"],
            "vote_count": data["vote_count"],
            "rating": rating,
            "genres": gString
        }
    except (KeyError, TypeError, ValueError):
        return None


def increment(ID):
    """Increment ID by 1"""

    # https://stackoverflow.com/a/67505817/6568837
    newID = f'tt{int(ID.lstrip("t"))+1:07}'
    return newID


def populate(ID, number):
    """populate database"""

    # 0499243
    # next is tt0463291
    # ID = "tt1950183"
    for i in range(number):

        # next ID
        ID = increment(ID)

        # lookup movie
        data = lookup(ID)

        # ensure movie is in TMDB database
        if data != None:

            # Ensure no values are None
            for key, value in data.items():
                if data[key] is None:
                    data[key] = 1

            # disregard movies with  NC-17 or X ratings
            if data["rating"] == "X" or data["rating"] == "NC-17":
                continue

            # Input data into database
            try:
                db.execute("INSERT INTO movie_data (imdb_id, tmdb_id, title, release_year, runtime, popularity, vote_average, vote_count, genres, rating) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", data["imdb_id"], data["tmdb_id"], data["title"], data["release_year"], data["runtime"], data["popularity"], data["vote_average"], data["vote_count"], data["genres"], data["rating"])
            except (ValueError):
                continue


def updatedb():
    """updates database with current information"""

    # makes list of IMDB_IDs to use from database
    ids = []
    imdb_ids = db.execute("SELECT imdb_id FROM movie_data")
    for dic in imdb_ids:
        for val in dic.values():
            ids.append(val)

    # Iterates over every ID
    for id in ids:

        # lookup movie
        data = lookup(id)

        # ensure movie is in TMDB database
        if data != None:

            # Ensure no values are None
            for key, value in data.items():
                if data[key] is None:
                    data[key] = 1

            # updates database with movie data
            try:
                db.execute("UPDATE copy SET tmdb_id = ?, title = ?, release_year = ?, runtime = ?, popularity = ?, vote_average = ?, vote_count = ?, genres = ?, rating = ? WHERE imdb_id = ?", data["tmdb_id"], data["title"], data["release_year"], data["runtime"], data["popularity"], data["vote_average"], data["vote_count"], data["genres"], data["rating"], id)
            except (ValueError):
                continue



updatedb()
ID = "tt0796066"
#print(lookup("tt1950186"))
#populate(ID, 1000)


# tt0765029 + 1000
# tt0443053 + 1000
# tt0252003 + 10000 big
