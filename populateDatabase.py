import os
import requests
import urllib.parse
from pprint import pprint


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
        print(response.status_code)
        # pprint(data["release_dates"]["results"])
        rating = "placeholder"

        # https://stackoverflow.com/a/4391978/6568837
        for i, dic in enumerate(data["release_dates"]["results"]):
            if dic["iso_3166_1"] == "US":
                rating = data["release_dates"]["results"][i]["release_dates"][0]["certification"]

        genres = []
        for i in range(len(data["genres"])):
            genres.append(data["genres"][i]["name"])

        return {
            "imdb_id": data["imdb_id"],
            "tmdb_id": data["id"],
            "title": data["title"],
            "release_date": data["release_date"],
            "runtime": data["runtime"],
            "vote_average": data["vote_average"],
            "vote_count": data["vote_count"],
            "genres": data["genres"],
            "rating": rating,
            "genres": genres
        }
    except (KeyError):
        return "KeyError"
    except (TypeError):
        return "TypeError"
    except (ValueError):
        return "ValueError"

print(lookup("tt0451279"))
