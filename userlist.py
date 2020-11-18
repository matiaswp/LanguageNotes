import app
from flask_sqlalchemy import SQLAlchemy
from flask import render_template
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash

#Adds card to a given list
def addCardToList(SQLAlchemy, username, name, word, translation):
    sql = "SELECT id FROM userinfo WHERE username=:username"
    getId = SQLAlchemy.session.execute(sql, {"username":username})
    userId = getId.fetchone()[0]

    sql2 = "SELECT id FROM lists WHERE userid=:userid AND name=:name"
    getList = SQLAlchemy.session.execute(sql2, {"userid":userId, "name":name})
    listId = getList.fetchone()[0]

    sql3 = "INSERT INTO cards (word, translation, date, listid) VALUES"\
         "(:word, :translation, NOW(), :listid)"
    SQLAlchemy.session.execute(sql3, {"word":word,"translation":translation,"listid":listId})
    SQLAlchemy.session.commit()

#Removes a card from list
def remove_card_from_list(SQLAlchemy, username, listname, word, translation):
    sql = "SELECT id FROM userinfo WHERE username=:username"
    getId = SQLAlchemy.session.execute(sql, {"username":username})
    userId = getId.fetchone()[0]

    sql2 = "SELECT id FROM lists WHERE userid=:userid AND name=:name"
    getList = SQLAlchemy.session.execute(sql2, {"userid":userId, "name":listname})
    listid = getList.fetchone()[0]

    sql3 = "DELETE FROM cards WHERE word=:word AND listid=:listid "\
         "AND translation=:translation"
    SQLAlchemy.session.execute(sql3, {"word":word, "listid":listid, \
        "translation":translation})
    SQLAlchemy.session.commit()

#Edit card
def editCard(SQLAlchemy, listname, word, translation, newWord, newTranslation):
    
    sql3 = "UPDATE cards SET word='"+newWord+"', translation='"+newTranslation+\
        "' WHERE listid='"+str(listname)+"' AND word='"+word+"' AND translation='"\
            +translation+"'"
    SQLAlchemy.session.execute(sql3)
    SQLAlchemy.session.commit()


#Returns all cards from given list
def showCards(SQLAlchemy, username, name):
    sql = "SELECT id FROM userinfo WHERE username=:username"
    getId = SQLAlchemy.session.execute(sql, {"username":username})
    userId = getId.fetchone()[0]

    sql2 = "SELECT id FROM lists WHERE userid=:userid AND name=:name"
    getList = SQLAlchemy.session.execute(sql2, {"userid":userId, "name":name})
    listId = getList.fetchone()[0]

    sql3 = "SELECT word, translation, date FROM cards WHERE listid=:listid"
    getCards = SQLAlchemy.session.execute(sql3, {"listid":listId})
    cards = getCards.fetchall()

    return cards