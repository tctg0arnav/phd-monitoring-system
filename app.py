from flask import Flask, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
import sqlite3


app = Flask(__name__)
app.secret_key = 'secretkey'

# users = {
#     'student': ['student',1],
#     'supervisor': ['supervisor',2],
#     'doc_comm': ['doc_comm',3],
#     'hoau': ['hoau',4],
#     'adordc': ['adordc',5],
#     'dr_a': ['dr_a',6]
# }

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    tier = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(20), nullable=False)
    surname = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    AU = db.Column(db.String(20), nullable=False)

class project(db.Model):
    projectid = db.Column(db.Integer, primary_key=True)
    AU = db.Column(db.String(20), nullable=False)
    studentid = db.Column(db.Integer, nullable=False)
    date_of_registration = db.Column(db.date, nullable=False)
    GATE = db.Column(db.boolean, nullable=False)
    project_title = db.Column(db.String(50), nullable=False)
    date_of_irb = db.Column(db.date, nullable=False)
    date_of_progress_present = db.Column(db.date, nullable=False)
    file_path = db.Column(db.String(50), nullable=False)
    publications = db.Column(db.String(50), nullable=False)
    conferences = db.Column(db.String(50), nullable=False)
    

@app.route('/')
def index():
    # Redirect to login page
    print(session)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    # Check if user is already logged in
    if 'username' in session:
        print(session)
        return redirect(url_for('dashboard',tier=users[session['username']][1]))

    if request.method == 'POST':
        print(session)
        username = request.form['username']
        password = request.form['password']

        # Check if username and password are valid
        if username in users and password == users[username][0]:
            session['username'] = username
            print(session)
            tier = users[username][1]
            return redirect(url_for('dashboard', tier=tier))
        else:
            error = 'Invalid username or password.'
            return render_template('login.html', error=error)
    else:
        return render_template('login.html')

@app.route('/dashboard/<int:tier>')
def dashboard(tier):
    # Check if tier is valid
    if 'username' not in session:
        print(session)
        return redirect(url_for('login'))
    return render_template('dashboard.html', tier=tier)


@app.route('/logout')
def logout():
    session.clear()
    print(session)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
