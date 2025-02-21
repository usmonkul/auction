import sqlite3
from flask import g
from flask import Flask
from run import app

DATABASE = 'auction.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.execute('PRAGMA foreign_keys = ON')
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def execute_query(query):
    db = get_db()
    cursor = db.cursor()
    try:
        cursor.execute(query)
        db.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        cursor.close()

def create_foydalanuvchilar_table():
    query = '''CREATE TABLE IF NOT EXISTS foydalanuvchilar (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                foydalanuvchi_nomi TEXT, 
                parol TEXT)'''
    execute_query(query)

def create_mahsulotlar_table():
    query = '''CREATE TABLE IF NOT EXISTS mahsulotlar (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                nomi TEXT, 
                tavsifi TEXT, 
                boshlangich_narx REAL, 
                hozirgi_narx REAL, 
                sotish_muddati DATETIME, 
                sotuvchi_id INTEGER,
                FOREIGN KEY (sotuvchi_id) REFERENCES foydalanuvchilar(id))'''
    execute_query(query)

def create_takliflar_table():
    query = '''CREATE TABLE IF NOT EXISTS takliflar (
                id INTEGER PRIMARY KEY AUTOINCREMENT, 
                mahsulot_id INTEGER, 
                foydalanuvchi_id INTEGER, 
                narx REAL, 
                vaqt DATETIME,
                FOREIGN KEY (mahsulot_id) REFERENCES mahsulotlar(id),
                FOREIGN KEY (foydalanuvchi_id) REFERENCES foydalanuvchilar(id))'''
    execute_query(query)

if __name__ == '__main__':
    with app.app_context():
        create_foydalanuvchilar_table()
        create_mahsulotlar_table()
        create_takliflar_table()
        print("Tables created successfully.")