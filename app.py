from flask import Flask
from flask import redirect, render_template, request, session, url_for
from os import getenv
import database
import userlists
import userlist
import editprofile
from flask_sqlalchemy import SQLAlchemy
import os
from werkzeug.exceptions import abort
from flask.helpers import flash
import flask

app = Flask(__name__)
app.secret_key = getenv("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = getenv("DATABASE_URL")
db = SQLAlchemy(app)

@app.route("/")
def index():
    return render_template("login.html")

@app.route("/login",methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    
    if username.strip() == "" or password.strip() == "":
        message = "Username or password incorrect"
        return render_template("login.html", message=message)        

    if database.check_credentials(db, username, password):
        session["username"] = username
        session["csrf_token"] = os.urandom(16).hex()
        return redirect("/home")
    else:
        message = "Username or password incorrect"
        return render_template("login.html", message=message)
    
@app.route("/logout")
def logout():
    del session["username"]
    return redirect("/")

@app.route("/home")
def home():
    if is_not_logged_in():
        return redirect("/")
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register_page():
    
    if request.method == "POST":
        
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        retyped_password = request.form["retypedPassword"].strip()

        if username == "" or password == "":
            message = "Can't create account with empty credentials"
            return render_template("register.html", message=message)

        if len(username) > 16 or len(username) < 3:
            message = "Username too short or too long"
            return render_template("register.html", message=message)

        if len(password) > 16 or len(password) < 6:
            message = "Password is too short or too long"
            return render_template("register.html", message=message)

        if password == retyped_password:
            if database.create_account(db, username, password):
                return redirect("/")
            else:
                message = "Username taken"
                return render_template("register.html", message=message)
        else:
            message = "Passwords didn't match"
            return render_template("register.html", message=message)
    else:
        message = ""
        return render_template("register.html", message=message)

@app.route("/user/<username>/mylists", methods=["GET", "POST"])    
def mylists(username):

    if is_not_logged_in():
        return redirect("/")

    if username != session["username"]:
        return redirect("/user/" + session["username"] + "/mylists")

    if request.method == "POST":
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)

        username = session["username"]
        name = request.form["listname"].strip()

        if name == "" or len(name) > 25:
            flash("Invalid listname. Empty or too long", category="error")
            return redirect("/user/" + session["username"] + "/mylists")
        
        if userlists.create_new_list(db, username, name):
            flash("List added successfully", category="message")
            return redirect("/user/" + session["username"] + "/mylists")
        else:
            flash("Listname already in use.", category="error")
            return redirect("/user/" + session["username"] + "/mylists")
    else:
        user_list = userlists.list_lists(db,username)
        return render_template("mylists.html", lists=user_list)
                  
@app.route("/user/<username>/mylists/<listname>", methods=["POST", "GET"])
def show_list(username, listname):

    if is_not_logged_in():
        return redirect("/")

    username = session["username"]

    if request.method == "POST":

        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)

        word = request.form["word"].strip()
        translation = request.form["translation"].strip()

        if word == "" or translation == "":
            flash("Can't create a card with empty values", category="error")
            return redirect("/user/" + username + "/mylists/" + listname)
        if len(word) > 50 or len(translation) > 50:
            flash("Given values are too long. The limit is 100.", category="error")
            return redirect("/user/" + username + "/mylists/" + listname)

        userlist.add_card_to_list(db,username, listname, word, translation)
        flash("Card added successfully", category="message")
        return redirect("/user/" + username + "/mylists/" + listname)
    else:
        username = session["username"]
        cards = userlist.show_cards(db, username, listname)
        return render_template("mylist.html", listname=listname, cards=cards)

@app.route("/user/<username>/mylists/<listname>/delete", methods=["POST"])
def delete_list(username, listname):

    if is_not_logged_in():
        return redirect("/")

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    if session["username"] != username:
        return redirect("/user/" + username + "/mylists")

    username = session["username"]
    userlists.delete_list(db, username, listname)
    flash("List deleted successfully", category="message")
    return redirect("/user/" + username + "/mylists")

@app.route("/user/<username>/mylists/<listname>/edit", methods=["POST"])
def edit_list(username, listname):
    if is_not_logged_in():
        return redirect("/")

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    if session["username"] != username:
        return redirect("/user/" + username + "/mylists")

    user_list = userlists.list_lists(db,username)
    username = session["username"]
    listname = request.form["listname"]
    new_name = request.form["newName"].strip()

    if new_name == "" or len(new_name) > 25:
        flash("Invalid listname. Empty or too long", category="error")
        return redirect("/user/" + username + "/mylists")

    if userlists.edit_list(db, username, listname, new_name):
        flash("Edited listname succesfully", category="message")
        return redirect("/user/" + username + "/mylists")
    else:
        flash("Listname already in use.", category="error")
        return redirect("/user/" + username + "/mylists")

@app.route("/user/<username>/mylists/<listname>/deletecard", methods=["POST"])
def delete_card(username, listname):
    if is_not_logged_in():
        return redirect("/")

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    if session["username"] != username:
        return redirect("/user/" + username + "/mylists/" + listname)

    username = session["username"]
    word = request.form["word"]
    translation = request.form["translation"]
    userlist.remove_card_from_list(db, username, listname, word, translation)
    flash("Card deleted successfully", category="message")
    return redirect("/user/" + username + "/mylists/" + listname)

@app.route("/user/<username>/mylists/<listname>/editcard", methods=["POST"])
def edit_card(username, listname):

    if is_not_logged_in():
        return redirect("/")

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    if session["username"] != username:
        return redirect("/user/" + username + "/mylists/" + listname)

    word = request.form["word"].strip()
    translation = request.form["translation"].strip()
    new_word = request.form["newWord"].strip()
    new_translation = request.form["newTranslation"].strip()

    if new_word == "" or new_translation == "":
        flash("Can't rename cards with empty values", category="error")
        return redirect("/user/" + username + "/mylists/" + listname)

    if len(new_word) > 100 or len(new_translation) > 100:
        flash("Given values are too long. The limit is 100.", category="error")
        return redirect("/user/" + username + "/mylists/" + listname)

    userlist.edit_card(db, listname, username, word, translation, new_word, new_translation)
    flash("Card edited succesfully", category="message")
    return redirect("/user/" + username + "/mylists/" + listname)

@app.route("/user/<username>/mylists/<listname>/study", methods=["GET", "POST"])
def flashcard(username, listname):

    if is_not_logged_in():
        return redirect("/")

    if request.method == "POST":

        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)

        word = request.form["word"]
        translation = request.form["translation"]

        if request.form["flip"] == "Got it!":
            userlist.add_more_date(db, username, listname, word, translation, "correct")
        else:
            userlist.add_more_date(db, username, listname, word, translation, "wrong")

        return redirect("/user/" + username + "/mylists/" + listname + "/study")
    else:
        username = session["username"]
        cards = userlist.show_study_cards(db, username, listname)
        length = len(cards)

        if length == 0:
            flash("No more studying for today!", category="allDone")
            return redirect("/user/" + username + "/mylists/" + listname)

        return render_template("flashcard.html", cards=cards, length=length, 
        listname=listname)

"""Shows user's profile page. You can follow and unfollow a user here"""
@app.route("/user/<username>/profile", methods=["GET", "POST"])
def profile(username):

    if is_not_logged_in():
        return redirect("/")

    follow_status = database.check_if_following(db, session["username"], username)

    if request.method == "POST":

        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)

        if follow_status:
            database.unfollow(db, session["username"], username)
            flash("Unfollowed succesfully", category="message")
            return redirect("/user/" + username + "/profile")
        else:
            database.follow(db, session["username"], username)
            flash("Followed successfully", category="message")
            return redirect("/user/" + username + "/profile")
    else:
        message = ""
        if session["username"] == username:
            message = "Yes, you can follow yourself..."
        if follow_status:
            follow = "Unfollow"
        else:
            follow = "Follow"
        user_list = userlists.list_lists(db,username)
        if user_list == False:
            return render_template("profile.html", username="User does not exist", 
            lists="", follow="")
        languages = editprofile.get_languages(db, username)
        return render_template("profile.html", lists=user_list, username=username, follow=follow,
        message=message, languages=languages)

@app.route("/user/<username>/profile/<listname>")
def user_card_list(username, listname):

    if is_not_logged_in():
        return redirect("/")

    if username == session["username"]:
        return redirect("/user/" + session["username"] + "/mylists/" + listname)

    cards = userlist.show_cards(db, username, listname)
    return render_template("userlist.html", username=username, listname=listname,
    cards=cards)

@app.route("/user/<username>/profile/edit", methods=["GET", "POST"])
def edit_profile(username):
    if is_not_logged_in():
        return redirect("/")
    
    if request.method == "POST":
        if session["csrf_token"] != request.form["csrf_token"]:
            abort(403)

        new_lang = request.form["lang1"].strip()
        old_lang = request.form["lang"]

        if new_lang == "" or len(new_lang) > 25:
            flash("Invalid language. Empty or too long.", category="error")
            return redirect("/user/" + username + "/profile/edit")

        """Method returns true if already learning given language"""
        if editprofile.check_if_learning(db, username, new_lang):
            flash("Already learning that language.", category="error")
            return redirect("/user/" + username + "/profile/edit")

        editprofile.edit_language(db, username, new_lang, old_lang)
        flash("Language edited successfully.", category="message")
        return redirect("/user/" + username + "/profile/edit")
    else:
        if username != session["username"]:
            return redirect("/user/" + session["username"] + "/profile/edit")
        languages = editprofile.get_languages(db, session["username"])
        return render_template("editprofile.html", message="", languages=languages)

@app.route("/user/<username>/profile/edit/add", methods=["POST"])
def edit_add_lang(username):
    if is_not_logged_in():
        return redirect("/")

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    if username != session["username"]:
        return redirect("/user/" + session["username"] + "/profile/edit")

    languages = editprofile.get_languages(db, session["username"])
    language = request.form["lang"].strip()
    if language == "" or len(language) > 25:
        flash("Invalid language. Empty or too long.", category="error")
        return redirect("/user/" + session["username"] + "/profile/edit")

    if len(languages) >= 3:
        flash("Already learning max amount of languages.", category="error")
        return redirect("/user/" + session["username"] + "/profile/edit")

    """Method returns true if already learning given language"""
    if editprofile.check_if_learning(db, username, language):
        flash("Already learning that language.", category="error")
        return redirect("/user/" + session["username"] + "/profile/edit")

    user_id = database.get_user_id(db, username)
    editprofile.add_language(db, user_id,  language)
    flash("Language added successfully.", category="message")
    return redirect("/user/" + session["username"] + "/profile/edit")

@app.route("/user/<username>/profile/edit/delete", methods=["POST"])
def edit_delete_lang(username):

    if is_not_logged_in():
        return redirect("/")

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    if username != session["username"]:
        return redirect("/user/" + session["username"] + "/profile/edit")

    language = request.form["language"]
    editprofile.delete_language(db, username, language)
    flash("Language deleted successfully.", category="message")
    return redirect("/user/" + session["username"] + "/profile/edit")

@app.route("/user/<username>/following")
def following(username):

    if is_not_logged_in():
        return redirect("/")

    if username != session["username"]:
        return redirect("/user/" + session["username"] + "/following")

    names = database.show_following(db, session["username"])
    return render_template("following.html", names=names)

@app.route("/info")
def info_about():

    if is_not_logged_in():
        return redirect("/")

    return render_template("infoabout.html")

@app.route("/search", methods=["POST"])
def search():

    if is_not_logged_in():
        return redirect("/")

    if session["csrf_token"] != request.form["csrf_token"]:
        abort(403)

    username = request.form["search"].strip()
    if username == "":
        flash("No input!", category="searchError")
        return redirect(request.referrer)

    if database.check_if_username_exists(db,username):
        flash("User does not exist.", category="searchError")
        return redirect(request.referrer)
        
    return redirect("/user/" + username + "/profile")

def is_not_logged_in():
    try:
        session["username"].strip()
    except:
        return True