from flask import Flask
from flask import redirect, render_template, request, session
import app
from flask_sqlalchemy import SQLAlchemy
import database

def add_language(SQLAlchemy, user_id, language):

    add_sql = "INSERT INTO languages (language, user_id) VALUES (:lang, :user_id)"
    SQLAlchemy.session.execute(add_sql, {"lang":language, "user_id":user_id})
    SQLAlchemy.session.commit()

    return True

def edit_language(SQLAlchemy, username, language, new_language):
    user_id = database.get_user_id(SQLAlchemy, username)
    add_sql = "UPDATE languages SET language=:language WHERE user_id=:user_id"\
    " AND language=:new_language"
    SQLAlchemy.session.execute(add_sql, {"language":language, "user_id":user_id, 
    "new_language":new_language})
    SQLAlchemy.session.commit()

    return True

def delete_language(SQLAlchemy, username, language):
    
    user_id = database.get_user_id(SQLAlchemy, username)
    delete_sql = "DELETE FROM languages WHERE user_id=:id AND language=:lang"
    SQLAlchemy.session.execute(delete_sql, {"id":user_id, "lang":language})
    SQLAlchemy.session.commit()

def get_languages(SQLAlchemy, username):

    user_id = database.get_user_id(SQLAlchemy, username)
    get_lang_sql = "SELECT language FROM languages WHERE user_id=:user_id"
    get_languages = SQLAlchemy.session.execute(get_lang_sql, {"user_id":user_id})
    
    try:
        languages = get_languages.fetchall()
        return languages
    except:
        return False
    
def check_if_learning(SQLAlchemy, username, language):

    if language.strip() == "":
        return True
        
    if len(language) < 3 or len(language) > 25:
        return True

    user_id = database.get_user_id(SQLAlchemy, username)
    get_lang_sql = "SELECT language FROM languages WHERE user_id=:user_id AND language=:language"
    get_language = SQLAlchemy.session.execute(get_lang_sql, {"user_id":user_id, 
    "language":language})

    try:
        language = get_language.fetchone()[0]
        if language == None:
            return False
        return True
    except:
        return False
    

