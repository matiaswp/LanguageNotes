from flask import Flask
from flask import redirect, render_template, request, session
from os import getenv
import database
import userlists
import userlist
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)

#Handles requests to "/" (redirects to login page)
@app.route("/")
def index():
    return render_template("login.html")

#Logs you in only and only if you somehow remember your password (Handles logins)
@app.route("/login",methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    #This is where we check if the username and password you entered are valid
    if database.checkCreditals(db, username, password) == True:
        session["username"] = username
        return redirect("/home")
    #TODO if password or username wrong show a message
    else:
        return redirect("/")
    
#Logs you out
@app.route("/logout")
def logout():
    username = ""
    del session["username"]
    return redirect("/")

#Shows home page
@app.route("/home")
def home():
    #The next line is only temporary and for testing purposes
    messages = database.users(db) 
    return render_template("home.html", messages=messages)

#Shows register page
@app.route("/register")
def registerPage():
    return render_template("register.html")

#For creating a new account
@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password = request.form["password"]
    retypedPassword = request.form["retypedPassword"]

    if password == retypedPassword:
        if database.createAccount(db, username, password) == False:
            return redirect("/register")
        else:
            return redirect("/")
    #if passwords doesnt match, reloads the page 
    #TODO show message that passwords don't match
    else:
        return redirect("/register")

#Shows lists page
@app.route("/lists")    
def lists():
    username = session["username"]
    print(username)
    usersList = userlists.listLists(db,username)
    return render_template("lists.html", lists=usersList)

#For creating a new list
@app.route("/lists", methods=["POST"])
def listsNewList():
    
    username = session["username"]
    name = request.form["listname"]
    value = request.form["listname"]
    userlists.createNewList(db, username, name)
    return redirect("/lists")

@app.route("/lists/<username>/<name>")
def showlist(username, name):
    username = session["username"]
    cards = userlist.showCards(db, username, name)
    return render_template("list.html", name=name, cards=cards)

@app.route("/lists/<username>/<name>", methods=["POST"])
def newCardToList(username, name):
    word = request.form["word"]
    
    translation = request.form["translation"]
    userlist.addCardToList(db,username,name,word,translation)
    return redirect("/lists/" + username + "/" + name)

@app.route("/edit/<name>", methods=["POST"])
def editList(name):
    username = session["username"]

    if request.form['btn'] == 'edit':
        
        return redirect("/")
    else:
        userlists.deleteList(db,username,name)
        return redirect("/lists")

def editCard():
    i=0