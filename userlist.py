import app
from flask_sqlalchemy import SQLAlchemy
from flask import render_template
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash

#Adds card to a given list
def addCardToList(SQLAlchemy, username, name, word, translation):

    sql = "SELECT id FROM userinfo WHERE username=:username"
    getId = SQLAlchemy.session.execute(sql, {"username":username})
    user_id = getId.fetchone()[0]

    get_list_sql = "SELECT l.id FROM lists l, userinfo u WHERE l.user_id=u.id AND name=:name AND"\
        " u.username=:username"
    get_list = SQLAlchemy.session.execute(get_list_sql, {"username":username,"name":name})
    list_id = get_list.fetchone()[0]

    sql3 = "INSERT INTO cards (word, translation, date, list_id, difficulty) VALUES"\
         "(:word, :translation, NOW(), :list_id, 1)"
    SQLAlchemy.session.execute(sql3, {"word":word,"translation":translation,"list_id":list_id})
    SQLAlchemy.session.commit()

#Removes a card from list
def remove_card_from_list(SQLAlchemy, username, listname, word, translation):
    sql = "SELECT id FROM userinfo WHERE username=:username"
    getId = SQLAlchemy.session.execute(sql, {"username":username})
    user_id = getId.fetchone()[0]

    sql2 = "SELECT id FROM lists WHERE user_id=:user_id AND name=:name"
    getList = SQLAlchemy.session.execute(sql2, {"user_id":user_id, "name":listname})
    list_id = getList.fetchone()[0]

    sql3 = "DELETE FROM cards WHERE word=:word AND list_id=:list_id "\
         "AND translation=:translation"
    SQLAlchemy.session.execute(sql3, {"word":word, "list_id":list_id, \
        "translation":translation})
    SQLAlchemy.session.commit()

#Edit card
def editCard(SQLAlchemy, listname, username, word, translation, newWord, newTranslation):
    sql = "SELECT id FROM userinfo WHERE username=:username"
    getId = SQLAlchemy.session.execute(sql, {"username":username})
    user_id = getId.fetchone()[0]

    sql2 = "SELECT id FROM lists WHERE user_id=:user_id AND name=:name"
    getList = SQLAlchemy.session.execute(sql2, {"user_id":user_id, "name":listname})
    list_id = getList.fetchone()[0]

    sql3 = "UPDATE cards SET word='"+newWord+"', translation='"+newTranslation+\
        "' WHERE list_id='"+str(list_id)+"' AND word='"+word+"' AND translation='"\
            +translation+"'"
    SQLAlchemy.session.execute(sql3)
    SQLAlchemy.session.commit()


#Returns all cards from given list
def showCards(SQLAlchemy, username, name):
    sql = "SELECT id FROM userinfo WHERE username=:username"
    getId = SQLAlchemy.session.execute(sql, {"username":username})
    user_id = getId.fetchone()[0]

    sql2 = "SELECT id FROM lists WHERE user_id=:user_id AND name=:name"
    getList = SQLAlchemy.session.execute(sql2, {"user_id":user_id, "name":name})
    list_id = getList.fetchone()[0]

    sql3 = "SELECT word, translation, date FROM cards WHERE list_id=:list_id ORDER BY date"
    getCards = SQLAlchemy.session.execute(sql3, {"list_id":list_id})
    cards = getCards.fetchall()

    return cards