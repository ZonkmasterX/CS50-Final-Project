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

        return {
            "imdb_id": data["imdb_id"],
            "tmdb_id": data["id"],
            "title": data["title"],
            "release_year": int(data["release_date"][0:4]),
            "runtime": data["runtime"],
            "vote_average": data["vote_average"],
            "vote_count": data["vote_count"],
            "rating": rating,
            "genres": gString
        }
    except (KeyError):
        return "KeyError"
    except (TypeError):
        return "TypeError"
    except (ValueError):
        return "ValueError"


def increment(ID):
    """Increment ID by 1"""

    # https://stackoverflow.com/a/67505817/6568837
    newID = f'tt{int(ID.lstrip("t"))+1:07}'
    return newID


def populate():
    """populate database"""

    ID = "tt1000000"
    for i in range(100):
        data = lookup(ID)
        if data != None:
            try:
                # Input data into database
                db.execute("INSERT INTO movie_data VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", data["imdb_id"], data["tmdb_id"], data["title"], data["release_year"], data["runtime"], data["vote_average"], data["vote_count"], data["genres"], data["rating"])
            except (ValueError):
                continue
        ID = increment(ID)


#print(lookup("tt1000093"))
populate()
