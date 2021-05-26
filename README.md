# CS50 Final Project: Movie recommendation system
#### Video Demo:  <URL HERE>
#### Description:
    This project was completed by Liam Barthelmy and Evan Fleischer in an attempt to make
a movie recommendation system via a web app in which the user inputs his/her preferences
for certain movie qualities/characteristics, and then the system does some math for every
movie to then output a tailored list of movies for the user.

    To begin, the main (and currently the only page) is index.html, on which the user is
greeted and then asked to input on 4 sliders, on a scale of 1 to 10, how much they care
about a movie's user score (0 - 100%), its current popularity, its length (runtime), and
the genres the movie fits into. Below, the user is prompted to input their preferred
runtime, and optionally, their preferred release year window (a range of years they would
like to see in which a movie came out), their preferred MPAA rating (G, PG-13, etc), and
their preferred genres. We consciously decided that the release year window, ratings,
and genres should be optional, so if none are selected, the resulting movies will not be
filtered according to the criteria left blank. Lastly, there is a slider for the user to
choose how many recommendations they would like on a scale from 1 to 100 (default is 10).

    Once the user clicks the recommend button, the index.html document will send the
user's preferences to application.py via an XML HTTP request, where a function in
algorithm.py is called to perform the match on the movies and create a list of
recommendations.

    To get the necessary information about the movies to be able to perform any math,
we used an API from the online service TMDB (The Movie Database) since it is free, as
opposed to IMDB's API, which is not. In populateDatabase.py, the function lookup() performs
an API call for a movie (identified by its IMDB, not its TMDB, ID) and returns the movie's
IMDB ID, TMDB ID, title, release year, runtime, popularity, user score, vote count (how
many ratings it received), MPAA rating, and genres. Then, the function populate() takes an
IMDB ID and number of IDs to cycle through to create a database of movie data, inputted
into a SQLite3 database called "movie_info".

    In algorithm.py, we created an algorithm through hours of work and tweaking that we
believe effectively scores movies based on the user's preferences and each movie's
information. For example, if a user sets their user score preference to 8 out of 10,
movies' user scores will be scored more harshly than if the user set their user score
preference to 2 out of 10. Thus is the case with the three other slider preferences.
For MPAA ratings, any movie with an MPAA rating not chosen by the user will not even be
scored, and the more genres that the user chooses that a movie fits into, the higher the
movie's score will be.

    To actually come up with a final score, each movie starts with a final score of 1
(100%), and 4 four multipliers are generated (based on user score, popularity, length, and
genres) to generate a final score for each movie. For example, a movie could end up with
a user score multiplier of 0.96, a popularity multiplier of 0.82, a length multiplier of
0.87, and a genres multiplier of 0.90, generating a final score of 0.6164, or 61.64% (1 *
0.96 * 0.82 * 0.87 * 0.90 = 0.6164).

    Lastly, this data is returned to index.html via json.dumps(), where a table is
generated at the bottom of the page that contains the title and final score (match
percent) of the amount of movies that the user chose to have recommended to them in
descending order of match percent (top match first, second best match next, etc).

Design choices:
1) We chose to use an XML HTTP request once the recommend button is clicked as to tighten
up the user experience and not have to load another page. Also, with the table on the same
page, the user can see their chosen preferences, change their preferences if they wish,
and have other recommendations generated all on one simple page.
2) If you look at the algorithm.py document, you will see that the math used to score each
movie is very complicated and involves calculus. We wanted our algorithm to be very
specific, powerful, and dynamic, taking input from many variables to allow for high
precision in generating recommendations.
3) Originally, we wanted to include a login function to allow users to save their
preferences and potentially other functionalities, but we quickly realized that just the
main page and movie recommendation functionality is a lot to work on and definitely enough
of a challenge for this two-person project. In the future, if we were to make this a
public and even monetized service, we would include more functionalities, along with
paying for the IMDB API.

## MOTIVE BEHIND PROJECT
The impetus for this project arose from the realization that many current recommendation
services (Amazon, Netflix, etc) just output recommendations for the user seemingly
magically without any user input. Thus, we thought it would be very useful to create a
service that allows the user tight control over the results they receive and the 
preferences that led to their recommendations.
