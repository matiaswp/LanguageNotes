import app
from flask_sqlalchemy import SQLAlchemy
from flask import render_template
from os import getenv
from werkzeug.security import check_password_hash, generate_password_hash
import database

def list_lists(SQLAlchemy, username):

    get_lists_sql = "SELECT l.name FROM lists l, userinfo u WHERE l.user_id=u.id AND u.username=:username"
    get_lists = SQLAlchemy.session.execute(get_lists_sql, {"username":username})
    lists = get_lists.fetchall()
    
    return lists

def create_new_list(SQLAlchemy, username, listname):

    user_id = database.get_user_id(SQLAlchemy, username)

    if check_listname(SQLAlchemy, username, listname):
        return False
    
    insert_sql = "INSERT INTO lists (user_id, name) VALUES (:user_id, :name)"
    SQLAlchemy.session.execute(insert_sql, {"user_id":user_id, "name":listname})
    SQLAlchemy.session.commit()
    return True

def delete_list(SQLAlchemy, username, listname):

    list_id = get_list_id(SQLAlchemy, username, listname)

    delete_card_sql = "DELETE FROM cards WHERE list_id=:list_id"
    SQLAlchemy.session.execute(delete_card_sql, {"list_id":list_id})
    SQLAlchemy.session.commit()

    delete_list_sql = "DELETE FROM lists WHERE id=:list_id"
    SQLAlchemy.session.execute(delete_list_sql, {"list_id":list_id})
    SQLAlchemy.session.commit()
    return True

def edit_list(SQLAlchemy, username, listname, new_name):

    if check_listname(SQLAlchemy, username, new_name):
        return False

    user_id = database.get_user_id(SQLAlchemy, username)

    update_sql = "UPDATE lists SET name=:name WHERE user_id=:user_id AND name=:listname"
    SQLAlchemy.session.execute(update_sql, {"listname":listname, "name":new_name, "user_id":user_id})
    SQLAlchemy.session.commit()
    return True
  
def get_list_id(SQLAlchemy, username, listname):
    sql_list = "SELECT l.id FROM lists l, userinfo u WHERE l.user_id=u.id AND username=:username AND name=:name"
    get_list = SQLAlchemy.session.execute(sql_list, {"username":username, "name":listname})
    list_id = get_list.fetchone()[0]
    return list_id

def check_listname(SQLAlchemy, username, new_name):
    
    get_list_sql = "SELECT l.name FROM lists l, userinfo u WHERE l.user_id=u.id AND username=:username AND name=:name"
    get_list = SQLAlchemy.session.execute(get_list_sql, {"username":username, "name":new_name})
    try:
        get_name = get_list.fetchone()[0]
        if get_name == new_name:
            return True
    except:
        return False