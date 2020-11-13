import app
from flask_sqlalchemy import SQLAlchemy
from flask import render_template
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash


def listLists(SQLAlchemy, username):
    
    sql = "SELECT name FROM lists WHERE userid=:userId"
    sql2 = "SELECT id FROM userinfo WHERE username=:username"
    getId = SQLAlchemy.session.execute(sql2, {"username":username})
    userId = getId.fetchone()[0]
    getLists = SQLAlchemy.session.execute(sql, {"userId":userId})
    lists = getLists.fetchall()
    return lists

def createNewList(SQLAlchemy, username, name):

    sql = "SELECT id FROM userinfo WHERE username=:username"
    getId = SQLAlchemy.session.execute(sql, {"username":username})
    userId = getId.fetchone()[0]

    ql = "SELECT name FROM lists WHERE userid=:userid"
    getLists = SQLAlchemy.session.execute(ql, {"userid":userId})
    lists = getLists.fetchall()

    if name in lists:
        return
    sql2 = "INSERT INTO lists (userid, name) VALUES (:userid, :name)"
    SQLAlchemy.session.execute(sql2, {"userid":userId, "name":name})
    SQLAlchemy.session.commit()
    return True