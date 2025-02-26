from flask import Flask, render_template, request, redirect, session, g
from db import get_db, close_connection, create_tables
import hashlib
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

with app.app_context():
    create_tables(app)

@app.route('/')
def index():
    if 'user' in session:
        return render_template('index.html', user=session['user'])
    else:
        return render_template('index.html')
    
@app.route('/products')
def products():
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT * FROM mahsulotlar')
    products = cur.fetchall()
    cur.close()
    if 'user' in session:
        return render_template('mahsulotlar.html', products=products, user=session['user'])
    else:
        return render_template('mahsulotlar.html', products=products)

@app.route('/product/<int:id>')
def product(id):
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT * FROM mahsulotlar WHERE id = ?', (id,))
    product = cur.fetchone()

    cur.execute('''
        SELECT foydalanuvchilar.foydalanuvchi_nomi, takliflar.narx, takliflar.vaqt
        FROM takliflar
        JOIN foydalanuvchilar ON takliflar.foydalanuvchi_id = foydalanuvchilar.id
        WHERE takliflar.mahsulot_id = ?
    ''', (id,))
    bids = cur.fetchall()

    cur.close()

    if 'user' in session:
        return render_template('mahsulot.html', product=product, user=session['user'], bids=bids)
    else:
        return render_template('mahsulot.html', product=product, bids=bids)
    
@app.route('/add_product', methods=['GET', 'POST'])
def addProduct():
    if request.method == 'GET':
        return render_template('mahsulot_qoshish.html', user=session['user'])
    elif request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        initial_price = request.form.get('initial_price')
        current_price = request.form.get('current_price')
        selling_date = request.form.get('selling_date')

        db = get_db()
        cur = db.cursor()
        cur.execute('''
            INSERT INTO mahsulotlar (nomi, tavsifi, boshlangich_narx, hozirgi_narx, sotish_muddati, sotuvchi_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (name, description, initial_price, current_price, selling_date, session['user'][0]))
        db.commit()
        cur.close()

        return redirect('/')
    else:
        return 'Method not allowed'
    
# id INTEGER PRIMARY KEY AUTOINCREMENT,
# mahsulot_id INTEGER,
# foydalanuvchi_id INTEGER,
# narx REAL,
# vaqt DATETIME,
# FOREIGN KEY (mahsulot_id) REFERENCES mahsulotlar(id),
# FOREIGN KEY (foydalanuvchi_id) REFERENCES foydalanuvchilar(id)
@app.route("/product/<int:id>/taklif", methods=['POST', "GET"])
def bid(id):
    if 'user' not in session:
        return redirect('/login')
    if request.method == 'GET':
        return render_template('taklif.html', id=id)
    
    if request.method == 'POST':
        price = request.form.get('price')

        db = get_db()
        cur = db.cursor()
        cur.execute('''
            INSERT INTO takliflar (mahsulot_id, foydalanuvchi_id, narx, vaqt)
            VALUES (?, ?, ?, ?)
        ''', (id, session['user'][0], price, datetime.now()))
        db.commit()
        cur.close()

        return redirect('/product/' + str(id))
    else:
        return 'Method not allowed'
    


@app.get('/login')
def login():
    return render_template('login.html')

@app.post('/login')
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')

    # Check if the username and password are correct
    db = get_db()
    cur = db.cursor()
    cur.execute('SELECT * FROM foydalanuvchilar WHERE foydalanuvchi_nomi = ?', (username,))
    user = cur.fetchone()
    cur.close()

    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    if user:
        session['user'] = user
        return redirect('/')
    else:
        return render_template('login.html', error='Username yoki parol noto\'g\'ri')

@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    
    elif request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        # Hash the password using bcrypt
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        db = get_db()
        cur = db.cursor()
        try:
            cur.execute('''INSERT INTO foydalanuvchilar (foydalanuvchi_nomi, parol) VALUES (?, ?)''', (username, hashed_password))
            db.commit()
            
            # Log the user in automatically after registration
            cur.execute('''SELECT * FROM foydalanuvchilar WHERE foydalanuvchi_nomi = ?''', (username,))
            user = cur.fetchone()
            session['user'] = user
            return redirect('/')
        
        except sqlite3.IntegrityError:
            return render_template('register.html', error='Bu foydalanuvchi nomi allaqachon mavjud')
        finally:
            cur.close()
    else:
        return 'Method not allowed'


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/')

@app.teardown_appcontext
def close_db(exception):
    close_connection()

if __name__ == '__main__':
    app.run(port=4200, debug=True)