from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
# In Finance there's "from tempfile import mkdtemp" but idk what it does
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3
from sqlite3 import Error

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Connect to sqlite3 database
def create_connection():
    connection = None
    try:
        connection = sqlite3.connect('project.db')
        print("Connection to SQLite DB successful")
    except Error as e:
        print(f"The error '{e}' occurred")
    return connection


@app.route("/")
def index():
    return render_template("index.html")


# @app.route("/login", methods=["GET", "POST"])
# def login():
#     """Log user in"""
#     # Forget any user_id
#     session.clear()
# 
#     # User reached route via POST (as by submitting a form via POST)
#     if request.method == "POST":
#
#         # Ensure username was submitted
#         if not request.form.get("username"):
#             return apology("must provide username", 403)
#
#         # Ensure password was submitted
#         elif not request.form.get("password"):
#             return apology("must provide password", 403)
#
#         # Query database for username
#         rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
#
#         # Ensure username exists and password is correct
#         if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
#             return apology("invalid username and/or password", 403)
#
#         # Remember which user has logged in
#         session["user_id"] = rows[0]["id"]
#
#         # Redirect user to home page
#         return redirect("/")
#
#     # User reached route via GET (as by clicking a link or via redirect)
#     else:
#         return render_template("templates/login.html")
#
#
# @app.route("/register", methods=["GET", "POST"])
# def register():
#     """Register user"""
#     # User reached route via POST (as by submitting a form via POST)
#     if request.method == "POST":
#
#         # Ensure username was submitted
#         if not request.form.get("username"):
#             return apology("must provide username", 400)
#
#         # Ensure username does not already exist
#         users = db.execute("SELECT username FROM users")
#         username = request.form.get("username")
#         for dict_item in users:
#             if username == dict_item["username"]:
#                 return apology("username already exists", 400)
#
#         # Ensure password was submitted
#         if not request.form.get("password"):
#             return apology("must provide password", 400)
#
#         # Ensure confirmation password is typed
#         if not request.form.get("confirmation"):
#             return apology("must confirm password", 400)
#
#         # Ensure passwowrd and confirmation match
#         password = request.form.get("password")
#         hashed = generate_password_hash(password)
#         confirmation = request.form.get("confirmation")
#         if password != confirmation:
#             return apology("passwords must match", 400)
#
#         # Inserts login info into 'users' database
#         db.execute("INSERT INTO users (username, hash) VALUES (?, ?)", username, hashed)
#         userID = db.execute("SELECT id FROM users WHERE hash = ?", hashed)
#         userID = userID[0]["id"]
