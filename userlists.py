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
    get_id = SQLAlchemy.session.execute(sql, {"username":username})
    user_id = get_id.fetchone()[0]

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

    sql2 = "SELECT name FROM lists WHERE user_id=:user_id AND name=:name"
    get_list = SQLAlchemy.session.execute(sql2, {"user_id":user_id, "name":new_name})
    try:
        get_name = get_list.fetchone()[0]
        if get_name == new_name:
            return False
    except:
        i=0
    
    sql3 = "UPDATE lists SET name='"+new_name+"' WHERE user_id="+str(user_id)+\
        " AND name='"+listname+"'"
    SQLAlchemy.session.execute(sql3)
    SQLAlchemy.session.commit()
    return True

#Copies a list to your own collection
def copy_list(SQLAlchemy, username, listname, list_owner):

    sql = "SELECT id FROM userinfo WHERE username=:username"
    get_id = SQLAlchemy.session.execute(sql, {"username":username})
    user_id = get_id.fetchone()[0]

    sql2 = "SELECT id FROM userinfo WHERE username=:username"
    get_id = SQLAlchemy.session.execute(sql2, {"username":list_owner})
    owner_id = get_id.fetchone()[0]

    sql_list = "SELECT id FROM lists WHERE user_id=:user_id AND name=:name"
    get_list = SQLAlchemy.session.execute(sql_list, {"user_id":owner_id, "name":listname})
    list_id = get_list.fetchone()[0]

    #Create a new list for cards to be copied in and get the list's id
    sql_add_list = "INSERT INTO lists (user_id, name) VALUES (:user_id, :name)"
    name = "Copy of " + listname
    SQLAlchemy.session.execute(sql_add_list, {"user_id":user_id, "name":name})
    """SQLAlchemy.session.commit()"""

    get_new_list = SQLAlchemy.session.execute(sql_list, {"user_id":user_id, "name":name})
    new_listid = get_new_list.fetchone()[0]

    #Copy cards from target list and paste them to the new list
    sql_get_cards = "SELECT word FROM cards WHERE list_id=:listid"
    get_words = SQLAlchemy.session.execute(sql_get_cards, {"listid":list_id})
    words = get_words.fetchall()
    print(words)
    sql_get_translation = "SELECT translation FROM cards WHERE list_id=:listid"
    get_translations = SQLAlchemy.session.execute(sql_get_translation, {"listid":list_id})
    translations = get_translations.fetchall()

    sql3 = "INSERT INTO cards (word, translation, date, list_id, difficulty) VALUES"\
         "(:word, :translation, NOW(), :list_id, 1)"

    for i in range(len(words)):
        word = words[i]
        translation = translations[i]
        SQLAlchemy.session.execute(sql3, {"word":word,"translation":translation,
        "list_id":new_listid})
        i = i + 1
    SQLAlchemy.session.commit()
    return True
    
#For future refactoring
def get_list_id():
    i=0