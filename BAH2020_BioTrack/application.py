import os
import json
import requests

from werkzeug.security import check_password_hash, generate_password_hash

from flask import Flask, session, jsonify, render_template, request, redirect, url_for
from flask_session.__init__ import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
# engine = create_engine(os.getenv("DATABASE_URL"))
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
        return render_template("index.html")

@app.route("/hotlines")
def hotlines():
    return render_template("hotline.html")

@app.route("/understand")
def understand():
    return render_template("understand.html")

@app.route("/destress")
def destress():
    return render_template("destress.html")

@app.route("/aboutus")
def about():
    return render_template("about.html")

@app.route("/register", methods=["POST", "GET"])
def register():

    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        #Make sure all data is collected
        if not request.form.get("username"):
            return render_template("error.html", message="No username has been entered")
        elif not request.form.get("password"):
            return render_template("error.html", message="No password has been entered")
        #Check if username is in the database by making sure there is 0 rows of the username
        if (
            db.execute(
                "SELECT * FROM users WHERE username = :username", {"username": username}
            ).rowcount
            > 0
        ):
            return render_template("error.html", message="The username you entered already exists.")
        else:
            hashedPassword = generate_password_hash(
                request.form.get("password"), method="pbkdf2:sha256", salt_length=8
            )
            db.execute(
                "INSERT INTO users (username, password) VALUES (:username, :password)",
                {"username": username, "password": hashedPassword},
            )
            db.commit()
            #commit changes to data table
            session["user_name"] = username
            session["signedin"] = True
            return render_template("plan.html")
    else:
        return render_template("register.html")


@app.route("/login", methods=["POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        # Get form info.
        username = request.form.get("username")
        password = request.form.get("password")
        #Make sure that all components of the form havee been filled out
        if not request.form.get("username"):
            return render_template("error.html", message="No username has been entered")
        elif not request.form.get("password"):
            return render_template("error.html", message="No password has been entered")
        #Check if username is in the database.
        result = db.execute(
            "SELECT * FROM users WHERE username = :username", {"username": username}
        ).fetchone()
        #prevents hacker from hacking and also makes sure username is in database
        if result == None  or not check_password_hash(result[2], password):
            return render_template(
                "error.html", message="Invalid Username and/or Password"
            )
        else:
            session["user_name"] = result[1]
            session["signedin"] = True
            return render_template("plan.html")

@app.route("/logout")
def logout():
    #forget any user information
    session["user_name"] = None
    session["logged_in"] = False
    session.clear()
    #redirect user to main page
    return render_template("login.html")

posts = []

@app.route("/discuss", methods=["GET", "POST"])
def discuss():
    if request.method == "POST":
        post = request.form.get("post")
        posts.append(post)

    return render_template("discussion.html", posts=posts)

@app.route("/community")
def community():
    #if user is currently logged in, automatically send them to search page
    if session.get("signedin") is True:
        return render_template("plan.html", username = session["user_name"])
    else:
        #if user is not logged in, send them to homepage
        return render_template("login.html")

currentSituation = []
goalOne = []
goalTwo = []
goalThree = []
achieveGoalOne = []
achieveGoalTwo = []
achieveGoalThree = []
problems = []
solutions = []
@app.route("/plan", methods=["GET", "POST"])
def plan():
    if request.method == "POST":
        situation = request.form.get("situation")
        currentSituation.append(situation)
        goalFirst = request.form.get("goalFirst")
        goalOne.append(goalFirst)
        goalSecond = request.form.get("goalSecond")
        goalTwo.append(goalSecond)
        goalThird = request.form.get("goalThird")
        goalThree.append(goalThird)
        achieveGoalFirst = request.form.get("achieveGoalFirst")
        achieveGoalOne.append(achieveGoalFirst)
        achieveGoalSecond = request.form.get("achieveGoalSecond")
        achieveGoalTwo.append(achieveGoalSecond)
        achieveGoalThird = request.form.get("achieveGoalThird")
        achieveGoalThree.append(achieveGoalThird)
        problem = request.form.get("problem")
        problems.append(problem)
        solution = request.form.get("solution")
        solutions.append(solution)

    return render_template("plan.html", currentSituation=currentSituation, goalOne=goalOne, goalTwo=goalTwo, goalThree=goalThree, achieveGoalOne=achieveGoalOne, achieveGoalTwo=achieveGoalTwo, achieveGoalThree=achieveGoalThree, problems=problems, solutions=solutions)
