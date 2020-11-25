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

    return render_template("home.html")

#Shows register page
@app.route("/register")
def register_page():
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

#Shows lists and creates new lists
@app.route("/user/<username>/mylists", methods=["GET", "POST"])    
def lists(username):
    access = "false"
    if request.method == "POST":
        if session["username"] != username:
            return redirect("/user/" + username + "/mylists")
        username = session["username"]
        name = request.form["listname"]
        if name.strip() == "":
            return redirect("/user/" + username + "/mylists")
    
        userlists.create_new_list(db, username, name)
        return redirect("/user/" + username + "/mylists")
    else:       
        if session["username"] == username:
            user_list = userlists.listLists(db,username)
            return render_template("mylists.html", lists=user_list, access=access)
        else:
            return redirect("/user/" + session["usernane"] + "/mylists")
        
#Shows cards in list
@app.route("/user/<username>/mylists/<listname>")
def show_list(username, listname):
    username = session["username"]
    cards = userlist.showCards(db, username, listname)
    return render_template("mylist.html", listname=listname, cards=cards)

#Create new card in list
@app.route("/user/<username>/mylists/<listname>", methods=["POST"])
def new_card_to_list(username, listname):
    word = request.form["word"]
    
    translation = request.form["translation"]
    userlist.addCardToList(db,username, listname, word, translation)
    return redirect("/user/" + username + "/mylists/" + listname)

#Deletes a list
@app.route("/user/<username>/mylists/<listname>/delete", methods=["POST"])
def delete_list(username, listname):
    if session["username"] != username:
        return redirect("/user/" + username + "/mylists")
    username = session["username"]
    userlists.deleteList(db, username, listname)
    return redirect("/user/" + username + "/mylists")

#Edits a list
@app.route("/user/<username>/mylists/<listname>/edit", methods=["POST"])
def edit_list(username, listname):
    if session["username"] != username:
        return redirect("/user/" + username + "/mylists")
    username = session["username"]
    listname = request.form["listname"]
    newName = request.form["newName"]
    print(newName)
    userlists.editList(db, username, listname, newName)
    return redirect("/user/" + username + "/mylists")

#Delete a card in list
@app.route("/user/<username>/mylists/<listname>/deletecard", methods=["POST"])
def delete_card(username, listname):
    if session["username"] != username:
        return redirect("/user/" + username + "/mylists/" + listname)
    username = session["username"]
    word = request.form["word"]
    translation = request.form["translation"]
    userlist.remove_card_from_list(db, username, listname, word, translation)
    return redirect("/user/" + username + "/mylists/" + listname)

#Edit the contents of a card
@app.route("/user/<username>/mylists/<listname>/editcard", methods=["POST"])
def edit_card(username, listname):
    if session["username"] != username:
        return redirect("/user/" + username + "/mylists/" + listname)
    word = request.form["word"]
    translation = request.form["translation"]
    new_word = request.form["newWord"]
    new_translation = request.form["newTranslation"]
    userlist.editCard(db, listname, username, word, translation, new_word, new_translation)
    return redirect("/user/" + username + "/mylists/" + listname)

#Shows flashcard mode
@app.route("/user/<username>/mylists/<listname>/study", methods=["GET", "POST"])
def flashcard(username, listname):
    if request.method == "POST":
        word = request.form["word"]
        translation = request.form["translation"]

        if request.form.action == "Got it!":
            userlist.add_more_date(db, username, listname, word, translation, "correct")
        else:
            userlist.add_more_date(db, username, listname, word, translation, "wrong")

        return True
    else:
        username = session["username"]
        cards = userlist.showCards(db, username, listname)
        length = len(cards)
        return render_template("flashcard.html", cards=cards, length=length, 
        listname=listname)

#Shows user's profile page. You can also clone other users' lists to you own collection here
@app.route("/user/<username>/profile")
def profile(username):
    user_list = userlists.listLists(db,username)
    if user_list == False:
        return render_template("profile.html", username="User does not exist", lists="")
    return render_template("profile.html", lists=user_list, username=username)

#Edit your profile
@app.route("/user/<username>/profile/edit")
def edit_profile(username):
    return render_template("editprofile.html")

#Shows a list of a given user
@app.route("/user/<username>/lists/<listname>")
def user_list(username, listname):
    return render_template(".html")

#Shows who you are following
app.route("/user/<username>/following")
def following(username):
    return render_template("following.html")

#Shows info/about page
@app.route("/info")
def info_about():
    return render_template("infoabout.html")

#Used to search people
@app.route("/search", methods=["POST"])
def search():
    username = request.form["search"]
    return redirect("/user/" + username + "/profile")