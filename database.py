import app
from flask_sqlalchemy import SQLAlchemy
from flask import render_template
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash

#Lists all usernames (temporary, for testing pusposes only)
def users(SQLAlchemy):
    result = SQLAlchemy.session.execute("SELECT username FROM userinfo")
    content = result.fetchall()
    return content

#Checks if the username and password are valid
def check_credentials(SQLAlchemy, username, password):

    #Returns false if username doesn't exist
    if check_if_username_exists(SQLAlchemy, username) == False:
        return False
    #Checks if the password is correct for given account
    else:
        if check_if_password_correct(SQLAlchemy, username, password) == True:
            return True
        else: 
            return False

#Creates you a cool account
def create_account(SQLAlchemy, username, password):

    #TODO minimum and maximum lenght for username and password

    #If username doesn't exist, create user and return true
    if check_if_username_exists(SQLAlchemy, username) == False:
        hash_value = generate_password_hash(password)
        sql = "INSERT INTO userinfo (username,password) VALUES (:username,:password)"
        SQLAlchemy.session.execute(sql, {"username":username,"password":hash_value})
        SQLAlchemy.session.commit()
        return True
    #Return false if username already exists
    else:
        return False

#Checks if the given username exists in the database
def check_if_username_exists(SQLAlchemy, username): 

    #Tries to find given username from database
    sql = "SELECT username FROM userinfo WHERE username=:username"
    result = SQLAlchemy.session.execute(sql, {"username":username})
    user = result.fetchone()

    #Returs false if username doesn't exist and otherwise true
    if user == None:
        return False
    else:
        return True

#Checks if given password is correct
def check_if_password_correct(SQLAlchemy, username, password):

    typedPassword = generate_password_hash(password)
    
    #Fetches the password for the given account
    sql = "SELECT password FROM userinfo WHERE username=:username"
    result = SQLAlchemy.session.execute(sql, {"username":username})
    pw = result.fetchone()
    correctPassword = pw[0]

    #Checks if the passwords match. Returns true if matches, otherwise return false
    if check_password_hash(correctPassword,password):
        return True
    else:
        return False

#Checks if user is following other user
def check_if_following(SQLAlchemy, username, following):
    user_sql = "SELECT id FROM userinfo WHERE username=:username"
    get_id = SQLAlchemy.session.execute(user_sql, {"username":username})
    user_id = get_id.fetchone()[0]
    
    try:
        following_sql = "SELECT id FROM userinfo WHERE username=:username"
        get_id = SQLAlchemy.session.execute(following_sql, {"username":following})
        following_id = get_id.fetchone()[0]
    except:
        return False
    check_sql = "SELECT id FROM follow WHERE user_id=:user_id AND "\
    "following_userid=:following_id"
    get_id = SQLAlchemy.session.execute(check_sql, {"user_id":user_id, "following_id":following_id})
    
    try:
        id = get_id.fetchone()[0]
    except:
        return False
    return True
    
#Follows a user
def follow(SQLAlchemy, username, following):
    user_sql = "SELECT id FROM userinfo WHERE username=:username"
    get_id = SQLAlchemy.session.execute(user_sql, {"username":username})
    user_id = get_id.fetchone()[0]

    following_sql = "SELECT id FROM userinfo WHERE username=:username"
    get_id = SQLAlchemy.session.execute(following_sql, {"username":following})
    following_id = get_id.fetchone()[0]

    follow_sql = "INSERT INTO follow (user_id, following_userid) VALUES (:user_id, :following)"
    SQLAlchemy.session.execute(follow_sql, {"user_id":user_id, "following":following_id})
    SQLAlchemy.session.commit()
    return True

#Unfollows a user
def unfollow(SQLAlchemy, username, following):
    user_sql = "SELECT id FROM userinfo WHERE username=:username"
    get_id = SQLAlchemy.session.execute(user_sql, {"username":username})
    user_id = get_id.fetchone()[0]

    following_sql = "SELECT id FROM userinfo WHERE username=:username"
    get_id = SQLAlchemy.session.execute(following_sql, {"username":following})
    following_id = get_id.fetchone()[0]

    check_sql = "SELECT id FROM follow WHERE user_id=:user_id AND "\
    "following_userid=:following_id" 
    get_id = SQLAlchemy.session.execute(check_sql, {"user_id":user_id, 
    "following_id":following_id})
    id = get_id.fetchone()[0]

    unfollow_sql = "DELETE FROM follow WHERE id=:id"
    SQLAlchemy.session.execute(unfollow_sql, {"id":id})
    SQLAlchemy.session.commit()
    return True

def show_following(SQLAlchemy, username):
    user_sql = "SELECT id FROM userinfo WHERE username=:username"
    get_id = SQLAlchemy.session.execute(user_sql, {"username":username})
    user_id = get_id.fetchone()[0]

    follow_sql = "SELECT u.username FROM userinfo u, follow f WHERE f.user_id=:user_id AND "\
    "f.following_userid=u.id"
    get_follow = SQLAlchemy.session.execute(follow_sql, {"user_id":user_id})
    following = get_follow.fetchall()

    return following
