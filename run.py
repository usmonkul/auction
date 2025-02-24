from flask import Flask, render_template, request, redirect, session, g
from db import get_db, close_connection, create_tables
import hashlib
import sqlite3

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

    return render_template('mahsulotlar.html', products=products)
    
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