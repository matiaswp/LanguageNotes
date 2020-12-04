from flask import Flask
from flask import redirect, render_template, request, session, url_for
from os import getenv
import database
import userlists
import userlist
import editprofile
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)

"""Handles requests to "/" (redirects to login page)"""
@app.route("/")
def index():
    return render_template("login.html")

"""Logs you in only and only if you somehow remember your password (Handles logins)"""
@app.route("/login",methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    
    if database.check_credentials(db, username, password) == True:
        session["username"] = username
        return redirect("/home")
    #TODO if password or username wrong show a message
    else:
        message = "Username or password incorrect"
        return render_template("login.html", message=message)
    
"""Logs you out"""
@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

"""Shows home page"""
@app.route("/home")
def home():
    return render_template("home.html")

"""Shows register page"""
@app.route("/register", methods=["GET", "POST"])
def register_page():
    message = ""
    if request.method == "POST":
        
        username = request.form["username"]
        password = request.form["password"]
        retyped_password = request.form["retypedPassword"]
        stripusername = username.strip()
        strippw = password.strip()
        
        if stripusername == "" or strippw == "":
            message = "Can't create account with empty credentials"
            return render_template("register.html", message=message)

        if len(username) > 16 or len(username) < 3:
            message = "Username too short or too long"
            return render_template("register.html", message=message)

        if len(password) > 16 or len(password) < 6:
            message = "Password is too short or too long"
            return render_template("register.html", message=message)

        if password == retyped_password:
            if database.create_account(db, username, password) == False:
                message = "Username taken"
                return render_template("register.html", message=message)
            else:
                return redirect("/")
        else:
            message = "Passwords didn't match"
            return render_template("register.html", message=message)
    else:
        return render_template("register.html", message=message)

"""Shows session ownwer's lists. IF username does not match to session username
Then redirect to session username's lists page."""
@app.route("/user/<username>/mylists", methods=["GET", "POST"])    
def mylists(username):
    try:
        message = request.args("message")
    except:
        message = ""
    if request.method == "POST":
    
        if session["username"] != username:
            return redirect("/user/" + session["username"] + "/mylists")

        username = session["username"]
        name = request.form["listname"]

        #If name empty, redirect same page. TODO add error message.
        if name.strip() == "":
            return redirect("/user/" + session["username"] + "/mylists")

        userlists.create_new_list(db, username, name)
        return redirect("/user/" + username + "/mylists")
    else:
        if session["username"] == username:
            user_list = userlists.list_lists(db,username)
            return render_template("mylists.html", lists=user_list, message=message)
        else:
            return redirect("/user/" + session["username"] + "/mylists")
        
"""Shows cards in list"""
@app.route("/user/<username>/mylists/<listname>", methods=["POST", "GET"])
def show_list(username, listname):

    username = session["username"]
    cards = userlist.show_cards(db, username, listname)

    if request.method == "POST":
        word = request.form["word"]
        translation = request.form["translation"]

        if word.strip() == "" or translation.strip() == "":
            message = "Can't create a card with empty values"
            return render_template("mylist.html", listname=listname, cards=cards, 
            message=message)
        message = ""
        userlist.add_card_to_list(db,username, listname, word, translation)
        return redirect("/user/" + username + "/mylists/" + listname)
    else:
        username = session["username"]
        cards = userlist.show_cards(db, username, listname)
        message = ""
        return render_template("mylist.html", listname=listname, cards=cards, message=message)

"""Deletes a list"""
@app.route("/user/<username>/mylists/<listname>/delete", methods=["POST"])
def delete_list(username, listname):
    if session["username"] != username:
        return redirect("/user/" + username + "/mylists")
    username = session["username"]
    userlists.delete_list(db, username, listname)
    return redirect("/user/" + username + "/mylists")

"""Edits a list"""
@app.route("/user/<username>/mylists/<listname>/edit", methods=["POST"])
def edit_list(username, listname):
    if session["username"] != username:
        return redirect("/user/" + username + "/mylists")
    username = session["username"]
    listname = request.form["listname"]
    new_name = request.form["newName"]
    if new_name.strip() == "":
        #TODO
        message = "Can't rename without proper input :("
        return redirect(url_for(".mylists", message=message, username=username))
    userlists.edit_list(db, username, listname, new_name)
    return redirect("/user/" + username + "/mylists")

"""Delete a card in list"""
@app.route("/user/<username>/mylists/<listname>/deletecard", methods=["POST"])
def delete_card(username, listname):
    if session["username"] != username:
        return redirect("/user/" + username + "/mylists/" + listname)

    username = session["username"]
    word = request.form["word"]
    translation = request.form["translation"]
    userlist.remove_card_from_list(db, username, listname, word, translation)
    return redirect("/user/" + username + "/mylists/" + listname)

"""Edit the contents of a card"""
@app.route("/user/<username>/mylists/<listname>/editcard", methods=["POST"])
def edit_card(username, listname):

    if session["username"] != username:
        return redirect("/user/" + username + "/mylists/" + listname)

    word = request.form["word"]
    translation = request.form["translation"]
    new_word = request.form["newWord"]
    new_translation = request.form["newTranslation"]

    if new_word.strip() == "" or new_translation.strip() == "":
        return redirect("/user/" + username + "/mylists/" + listname)


    userlist.edit_card(db, listname, username, word, translation, new_word, new_translation)
    return redirect("/user/" + username + "/mylists/" + listname)

"""Shows flashcard mode"""
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
        cards = userlist.show_cards(db, username, listname)
        length = len(cards)
        return render_template("flashcard.html", cards=cards, length=length, 
        listname=listname)

"""Shows user's profile page. You can follow and unfollow a user here"""
@app.route("/user/<username>/profile", methods=["GET", "POST"])
def profile(username):

    follow_status = database.check_if_following(db, session["username"], username)

    if request.method == "POST":
        if follow_status:
            database.unfollow(db, session["username"], username)
            return redirect("/user/" + username + "/profile")
        else:
            database.follow(db, session["username"], username)
            return redirect("/user/" + username + "/profile")
    else:
        message = ""
        if session["username"] == username:
            message = "Yes, you can follow yourself so your follow list is never empty :)"
        if follow_status:
            follow = "Unfollow"
        else:
            follow = "Follow"
        user_list = userlists.list_lists(db,username)
        if user_list == False:
            return render_template("profile.html", username="User does not exist", 
            lists="", follow=follow)
        return render_template("profile.html", lists=user_list, username=username, follow=follow,
        message=message)

"""Shows list content of a user. Copy functionality"""
@app.route("/user/<username>/profile/<listname>", methods=["GET", "POST"])
def usercardlist(username, listname):

    if request.method == "POST":
        userlists.copy_list(db, session["username"], listname, username)
        return redirect("/user/" + username + "/profile/" + listname)
    else:
        cards = userlist.show_cards(db, username, listname)
        return render_template("userlist.html", username=username, listname=listname,
        cards=cards)

"""Edit profile page and name change"""
@app.route("/user/<username>/profile/edit", methods=["GET", "POST"])
def edit_profile(username):

    if request.method == "POST":
        new_name = request.form("editName")
        if new_name.strip() == "":
            return render_template("editprofile.html", message="Invalid input")
        if len(username) > 16 or len(username) < 3:
            message = "Username too short or too long"
            return render_template("editprofile.html", message=message)
        editprofile.edit_name(db, username, new_name)
        return redirect("/user/" + username + "/profile/edit")
    else:
        return render_template("editprofile.html", message="")

"""Edit your languages"""
@app.route("/user/<username>/profile/edit/lang", methods=["POST"])
def edit_language(username):
    editprofile.edit_language(db)
    return redirect("/user/" + username + "/profile/edit")

"""Shows who you are following"""
@app.route("/user/<username>/following")
def following(username):
    if username != session["username"]:
        redirect("/user/" + session[username] + "/following")
    names = database.show_following(db, session["username"])
    return render_template("following.html", names=names)

"""Shows info/about page"""
@app.route("/info")
def info_about():
    return render_template("infoabout.html")

"""Used to search people"""
@app.route("/search", methods=["POST"])
def search():
    username = request.form["search"]
    if username.strip() == "":
        error = "Can't search without proper input :("
        return render_template("layout.html", error=error)
    error = ""
    return redirect("/user/" + username + "/profile")