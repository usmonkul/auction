from flask import Flask, render_template, request, redirect, session
import hashlib
from db import get_db, close_connection


app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.get('/login')
def login():
    return render_template('login.html')

@app.post('/login')
def login_post():
    username = request.form.get('username')
    password = request.form.get('password')

    # Hash the password
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    # Check if the username and password are correct
    cur = get_db().cursor()
    cur.execute('SELECT * FROM foydalanuvchilar WHERE foydalanuvchi_nomi = ? AND parol = ?', (username, hashed_password))
    user = cur.fetchone()

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

        # Hash the password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        # Save the username and password to the database
        cur = get_db().cursor()
        cur.execute('''INSERT INTO foydalanuvchilar (foydalanuvchi_nomi, parol) VALUES (?, ?)''', (username, hashed_password))
        cur.close()
        return redirect('/')
    else:
        return 'Method not allowed'


if __name__ == '__main__':
    app.run(port=4200, debug=True)