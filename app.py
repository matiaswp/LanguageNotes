from flask import Flask
from flask import redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy
from os import getenv

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")

@app.route("/")
def index():
    return render_template("login.html")

@app.route("/login",methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    
    session["username"] = username
    return redirect("/home")

@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/home")
def home():
    return render_template("home.html")

