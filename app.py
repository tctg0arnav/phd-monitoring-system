from flask import Flask, render_template, redirect, url_for, request, session


app = Flask(__name__)
app.secret_key = 'secretkey'

users = {
    'student': ['student',1],
    'supervisor': ['supervisor',2],
    'doc_comm': ['doc_comm',3],
    'hoau': ['hoau',4],
    'adordc': ['adordc',5],
    'dr_a': ['dr_a',6]
}

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
