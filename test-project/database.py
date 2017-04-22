import sqlite3
from random import randint

# define global variables
db_name = 'database.db'
tables = ['users', 'quotes']
table_queries = ["CREATE TABLE IF NOT EXISTS users (" +
                 "id INTEGER PRIMARY KEY AUTOINCREMENT, " +
                 "email text, " +
                 "password text)",

                 "CREATE TABLE IF NOT EXISTS quotes (" +
                 "id INTEGER PRIMARY KEY AUTOINCREMENT, " +
                 "user_id INTEGER, " +
                 "quote text)"]


# this method can also be used for executing queries that don't require a result.
def execute(query):
    db = get_db()
    cursor = db.cursor()
    cursor.execute(query)
    db.commit()


def add_user(user):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO users(email, password) VALUES(?, ?)", user)
    db.commit()


def user_exists(email):
    return select_user(email) is not None


def select_user(email):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM users WHERE email=?", (email, ))
    return cursor.fetchone()


def add_quote(user_id, quote):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("INSERT INTO quotes(user_id, quote) VALUES(?, ?)", (user_id, quote))
    db.commit()


def get_quotes(user_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM quotes WHERE user_id=?", (user_id,))
    return cursor.fetchall()


def get_random_quote(user_id):
    quotes = get_quotes(user_id)
    if len(quotes) == 0:
        return "You don't have any quotes"
    random = randint(0, len(quotes) - 1)
    return quotes[random][2]


def get_db():
    return sqlite3.connect(db_name)


def create_tables():
    for query in table_queries:
        execute(query=query)
