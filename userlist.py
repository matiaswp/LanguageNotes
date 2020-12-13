import app
from flask_sqlalchemy import SQLAlchemy
import database
import userlists

def add_card_to_list(SQLAlchemy, username, listname, word, translation):

    list_id = userlists.get_list_id(SQLAlchemy, username, listname)

    sql3 = "INSERT INTO cards (word, translation, date, list_id, difficulty) VALUES"\
         "(:word, :translation, NOW(), :list_id, 1)"
    SQLAlchemy.session.execute(sql3, {"word":word,"translation":translation,"list_id":list_id})
    SQLAlchemy.session.commit()

def remove_card_from_list(SQLAlchemy, username, listname, word, translation):
    list_id = userlists.get_list_id(SQLAlchemy, username, listname)

    delete_sql = "DELETE FROM cards WHERE word=:word AND list_id=:list_id "\
         "AND translation=:translation"
    SQLAlchemy.session.execute(delete_sql, {"word":word, "list_id":list_id, \
        "translation":translation})
    SQLAlchemy.session.commit()

def edit_card(SQLAlchemy, listname, username, word, translation, new_word, new_translation):
    
    list_id = userlists.get_list_id(SQLAlchemy, username, listname)

    update_sql = "UPDATE cards SET word=:new_word, translation=:new_translation"\
        " WHERE list_id=:list_id AND word=:word AND translation=:translation"
    SQLAlchemy.session.execute(update_sql, {"new_word": new_word, "new_translation":new_translation, 
    "word":word , "translation":translation, "list_id":list_id})

    SQLAlchemy.session.commit()
    return True

def show_cards(SQLAlchemy, username, listname):

    list_id = list_id = userlists.get_list_id(SQLAlchemy, username, listname)

    sql3 = "SELECT word, translation, date FROM cards WHERE list_id=:list_id ORDER BY date"
    get_cards = SQLAlchemy.session.execute(sql3, {"list_id":list_id})
    cards = get_cards.fetchall()

    return cards

def show_study_cards(SQLAlchemy, username, listname):

    list_id = list_id = userlists.get_list_id(SQLAlchemy, username, listname)

    sql3 = "SELECT word, translation FROM cards WHERE list_id=:list_id AND date<=NOW() "\
        "ORDER BY date"
    get_cards = SQLAlchemy.session.execute(sql3, {"list_id":list_id})
    cards = get_cards.fetchall()
    return cards

def add_more_date(SQLAlchemy, username, listname, word, translation, answer):

    list_id = list_id = userlists.get_list_id(SQLAlchemy, username, listname)

    get_card_sql = "SELECT id FROM cards WHERE word=:word AND "\
            "translation=:translation AND list_id=:list_id"
    get_card = SQLAlchemy.session.execute(get_card_sql, {"word":word, 
    "translation":translation, "list_id":list_id})
    card_id = get_card.fetchone()[0]

    get_difficulty_sql = "SELECT difficulty FROM cards WHERE word=:word AND "\
            "translation=:translation AND list_id=:list_id"
    get_difficulty = SQLAlchemy.session.execute(get_difficulty_sql, {"word":word, 
    "translation":translation, "list_id":list_id})
    difficulty = get_difficulty.fetchone()[0]

    update_diff_sql = "UPDATE cards SET difficulty=:new_diff, date=NOW()+ "\
    "INTERVAL':date day' WHERE id="+str(card_id)
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

        SQLAlchemy.session.execute(update_diff_sql, {"new_diff":new_diff, "date":date})
        SQLAlchemy.session.commit()
    else:
        date = 1
        if difficulty == 1:
            date = 0    
        SQLAlchemy.session.execute(update_diff_sql, {"new_diff":1, "date":date})
        SQLAlchemy.session.commit()
    return True

