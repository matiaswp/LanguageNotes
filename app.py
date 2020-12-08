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

@app.route("/")
def index():
    return render_template("login.html")

@app.route("/login",methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]
    
    if database.check_credentials(db, username, password) == True:
        session["username"] = username
        session["logged_in"] = True
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
    try:
        session["username"].strip()
    except:
        return redirect("/")
    return render_template("home.html")

@app.route("/register", methods=["GET", "POST"])
def register_page():
    message = ""
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

@app.route("/user/<username>/mylists", methods=["GET", "POST"])    
def mylists(username):
    try:
        session["username"].strip()
    except:
        return redirect("/")
    try:
        message = request.args("message")
    except:
        message = ""
    if request.method == "POST":
    
        if session["username"] != username:
            return redirect("/user/" + session["username"] + "/mylists")

        username = session["username"]
        name = request.form["listname"].strip()

        #If name empty, redirect same page. TODO add error message.
        if name == "" or len(name) > 25:
            return redirect("/user/" + session["username"] + "/mylists")

        userlists.create_new_list(db, username, name)
        return redirect("/user/" + username + "/mylists")
    else:
        if session["username"] == username:
            user_list = userlists.list_lists(db,username)
            return render_template("mylists.html", lists=user_list, message=message)
        else:
            return redirect("/user/" + session["username"] + "/mylists")
        
@app.route("/user/<username>/mylists/<listname>", methods=["POST", "GET"])
def show_list(username, listname):
    try:
        session["username"].strip()
    except:
        return redirect("/")
    username = session["username"]
    cards = userlist.show_cards(db, username, listname)

    if request.method == "POST":
        word = request.form["word"].strip()
        translation = request.form["translation"].strip()

        if word == "" or translation == "":
            message = "Can't create a card with empty values"
            return render_template("mylist.html", listname=listname, cards=cards, 
            message=message)
        if len(word) > 50 or len(translation) > 50:
            message = "Values are too long"
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

@app.route("/user/<username>/mylists/<listname>/delete", methods=["POST"])
def delete_list(username, listname):
    try:
        session["username"].strip()
    except:
        return redirect("/")

    if session["username"] != username:
        return redirect("/user/" + username + "/mylists")

    username = session["username"]
    userlists.delete_list(db, username, listname)
    return redirect("/user/" + username + "/mylists")

@app.route("/user/<username>/mylists/<listname>/edit", methods=["POST"])
def edit_list(username, listname):
    try:
        session["username"].strip()
    except:
        return redirect("/")

    if session["username"] != username:
        return redirect("/user/" + username + "/mylists")
    username = session["username"]
    listname = request.form["listname"].strip()
    new_name = request.form["newName"].strip()
    if new_name == "" or len(new_name) > 25:
        #TODO
        message = "Invalid name"
        return redirect(url_for(".mylists", message=message, username=username))
    userlists.edit_list(db, username, listname, new_name)
    return redirect("/user/" + username + "/mylists")

@app.route("/user/<username>/mylists/<listname>/deletecard", methods=["POST"])
def delete_card(username, listname):
    try:
        session["username"].strip()
    except:
        return redirect("/")

    if session["username"] != username:
        return redirect("/user/" + username + "/mylists/" + listname)

    username = session["username"]
    word = request.form["word"]
    translation = request.form["translation"]
    userlist.remove_card_from_list(db, username, listname, word, translation)
    return redirect("/user/" + username + "/mylists/" + listname)

@app.route("/user/<username>/mylists/<listname>/editcard", methods=["POST"])
def edit_card(username, listname):
    try:
        session["username"].strip()
    except:
        return redirect("/")

    if session["username"] != username:
        return redirect("/user/" + username + "/mylists/" + listname)

    word = request.form["word"].strip()
    translation = request.form["translation"].strip()
    new_word = request.form["newWord"].strip()
    new_translation = request.form["newTranslation"].strip()

    if new_word == "" or new_translation == "":
        return redirect("/user/" + username + "/mylists/" + listname)

    if len(new_word) > 50 or len(new_translation) > 50:
        return redirect("/user/" + username + "/mylists/" + listname)

    userlist.edit_card(db, listname, username, word, translation, new_word, new_translation)
    return redirect("/user/" + username + "/mylists/" + listname)

@app.route("/user/<username>/mylists/<listname>/study", methods=["GET", "POST"])
def flashcard(username, listname):
    try:
        session["username"].strip()
    except:
        return redirect("/")

    username = session["username"]
    cards = userlist.show_study_cards(db, username, listname)
    length = len(cards)
    if request.method == "POST":
        word = request.form["word"]
        translation = request.form["translation"]

        if request.form["flip"] == "Got it!":
            userlist.add_more_date(db, username, listname, word, translation, "correct")
        else:
            userlist.add_more_date(db, username, listname, word, translation, "wrong")

        return render_template("flashcard.html", cards=cards, length=length, 
        listname=listname)
    else:
        return render_template("flashcard.html", cards=cards, length=length, 
        listname=listname)

"""Shows user's profile page. You can follow and unfollow a user here"""
@app.route("/user/<username>/profile", methods=["GET", "POST"])
def profile(username):
    try:
        session["username"].strip()
    except:
        return redirect("/")

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
            lists="", follow="")
        languages = editprofile.get_languages(db, username)
        return render_template("profile.html", lists=user_list, username=username, follow=follow,
        message=message, languages=languages)

@app.route("/user/<username>/profile/<listname>")
def usercardlist(username, listname):
    try:
        session["username"].strip()
    except:
        return redirect("/")

    cards = userlist.show_cards(db, username, listname)
    return render_template("userlist.html", username=username, listname=listname,
    cards=cards)

@app.route("/user/<username>/profile/edit", methods=["GET", "POST"])
def edit_profile(username):
    try:
        session["username"].strip()
    except:
        return redirect("/")
    
    if request.method == "POST":

        new_lang = request.form["lang1"].strip()
        old_lang = request.form["lang"]

        if new_lang == "" or len(new_lang) > 25:
            return redirect("/user/" + username + "/profile/edit")
            
        if editprofile.check_if_learning(db, username, new_lang):
            return redirect("/user/" + username + "/profile/edit")

        editprofile.edit_language(db, username, new_lang, old_lang)
        return redirect("/user/" + username + "/profile/edit")
    else:
        if username != session["username"]:
            return redirect("/user/" + session["username"] + "/profile/edit")
        languages = editprofile.get_languages(db, session["username"])
        return render_template("editprofile.html", message="", languages=languages)

@app.route("/user/<username>/profile/edit/add", methods=["POST"])
def edit_add_lang(username):
    try:
        session["username"].strip()
    except:
        return redirect("/")

    if username != session["username"]:
        return redirect("/user/" + session["username"] + "/profile/edit")

    languages = editprofile.get_languages(db, session["username"])
    language = request.form["lang"].strip()
    if language == "" or len(language) > 25:
        return redirect("/user/" + session["username"] + "/profile/edit")

    if len(languages) >= 3:
        return redirect("/user/" + session["username"] + "/profile/edit")

    if editprofile.check_if_learning(db, username, language):
        return redirect("/user/" + session["username"] + "/profile/edit")

    user_id = database.get_user_id(db, username)
    editprofile.add_language(db, user_id,  language)
    return redirect("/user/" + session["username"] + "/profile/edit")

@app.route("/user/<username>/following")
def following(username):
    try:
        session["username"].strip()
    except:
        return redirect("/")

    if username != session["username"]:
        return redirect("/user/" + session["username"] + "/following")
    names = database.show_following(db, session["username"])
    return render_template("following.html", names=names)

@app.route("/info")
def info_about():
    try:
        session["username"].strip()
    except:
        return redirect("/")

    return render_template("infoabout.html")

@app.route("/search", methods=["POST"])
def search():
    try:
        session["username"].strip()
    except:
        return redirect("/")

    username = request.form["search"].strip()

    if username == "":
        error = "Can't search without proper input :("
        return render_template("layout.html", error=error)
    error = ""
    return redirect("/user/" + username + "/profile")