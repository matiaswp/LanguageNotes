import app
from flask_sqlalchemy import SQLAlchemy
from flask import render_template
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash

#Lists all lists of a user
def listLists(SQLAlchemy, username):
    
    sql = "SELECT name FROM lists WHERE userid=:userId"
    sql2 = "SELECT id FROM userinfo WHERE username=:username"
    getId = SQLAlchemy.session.execute(sql2, {"username":username})
    userId = getId.fetchone()[0]
    getLists = SQLAlchemy.session.execute(sql, {"userId":userId})
    lists = getLists.fetchall()
    return lists

#Creates a new list
def createNewList(SQLAlchemy, username, listname):

    sql = "SELECT id FROM userinfo WHERE username=:username"
    getId = SQLAlchemy.session.execute(sql, {"username":username})
    userId = getId.fetchone()[0]

    ql = "SELECT name FROM lists WHERE userid=:userid"
    getLists = SQLAlchemy.session.execute(ql, {"userid":userId})
    lists = getLists.fetchall()

    if listname in lists:
        return
    sql2 = "INSERT INTO lists (userid, name) VALUES (:userid, :name)"
    SQLAlchemy.session.execute(sql2, {"userid":userId, "name":listname})
    SQLAlchemy.session.commit()
    return True

#Deletes the list and all the cards in it
def deleteList(SQLAlchemy, username, listname):
    sql = "SELECT id FROM userinfo WHERE username=:username"
    getId = SQLAlchemy.session.execute(sql, {"username":username})
    userId = getId.fetchone()[0]

    sql2 = "SELECT id FROM lists WHERE userid=:userid AND name=:name"
    getList = SQLAlchemy.session.execute(sql2, {"userid":userId, "name":listname})
    listId = getList.fetchone()[0]

    sql3 = "DELETE FROM cards WHERE listid=:listid"
    SQLAlchemy.session.execute(sql3, {"listid":listId})
    SQLAlchemy.session.commit()

    sql3 = "DELETE FROM lists WHERE name=:name AND userid=:userid"
    SQLAlchemy.session.execute(sql3, {"userid":userId, "name":listname})
    SQLAlchemy.session.commit()

#Edit lists name
def editList(SQLAlchemy, username, listname, newName):
    sql = "SELECT id FROM userinfo WHERE username=:username"
    getId = SQLAlchemy.session.execute(sql, {"username":username})
    userId = getId.fetchone()[0]

    sql2 = "SELECT id FROM lists WHERE userid=:userid AND name=:name"
    getList = SQLAlchemy.session.execute(sql2, {"userid":userId, "name":listname})
    listId = getList.fetchone()[0]

    sql3 = "UPDATE lists SET name='"+newName+"' WHERE userid="+str(userId)+\
        " AND name='"+listname+"'"
    SQLAlchemy.session.execute(sql3)
    SQLAlchemy.session.commit()

#For future refactoring
def getUserid():
    i=0

#For future refactoring
def getListid():
    i=0