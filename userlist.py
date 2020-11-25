import app
from flask_sqlalchemy import SQLAlchemy
from flask import render_template
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash

#Adds card to a given list
def add_card_to_list(SQLAlchemy, username, name, word, translation):

    get_id_sql = "SELECT id FROM userinfo WHERE username=:username"
    get_id = SQLAlchemy.session.execute(get_id_sql, {"username":username})
    user_id = get_id.fetchone()[0]

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
    get_id = SQLAlchemy.session.execute(sql, {"username":username})
    user_id = get_id.fetchone()[0]

    sql2 = "SELECT id FROM lists WHERE user_id=:user_id AND name=:name"
    get_list = SQLAlchemy.session.execute(sql2, {"user_id":user_id, "name":listname})
    list_id = get_list.fetchone()[0]

    sql3 = "DELETE FROM cards WHERE word=:word AND list_id=:list_id "\
         "AND translation=:translation"
    SQLAlchemy.session.execute(sql3, {"word":word, "list_id":list_id, \
        "translation":translation})
    SQLAlchemy.session.commit()

#Edit card
def edit_card(SQLAlchemy, listname, username, word, translation, newWord, newTranslation):
    sql = "SELECT id FROM userinfo WHERE username=:username"
    get_id = SQLAlchemy.session.execute(sql, {"username":username})
    user_id = get_id.fetchone()[0]

    sql2 = "SELECT id FROM lists WHERE user_id=:user_id AND name=:name"
    get_list = SQLAlchemy.session.execute(sql2, {"user_id":user_id, "name":listname})
    list_id = get_list.fetchone()[0]

    sql3 = "UPDATE cards SET word='"+newWord+"', translation='"+newTranslation+\
        "' WHERE list_id='" + str(list_id) + "' AND word='"+word+"' AND translation='"\
            +translation+"'"
    SQLAlchemy.session.execute(sql3)
    SQLAlchemy.session.commit()

#Returns all cards from given list
def show_cards(SQLAlchemy, username, name):

    sql = "SELECT id FROM userinfo WHERE username=:username"
    get_id = SQLAlchemy.session.execute(sql, {"username":username})
    user_id = get_id.fetchone()[0]

    sql2 = "SELECT id FROM lists WHERE user_id=:user_id AND name=:name"
    get_list = SQLAlchemy.session.execute(sql2, {"user_id":user_id, "name":name})
    list_id = get_list.fetchone()[0]

    sql3 = "SELECT word, translation, date FROM cards WHERE list_id=:list_id ORDER BY date"
    get_cards = SQLAlchemy.session.execute(sql3, {"list_id":list_id})
    cards = get_cards.fetchall()

    return cards

#Adds more date to a card. Used by SRS system.
def add_more_date(SQLAlchemy, username, listname, word, translation, answer):
    sql = "SELECT id FROM userinfo WHERE username=:username"
    get_id = SQLAlchemy.session.execute(sql, {"username":username})
    user_id = get_id.fetchone()[0]

    sql2 = "SELECT id FROM lists WHERE user_id=:user_id AND name=:name"
    get_list = SQLAlchemy.session.execute(sql2, {"user_id":user_id, "name":listname})
    list_id = get_list.fetchone()[0]

    sql3 = "SELECT id, difficulty FROM cards WHERE word=:word AND "\
            "translation=:translation AND list_id=:listid"
    get_card = SQLAlchemy.session.execute(sql3, {"word":word, "translation":translation, 
        "list_id":list_id})
    card_id = get_card.fetchone()[0]
    difficulty = get_card.fetchone()[1]

    sql4 = "UPDATE cards SET difficulty=:newDiff, date=NOW()+:date WHERE id=" + card_id
    if answer == "correct":
        if difficulty == 1:
            date = 1
            new_diff = difficulty + 1
        elif difficulty == 2:
            date = 2
            new_diff = difficulty + 1
        elif difficulty == 3:
            date = 5
            new_diff = difficulty + 1
        elif difficulty == 4:
            date = 9
            new_diff = difficulty + 1
        elif difficulty == 5:
            date = 14
            new_diff = difficulty

        
        SQLAlchemy.session.execute(sql4, {"difficulty":new_diff, "date":date})
        SQLAlchemy.session.commit()
    else:
        date = 1
        SQLAlchemy.session.execute(sql4, {"difficulty":1, "date":date})
        SQLAlchemy.session.commit()

