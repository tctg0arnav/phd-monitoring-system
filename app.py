from flask import Flask, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import dateutil.parser as dparser
import sqlite3, os, datetime

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)
app.secret_key = 'secretkey'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)


class Ticket(db.Model):
    projectid = db.Column(db.Integer, primary_key=True)
    RollNo = db.Column(db.Integer)
    AU = db.Column(db.String(10))
    DateOfRegistration = db.Column(db.DateTime)
    GATE = db.Column(db.Boolean)
    ProjectTitle = db.Column(db.String(100))
    DateOfIRB = db.Column(db.DateTime)
    DateOfProgressPresentation = db.Column(db.DateTime)
    Supervisor1 = db.Column(db.String(50))
    Supervisor1_email = db.Column(db.String(50))
    Supervisor2 = db.Column(db.String(50))
    Supervisor2_email = db.Column(db.String(50))
    Supervisor3 = db.Column(db.String(50))
    Supervisor3_email = db.Column(db.String(50))
    Committee1 = db.Column(db.String(50))
    Committee1_email = db.Column(db.String(50))
    Committee2 = db.Column(db.String(50))
    Committee2_email = db.Column(db.String(50))
    Committee3 = db.Column(db.String(50))
    Committee3_email = db.Column(db.String(50))
    Committee4 = db.Column(db.String(50))
    Committee4_email = db.Column(db.String(50))
    FilePath = db.Column(db.String(100))
    Publications = db.Column(db.String(100))
    Conferences = db.Column(db.String(100))

@app.route('/ticket')
def ticket():
    return render_template('ticket.html')

@app.route('/ticket', methods=['POST'])
def ticket_submit():
    RollNo = request.form['RollNo']
    AU = request.form['AU']
    DateOfRegistration = request.form['DateOfRegistration']
    DateOfRegistration = dparser.parse(DateOfRegistration, fuzzy=True)
    GATE = request.form['GATE']
    if GATE == 'Yes':
        GATE = True
    else:
        GATE = False
    ProjectTitle = request.form['ProjectTitle']
    DateOfIRB = request.form['DateOfIRB']
    DateOfIRB = dparser.parse(DateOfIRB, fuzzy=True)
    DateOfProgressPresentation = request.form['DateOfProgressPresentation']
    DateOfProgressPresentation = dparser.parse(DateOfProgressPresentation, fuzzy=True)
    Supervisor1 = request.form['Supervisor1']
    Supervisor1_email = request.form['Supervisor1_email']
    Supervisor2 = request.form.get('Supervisor2')
    Supervisor2_email = request.form.get('Supervisor2_email')
    Supervisor3 = request.form.get('Supervisor3')
    Supervisor3_email = request.form.get('Supervisor3_email')
    Committee1 = request.form['Committee1']
    Committee1_email = request.form['Committee1_email']
    Committee2 = request.form['Committee2']
    Committee2_email = request.form['Committee2_email']
    Committee3 = request.form['Committee3']
    Committee3_email = request.form['Committee3_email']
    Committee4 = request.form['Committee4']
    Committee4_email = request.form['Committee4_email']
    file = request.files.get('FilePath', None)
    filename = secure_filename(RollNo + '.pdf')
    FilePath = os.path.join(app.config['UPLOAD_FOLDER'], RollNo + '.pdf')
    file.save(FilePath)
    Publications = request.form.get('Publications')
    Conferences = request.form.get('Conferences')
    print(request.form)
    #store data in database
    new_ticket = Ticket(RollNo=RollNo, AU=AU, DateOfRegistration=DateOfRegistration, GATE=GATE, ProjectTitle=ProjectTitle, DateOfIRB=DateOfIRB, DateOfProgressPresentation=DateOfProgressPresentation, Supervisor1=Supervisor1, Supervisor1_email=Supervisor1_email, Supervisor2=Supervisor2, Supervisor2_email=Supervisor2_email, Supervisor3=Supervisor3, Supervisor3_email=Supervisor3_email, Committee1=Committee1, Committee1_email=Committee1_email, Committee2=Committee2, Committee2_email=Committee2_email, Committee3=Committee3, Committee3_email=Committee3_email, Committee4=Committee4, Committee4_email=Committee4_email, FilePath=FilePath, Publications=Publications, Conferences=Conferences)
    db.session.add(new_ticket)
    db.session.commit()

    return render_template('ticket.html', message=1)

@app.route('/view', methods=['GET', 'POST'])
def view():
    #get data from database
    tickets = Ticket.query.all()
    return render_template('view.html', tickets=tickets)

if __name__ == '__main__':
    app.run(debug=True)
