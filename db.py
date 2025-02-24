import sqlite3
from flask import g

DATABASE = 'auction.db'

def get_db():
    db = sqlite3.connect(DATABASE)
    db.execute('PRAGMA foreign_keys = ON')
    return db

def close_connection(exception=None):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def create_tables(app):
    """
    Create the necessary tables in the database.
    """
    with app.app_context():
        db = get_db()
        cursor = db.cursor()

        # Foydalanuvchi jadvali
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS foydalanuvchilar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                foydalanuvchi_nomi TEXT UNIQUE,
                parol TEXT
            )
        ''')
        # mahsulotlar jadvali
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS mahsulotlar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nomi TEXT,
                tavsifi TEXT,
                boshlangich_narx REAL,
                hozirgi_narx REAL,
                sotish_muddati DATETIME,
                sotuvchi_id INTEGER,
                FOREIGN KEY (sotuvchi_id) REFERENCES foydalanuvchilar(id)
            )
        ''')
        # takliflar jadvali
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS takliflar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                mahsulot_id INTEGER,
                foydalanuvchi_id INTEGER,
                narx REAL,
                vaqt DATETIME,
                FOREIGN KEY (mahsulot_id) REFERENCES mahsulotlar(id),
                FOREIGN KEY (foydalanuvchi_id) REFERENCES foydalanuvchilar(id)
            )
        ''')

        db.commit()
        cursor.close()


if __name__ == '__main__':
    from flask import Flask
    app = Flask(__name__)
    create_tables(app)
    print("Tables created successfully.")