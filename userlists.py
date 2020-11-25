import app
from flask_sqlalchemy import SQLAlchemy
from flask import render_template
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash

#Lists all lists of a user
def list_lists(SQLAlchemy, username):
    
    sql = "SELECT name FROM lists WHERE user_id=:user_id"
    sql2 = "SELECT id FROM userinfo WHERE username=:username"

    get_id = SQLAlchemy.session.execute(sql2, {"username":username})
    try:
        user_id = get_id.fetchone()[0]
    except:
        return False

    get_lists = SQLAlchemy.session.execute(sql, {"user_id":user_id})
    lists = get_lists.fetchall()
    
    return lists

#Creates a new list
def create_new_list(SQLAlchemy, username, listname):

    sql = "SELECT id FROM userinfo WHERE username=:username"
    getId = SQLAlchemy.session.execute(sql, {"username":username})
    user_id = getId.fetchone()[0]

    ql = "SELECT id FROM lists WHERE user_id=:user_id AND name=:listname"
    get_lists = SQLAlchemy.session.execute(ql, {"user_id":user_id, "listname":listname})

    try:
        get_list = get_lists.fetchone()[0]
    except:
        sql2 = "INSERT INTO lists (user_id, name) VALUES (:user_id, :name)"
        SQLAlchemy.session.execute(sql2, {"user_id":user_id, "name":listname})
        SQLAlchemy.session.commit()
        return True
    return False

#Deletes the list and all the cards in it
def delete_list(SQLAlchemy, username, listname):
    sql = "SELECT id FROM userinfo WHERE username=:username"
    get_id = SQLAlchemy.session.execute(sql, {"username":username})
    user_id = get_id.fetchone()[0]

    sql2 = "SELECT id FROM lists WHERE user_id=:user_id AND name=:name"
    get_list = SQLAlchemy.session.execute(sql2, {"user_id":user_id, "name":listname})
    list_id = get_list.fetchone()[0]

    sql3 = "DELETE FROM cards WHERE list_id=:list_id"
    SQLAlchemy.session.execute(sql3, {"list_id":list_id})
    SQLAlchemy.session.commit()

    sql3 = "DELETE FROM lists WHERE name=:name AND user_id=:user_id"
    SQLAlchemy.session.execute(sql3, {"user_id":user_id, "name":listname})
    SQLAlchemy.session.commit()

#Edit lists name
def edit_list(SQLAlchemy, username, listname, new_name):
    sql = "SELECT id FROM userinfo WHERE username=:username"
    get_id = SQLAlchemy.session.execute(sql, {"username":username})
    user_id = get_id.fetchone()[0]

    sql2 = "SELECT id FROM lists WHERE user_id=:user_id AND name=:name"
    get_list = SQLAlchemy.session.execute(sql2, {"user_id":user_id, "name":listname})
    list_id = get_list.fetchone()[0]

    sql3 = "UPDATE lists SET name='"+new_name+"' WHERE user_id="+str(user_id)+\
        " AND name='"+listname+"'"
    SQLAlchemy.session.execute(sql3)
    SQLAlchemy.session.commit()

#For future refactoring
def get_user_id():
    i=0

#For future refactoring
def get_list_id():
    i=0