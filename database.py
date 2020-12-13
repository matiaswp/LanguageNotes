import app
from flask_sqlalchemy import SQLAlchemy
from flask import render_template
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash
import editprofile

def check_credentials(SQLAlchemy, username, password):

    if check_if_username_exists(SQLAlchemy, username):
        return False
    else:
        return check_if_password_correct(SQLAlchemy, username, password)

def create_account(SQLAlchemy, username, password):

    if check_if_username_exists(SQLAlchemy, username):
        hash_value = generate_password_hash(password)
        sql = "INSERT INTO userinfo (username,password) VALUES (:username,:password)"
        SQLAlchemy.session.execute(sql, {"username":username,"password":hash_value})
        SQLAlchemy.session.commit()
        return True
    return False

def check_if_username_exists(SQLAlchemy, username): 

    get_user_sql = "SELECT username FROM userinfo WHERE username=:username"
    result = SQLAlchemy.session.execute(get_user_sql, {"username":username})
    user = result.fetchone()

    if user == None:
        return True
    else:
        return False

def check_if_password_correct(SQLAlchemy, username, password):

    get_pw_sql = "SELECT password FROM userinfo WHERE username=:username"
    result = SQLAlchemy.session.execute(get_pw_sql, {"username":username})
    pw = result.fetchone()
    correct_pw = pw[0]

    return check_password_hash(correct_pw, password)

def check_if_following(SQLAlchemy, username, following):

    following_sql = "SELECT id FROM userinfo WHERE username=:username"
    get_id = SQLAlchemy.session.execute(following_sql, {"username":following})
    following_id = get_id.fetchone()[0]

    check_sql = "SELECT f.following_userid FROM follow f, userinfo u WHERE u.id=user_id AND "\
    "u.username=:username AND f.following_userid=:following_id"
    get_id = SQLAlchemy.session.execute(check_sql, {"username":username, "following_id":following_id})
    
    try:
        id = get_id.fetchone()[0]
    except:
        return False
    return True

def follow(SQLAlchemy, username, following):
    
    user_id = get_user_id(SQLAlchemy, username)
    following_id = get_user_id(SQLAlchemy, following)

    follow_sql = "INSERT INTO follow (user_id, following_userid) VALUES (:user_id, :following)"
    SQLAlchemy.session.execute(follow_sql, {"user_id":user_id, "following":following_id})
    SQLAlchemy.session.commit()
    return True

def unfollow(SQLAlchemy, username, following):

    following_id = get_user_id(SQLAlchemy, following)

    get_follow_sql = "SELECT f.id FROM follow f, userinfo u WHERE u.id=f.user_id AND "\
    "username=:username AND f.following_userid=:following_id"
    get_id = SQLAlchemy.session.execute(get_follow_sql, {"username":username, 
    "following_id":following_id})
    id = get_id.fetchone()[0]

    unfollow_sql = "DELETE FROM follow WHERE id=:id"
    SQLAlchemy.session.execute(unfollow_sql, {"id":id})
    SQLAlchemy.session.commit()
    return True

def show_following(SQLAlchemy, username):

    user_id = get_user_id(SQLAlchemy, username)

    follow_sql = "SELECT u.username FROM userinfo u, follow f WHERE f.user_id=:user_id AND "\
    "f.following_userid=u.id"
    get_follow = SQLAlchemy.session.execute(follow_sql, {"user_id":user_id})
    following = get_follow.fetchall()

    return following

def get_user_id(SQLAlchemy, username):

    sql = "SELECT id FROM userinfo WHERE username=:username"
    get_id = SQLAlchemy.session.execute(sql, {"username":username})
    user_id = get_id.fetchone()[0]
    return user_id

