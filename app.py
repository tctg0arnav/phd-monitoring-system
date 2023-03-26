from flask import Flask, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import dateutil.parser as dparser
from pypdf import PdfWriter
import os
import yagmail
import sqlite3, os, datetime, pdfkit, jinja2, argparse

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
    student_name = db.Column(db.String(50))
    student_email = db.Column(db.String(50))
    AU = db.Column(db.String(10))
    DateOfRegistration = db.Column(db.DateTime)
    GATE = db.Column(db.Boolean)
    ProjectTitle = db.Column(db.String(100))
    DateOfIRB = db.Column(db.DateTime)
    DateOfProgressPresentation = db.Column(db.DateTime)
    Supervisor1 = db.Column(db.String(50))
    Supervisor1_email = db.Column(db.String(50))
    Supervisor1_remarks = db.Column(db.String(100))
    Supervisor1_approval = db.Column(db.String(50))
    Supervisor2 = db.Column(db.String(50))
    Supervisor2_email = db.Column(db.String(50))
    Supervisor2_remarks = db.Column(db.String(100))
    Supervisor2_approval = db.Column(db.String(50))
    Supervisor3 = db.Column(db.String(50))
    Supervisor3_email = db.Column(db.String(50))
    Supervisor3_remarks = db.Column(db.String(100))
    Supervisor3_approval = db.Column(db.String(50))
    #%workdonetillprev and %workdonetillpresent for each supervisor
    workdonetillprev1 = db.Column(db.Integer)
    workdonetillpresent1 = db.Column(db.Integer)
    workdonetillprev2 = db.Column(db.Integer)
    workdonetillpresent2 = db.Column(db.Integer)
    workdonetillprev3 = db.Column(db.Integer)
    workdonetillpresent3 = db.Column(db.Integer)
    Committee1 = db.Column(db.String(50))
    Committee1_email = db.Column(db.String(50))
    Committee1_remarks = db.Column(db.String(100))
    Committee1_approval = db.Column(db.String(50))
    Committee2 = db.Column(db.String(50))
    Committee2_email = db.Column(db.String(50))
    Committee2_remarks = db.Column(db.String(100))
    Committee2_approval = db.Column(db.String(50))
    Committee3 = db.Column(db.String(50))
    Committee3_email = db.Column(db.String(50))
    Committee3_remarks = db.Column(db.String(100))
    Committee3_approval = db.Column(db.String(50))
    Committee4 = db.Column(db.String(50))
    Committee4_email = db.Column(db.String(50))
    Committee4_remarks = db.Column(db.String(100))
    Committee4_approval = db.Column(db.String(50))
    Committee5 = db.Column(db.String(50))
    Committee5_email = db.Column(db.String(50))
    Committee5_remarks = db.Column(db.String(100))
    Committee5_approval = db.Column(db.String(50))
    FilePath = db.Column(db.String(100))
    Publications = db.Column(db.String(100))
    Conferences = db.Column(db.String(100))


class User(db.Model):
    email = db.Column(db.String(50), primary_key=True)
    password = db.Column(db.String(50))
    name = db.Column(db.String(50))
    role = db.Column(db.String(50))
    AU = db.Column(db.String(50))

@app.route('/')
def index():
    return """
    <h1>Routes</h1>
    <ul>
        <li><a href="/login">Login</a></li>
        <li><a href="/signup">Signup</a></li>
        <li><a href="/ticket">Ticket</a></li>
        <li><a href="/supervisor/1">Supervisor/1</a></li>
        <li><a href="/committee/1">Committee/1</a></li>
        <li><a href="/admin_dashboard">Admin Dashboard</a></li>
        <li><a href="/AU_head_dashboard">AU Head Dashboard</a></li>
    </ul>
    """


@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login_submit():
    email = request.form['email']
    password = request.form['password']
    user = User.query.filter_by(email=email).first()
    if user and user.password == password:
        session['user'] = user.email
        session['role'] = user.role
        if user.role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif user.role == 'AU_head':
            session['AU'] = user.AU
            return redirect(url_for('AU_dashboard'))

@app.route('/signup')
def signup():
    return render_template('signup.html')

@app.route('/signup', methods=['POST'])
def signup_submit():
    email = request.form['email']
    name = request.form['name']
    role = request.form['role']
    AU = request.form['AU']
    password = request.form['password']
    user = User(email=email, name=name, role=role, AU=AU, password=password)
    db.session.add(user)
    db.session.commit()
    return redirect(url_for('login'))

@app.route('/ticket')
def ticket():
    return render_template('ticket.html')

@app.route('/ticket', methods=['POST'])
def ticket_submit():
    student_name = request.form['student_name']
    RollNo = request.form['RollNo']
    student_email = request.form['student_email']
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
    Committee5 = request.form.get('Committee5')
    Committee5_email = request.form.get('Committee5_email')
    file = request.files.get('FilePath', None)
    FilePath = os.path.join(app.config['UPLOAD_FOLDER'], RollNo + '.pdf')
    file.save(FilePath)
    Publications = request.form.get('Publications')
    Conferences = request.form.get('Conferences')
    new_ticket = Ticket(student_name=student_name, student_email=student_email, RollNo=RollNo, AU=AU, DateOfRegistration=DateOfRegistration, GATE=GATE, ProjectTitle=ProjectTitle, DateOfIRB=DateOfIRB, DateOfProgressPresentation=DateOfProgressPresentation, Supervisor1=Supervisor1, Supervisor1_email=Supervisor1_email, Supervisor2=Supervisor2, Supervisor2_email=Supervisor2_email, Supervisor3=Supervisor3, Supervisor3_email=Supervisor3_email, Committee1=Committee1, Committee1_email=Committee1_email, Committee2=Committee2, Committee2_email=Committee2_email, Committee3=Committee3, Committee3_email=Committee3_email, Committee4=Committee4, Committee4_email=Committee4_email, Committee5=Committee5, Committee5_email = Committee5_email, FilePath=FilePath, Publications=Publications, Conferences=Conferences)
    db.session.add(new_ticket)
    db.session.commit()
    projectID = Ticket.query.filter_by(RollNo=RollNo).first().projectid
    ticket = Ticket.query.get(projectID)
    ticket = ticket.__dict__
    #create pdf from html using pdfkit
    pdf = pdfkit.from_string(ticket_static(projectID), False, options={"enable-local-file-access": ""})
    #save pdf to uploads folder
    with open(f'./uploads/ticket_{projectID}.pdf', 'wb') as f:
        f.write(pdf)
    return redirect(url_for('ticket_static', Ticket=ticket, projectid=projectID))

@app.route('/view/<int:projectid>', methods=['GET', 'POST'])
def ticket_static(projectid):
    ticket = Ticket.query.get(projectid)
    ticket = ticket.__dict__
    ticket['DateOfRegistration'] = ticket['DateOfRegistration'].strftime('%Y-%m-%d')
    ticket['DateOfIRB'] = ticket['DateOfIRB'].strftime('%Y-%m-%d')
    ticket['DateOfProgressPresentation'] = ticket['DateOfProgressPresentation'].strftime('%Y-%m-%d')
    if ticket['GATE']:
        ticket['gate_yes'] = 'checked'
        ticket['gate_no'] = ''
    else:
        ticket['gate_no'] = 'checked'
        ticket['gate_yes'] = ''
    print(ticket)
    return render_template('ticket_static.html', Ticket=ticket, projectid=projectid)

def send_mail(receiver,subject,body,attachment=None):
    yag = yagmail.SMTP('tempmail.xlcsgo@gmail.com', 'jjjthrbdtohkiomc')
    contents = [body]
    yag.send(receiver, subject, contents, attachments=attachment)
    return 0

@app.route('/supervisor/<int:projectid>', methods=['GET', 'POST'])
def supervisor(projectid):
    if request.method == 'GET':
        ticket = Ticket.query.get(projectid)
        ticket = ticket.__dict__
        return render_template('supervisor.html', Ticket=ticket, projectid=projectid)
    elif request.method == 'POST':
        supervisor_email = request.form['supervisor_email']
        if supervisor_email == Ticket.query.get(projectid).Supervisor1_email:
            Ticket.query.get(projectid).Supervisor1_remarks = request.form['remarks']
            workdonetillprev1 = request.form['percentage_prev']
            workdonetillnow1 = request.form['percentage_present']
            #put in database
            Ticket.query.get(projectid).workdonetillprev1 = workdonetillprev1
            Ticket.query.get(projectid).workdonetillnow1 = workdonetillnow1
            if request.form['approved'] == 'yes':
                Ticket.query.get(projectid).Supervisor1_approval = True
            else:
                Ticket.query.get(projectid).Supervisor1_approval = False
        elif supervisor_email == Ticket.query.get(projectid).Supervisor2_email:
            Ticket.query.get(projectid).Supervisor2_remarks = request.form['remarks']
            workdonetillprev2 = request.form['percentage_prev']
            workdonetillnow2 = request.form['percentage_present']
            #put in database
            Ticket.query.get(projectid).workdonetillprev2 = workdonetillprev2
            Ticket.query.get(projectid).workdonetillnow2 = workdonetillnow2
            if request.form['approved'] == 'yes':
                Ticket.query.get(projectid).Supervisor2_approval = True
            else:
                Ticket.query.get(projectid).Supervisor2_approval = False
        elif supervisor_email == Ticket.query.get(projectid).Supervisor3_email:
            Ticket.query.get(projectid).Supervisor3_remarks = request.form['remarks']
            workdonetillprev3 = request.form['percentage_prev']
            workdonetillnow3 = request.form['percentage_present']
            #put in database
            Ticket.query.get(projectid).workdonetillprev3 = workdonetillprev3
            Ticket.query.get(projectid).workdonetillnow3 = workdonetillnow3
            if request.form['approved'] == 'yes':
                Ticket.query.get(projectid).Supervisor3_approval = True
            else:
                Ticket.query.get(projectid).Supervisor3_approval = False
        db.session.commit()
        return redirect(url_for('index'))

@app.route('/committee/<int:projectid>', methods=['GET', 'POST'])
def committee(projectid):
    if request.method == 'GET':
        return render_template('committee.html', pdf_path=f'/uploads/ticket_{projectid}.pdf')
    else:
        committee_email = request.form['committee_email']
        if committee_email == Ticket.query.get(projectid).Committee1_email:
            Ticket.query.get(projectid).Committee1_remarks = request.form['committee_remarks']
            if request.form['submit'] == 'approve':
                Ticket.query.get(projectid).Committee1_approval = True
            else:
                Ticket.query.get(projectid).Committee1_approval = False
        elif committee_email == Ticket.query.get(projectid).Committee2_email:
            Ticket.query.get(projectid).Committee2_remarks = request.form['committee_remarks']
            if request.form['submit'] == 'approve':
                Ticket.query.get(projectid).Committee2_approval = True
            else:
                Ticket.query.get(projectid).Committee2_approval = False
        elif committee_email == Ticket.query.get(projectid).Committee3_email:
            Ticket.query.get(projectid).Committee3_remarks = request.form['committee_remarks']
            if request.form['submit'] == 'approve':
                Ticket.query.get(projectid).Committee3_approval = True
            else:
                Ticket.query.get(projectid).Committee3_approval = False
        elif committee_email == Ticket.query.get(projectid).Committee4_email:
            Ticket.query.get(projectid).Committee4_remarks = request.form['committee_remarks']
            if request.form['submit'] == 'approve':
                Ticket.query.get(projectid).Committee4_approval = True
            else:
                Ticket.query.get(projectid).Committee4_approval = False
        elif committee_email == Ticket.query.get(projectid).Committee5_email:
            Ticket.query.get(projectid).Committee5_remarks = request.form['committee_remarks']
            if request.form['submit'] == 'approve':
                Ticket.query.get(projectid).Committee5_approval = True
            else:
                Ticket.query.get(projectid).Committee5_approval = False
        db.session.commit()


@app.route('/supervisor_dashboard')
def supervisor_dashboard():
    supervisor_email = session['email']
    projects = Ticket.query.filter((Ticket.Supervisor1_email == supervisor_email) | (Ticket.Supervisor2_email == supervisor_email) | (Ticket.Supervisor3_email == supervisor_email)).all()
    return render_template('supervisor_dashboard.html', projects=projects)


@app.route('/committee_dashboard')
def committee_dashboard():
    committee_email = session['email']
    projects = Ticket.query.filter((Ticket.Committee1_email == committee_email) | (Ticket.Committee2_email == committee_email) | (Ticket.Committee3_email == committee_email) | (Ticket.Committee4_email == committee_email) | (Ticket.Committee5_email == committee_email)).all()
    return render_template('committee_dashboard.html', projects=projects)


@app.route('/AU_dashboard')
def AU_dashboard():
    AU = session['AU']
    projects = Ticket.query.filter(Ticket.AU == AU).all()
    for project in projects:
        if project.Supervisor1_approval == True:
            project.approved = project.Supervisor1
            if project.Supervisor2_approval == True:
                project.approved = project.approved + ", " + project.Supervisor2
                if project.Supervisor3_approval == True:
                    project.approved = project.approved + ", " + project.Supervisor3
            elif project.Supervisor3_approval == True:
                project.approved = project.approved + ", " + project.Supervisor3
        elif project.Supervisor2_approval == True:
            project.approved = project.Supervisor2
            if project.Supervisor3_approval == True:
                project.approved = project.approved + ", " + project.Supervisor3
        elif project.Supervisor3_approval == True:
            project.approved = project.Supervisor3
        else:
            project.approved = "None"
    projects = [project.__dict__ for project in projects] 
    return render_template('AU_dashboard.html', projects=projects)

@app.route('/AU_dashboard/filter', methods=['GET', 'POST'])
def AU_dashboard_filter():
    if request.form['filter'] == 'all':
        projects = Ticket.query.filter(Ticket.AU == session['AU']).all()
        return render_template('AU_dashboard.html', projects=projects)
    elif request.form['filter'] == 'approved':
        projects = Ticket.query.filter((Ticket.AU == session['AU']) & (Ticket.Supervisor1_approval == True) & (Ticket.Supervisor2_approval == True) & (Ticket.Supervisor3_approval == True) & (Ticket.Committee1_approval == True) & (Ticket.Committee2_approval == True) & (Ticket.Committee3_approval == True) & (Ticket.Committee4_approval == True) & (Ticket.Committee5_approval == True)).all()
        return render_template('AU_dashboard.html', projects=projects)
    elif request.form['filter'] == 'unapproved':
        projects = Ticket.query.filter((Ticket.AU == session['AU']) & ((Ticket.Supervisor1_approval == False) | (Ticket.Supervisor2_approval == False) | (Ticket.Supervisor3_approval == False) | (Ticket.Committee1_approval == False) | (Ticket.Committee2_approval == False) | (Ticket.Committee3_approval == False) | (Ticket.Committee4_approval == False) | (Ticket.Committee5_approval == False))).all()
        return render_template('AU_dashboard.html', projects=projects)
    for project in projects:
        if project.Supervisor1_approval == True:
            project.approved = project.Supervisor1
            if project.Supervisor2_approval == True:
                project.approved = project.approved + ", " + project.Supervisor2
                if project.Supervisor3_approval == True:
                    project.approved = project.approved + ", " + project.Supervisor3
            elif project.Supervisor3_approval == True:
                project.approved = project.approved + ", " + project.Supervisor3
        elif project.Supervisor2_approval == True:
            project.approved = project.Supervisor2
            if project.Supervisor3_approval == True:
                project.approved = project.approved + ", " + project.Supervisor3
        elif project.Supervisor3_approval == True:
            project.approved = project.Supervisor3
        else:
            project.approved = "None"
    projects = [project.__dict__ for project in projects]


@app.route('/admin_dashboard')
def admin_dashboard():
    projects = Ticket.query.all()
    projects = [project.__dict__ for project in projects]
    return render_template('admin_dashboard.html', projects=projects)

@app.route('/admin_dashboard/filter', methods=['GET', 'POST'])
def admin_dashboard_filter():
    if request.form['filter_approval'] == 'all' and request.form['filter_AU'] == 'all':
        projects = Ticket.query.all()
        for project in projects:
            if project.Supervisor1_approval == True:
                project.approved = project.Supervisor1
                if project.Supervisor2_approval == True:
                    project.approved = project.approved + ", " + project.Supervisor2
                    if project.Supervisor3_approval == True:
                        project.approved = project.approved + ", " + project.Supervisor3
                elif project.Supervisor3_approval == True:
                    project.approved = project.approved + ", " + project.Supervisor3
            elif project.Supervisor2_approval == True:
                project.approved = project.Supervisor2
                if project.Supervisor3_approval == True:
                    project.approved = project.approved + ", " + project.Supervisor3
            elif project.Supervisor3_approval == True:
                project.approved = project.Supervisor3
            else:
                project.approved = "None"
        projects = [project.__dict__ for project in projects]
        return render_template('admin_dashboard.html', projects=projects)
    elif request.form['filter_approval'] == 'approved' and request.form['filter_AU'] == 'all':
        projects = Ticket.query.filter((Ticket.Supervisor1_approval == True) & (Ticket.Supervisor2_approval == True) & (Ticket.Supervisor3_approval == True) & (Ticket.Committee1_approval == True) & (Ticket.Committee2_approval == True) & (Ticket.Committee3_approval == True) & (Ticket.Committee4_approval == True) & (Ticket.Committee5_approval == True)).all()
        for project in projects:
            if project.Supervisor1_approval == True:
                project.approved = project.Supervisor1
                if project.Supervisor2_approval == True:
                    project.approved = project.approved + ", " + project.Supervisor2
                    if project.Supervisor3_approval == True:
                        project.approved = project.approved + ", " + project.Supervisor3
                elif project.Supervisor3_approval == True:
                    project.approved = project.approved + ", " + project.Supervisor3
            elif project.Supervisor2_approval == True:
                project.approved = project.Supervisor2
                if project.Supervisor3_approval == True:
                    project.approved = project.approved + ", " + project.Supervisor3
            elif project.Supervisor3_approval == True:
                project.approved = project.Supervisor3
            else:
                project.approved = "None"
        projects = [project.__dict__ for project in projects]
        return render_template('admin_dashboard.html', projects=projects)
    elif request.form['filter_approval'] == 'unapproved' and request.form['filter_AU'] == 'all':
        projects = Ticket.query.filter((Ticket.Supervisor1_approval == False) | (Ticket.Supervisor2_approval == False) | (Ticket.Supervisor3_approval == False) | (Ticket.Committee1_approval == False) | (Ticket.Committee2_approval == False) | (Ticket.Committee3_approval == False) | (Ticket.Committee4_approval == False) | (Ticket.Committee5_approval == False)).all()
        for project in projects:
            if project.Supervisor1_approval == True:
                project.approved = project.Supervisor1
                if project.Supervisor2_approval == True:
                    project.approved = project.approved + ", " + project.Supervisor2
                    if project.Supervisor3_approval == True:
                        project.approved = project.approved + ", " + project.Supervisor3
                elif project.Supervisor3_approval == True:
                    project.approved = project.approved + ", " + project.Supervisor3
            elif project.Supervisor2_approval == True:
                project.approved = project.Supervisor2
                if project.Supervisor3_approval == True:
                    project.approved = project.approved + ", " + project.Supervisor3
            elif project.Supervisor3_approval == True:
                project.approved = project.Supervisor3
            else:
                project.approved = "None"
        projects = [project.__dict__ for project in projects]
        return render_template('admin_dashboard.html', projects=projects)
    elif request.form['filter_approval'] == 'all' and request.form['filter_AU'] != 'all':
        projects = Ticket.query.filter(Ticket.AU == request.form['filter_AU']).all()
        for project in projects:
            if project.Supervisor1_approval == True:
                project.approved = project.Supervisor1
                if project.Supervisor2_approval == True:
                    project.approved = project.approved + ", " + project.Supervisor2
                    if project.Supervisor3_approval == True:
                        project.approved = project.approved + ", " + project.Supervisor3
                elif project.Supervisor3_approval == True:
                    project.approved = project.approved + ", " + project.Supervisor3
            elif project.Supervisor2_approval == True:
                project.approved = project.Supervisor2
                if project.Supervisor3_approval == True:
                    project.approved = project.approved + ", " + project.Supervisor3
            elif project.Supervisor3_approval == True:
                project.approved = project.Supervisor3
            else:
                project.approved = "None"
        projects = [project.__dict__ for project in projects]
        return render_template('admin_dashboard.html', projects=projects)
    elif request.form['filter_approval'] == 'approved' and request.form['filter_AU'] != 'all':
        projects = Ticket.query.filter((Ticket.AU == request.form['filter_AU']) & (Ticket.Supervisor1_approval == True) & (Ticket.Supervisor2_approval == True) & (Ticket.Supervisor3_approval == True) & (Ticket.Committee1_approval == True) & (Ticket.Committee2_approval == True) & (Ticket.Committee3_approval == True) & (Ticket.Committee4_approval == True) & (Ticket.Committee5_approval == True)).all()
        for project in projects:
            if project.Supervisor1_approval == True:
                project.approved = project.Supervisor1
                if project.Supervisor2_approval == True:
                    project.approved = project.approved + ", " + project.Supervisor2
                    if project.Supervisor3_approval == True:
                        project.approved = project.approved + ", " + project.Supervisor3
                elif project.Supervisor3_approval == True:
                    project.approved = project.approved + ", " + project.Supervisor3
            elif project.Supervisor2_approval == True:
                project.approved = project.Supervisor2
                if project.Supervisor3_approval == True:
                    project.approved = project.approved + ", " + project.Supervisor3
            elif project.Supervisor3_approval == True:
                project.approved = project.Supervisor3
            else:
                project.approved = "None"
        projects = [project.__dict__ for project in projects]
        return render_template('admin_dashboard.html', projects=projects)
    elif request.form['filter_approval'] == 'unapproved' and request.form['filter_AU'] != 'all':
        projects = Ticket.query.filter((Ticket.AU == request.form['filter_AU']) & ((Ticket.Supervisor1_approval == False) | (Ticket.Supervisor2_approval == False) | (Ticket.Supervisor3_approval == False) | (Ticket.Committee1_approval == False) | (Ticket.Committee2_approval == False) | (Ticket.Committee3_approval == False) | (Ticket.Committee4_approval == False) | (Ticket.Committee5_approval == False))).all()
        for project in projects:
            if project.Supervisor1_approval == True:
                project.approved = project.Supervisor1
                if project.Supervisor2_approval == True:
                    project.approved = project.approved + ", " + project.Supervisor2
                    if project.Supervisor3_approval == True:
                        project.approved = project.approved + ", " + project.Supervisor3
                elif project.Supervisor3_approval == True:
                    project.approved = project.approved + ", " + project.Supervisor3
            elif project.Supervisor2_approval == True:
                project.approved = project.Supervisor2
                if project.Supervisor3_approval == True:
                    project.approved = project.approved + ", " + project.Supervisor3
            elif project.Supervisor3_approval == True:
                project.approved = project.Supervisor3
            else:
                project.approved = "None"
        projects = [project.__dict__ for project in projects]
        return render_template('admin_dashboard.html', projects=projects)


if __name__ == '__main__':
    app.run(debug=True, port=5001)
