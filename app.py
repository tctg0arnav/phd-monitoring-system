from flask import Flask, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import sqlite3, os, datetime

UPLOAD_FOLDER = '/static/uploads'
ALLOWED_EXTENSIONS = {'pdf'}

app = Flask(__name__)
app.secret_key = 'secretkey'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER




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
    regroll = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(20), nullable=False)
    tier = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(20), nullable=False)
    surname = db.Column(db.String(20), nullable=False)
    email = db.Column(db.String(50), nullable=False)
    AU = db.Column(db.String(20), nullable=False)

class project(db.Model):
    projectid = db.Column(db.Integer, db.Sequence('my_table_id_seq', start=1, increment=1), primary_key=True, server_default=db.text("to_char(nextval('my_table_id_seq'),'0000')"))
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
    worktillprev = db.Column(db.integer, nullable=False)
    worktillnow = db.Column(db.integer, nullable=False)

class remarks(db.Model):
    projectid = db.Column(db.Integer, nullable=False)
    remark = db.Column(db.String(50), nullable=False)
    date = db.Column(db.date, nullable=False)
    remark_by = db.Column(db.String(20), nullable=False)

class supervisors(db.Model):
    projectid = db.Column(db.Integer, nullable=False)
    supervisorX = db.Column(db.String(20), nullable=False)
    sx_approve = db.Column(db.boolean, nullable=False, default=False)
    supervisorY = db.Column(db.String(20))
    sy_approve = db.Column(db.boolean)
    supervisorZ = db.Column(db.String(20))
    sz_approve = db.Column(db.boolean)

class committee(db.Model):
    projectid = db.Column(db.Integer, nullable=False)
    committeeX = db.Column(db.String(20), nullable=False)
    cx_approve = db.Column(db.boolean, nullable=False, default=False)
    committeeY = db.Column(db.String(20), nullable=False)
    cy_approve = db.Column(db.boolean, nullable=False, default=False)
    committeeZ = db.Column(db.String(20), nullable=False)
    cz_approve = db.Column(db.boolean, nullable=False, default=False)
    committeeA = db.Column(db.String(20), nullable=False)
    ca_approve = db.Column(db.boolean, nullable=False, default=False)

#login page route that checks username and password against username and password in Users table of database and redirects to dashboard
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        session.pop('user', None)
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['user'] = username
            return redirect(url_for('dashboard'))
        return 'Invalid username or password'
    return render_template('login.html')

#dashboard route that checks if user is logged in and redirects to login page if not
@app.route('/dashboard')
def dashboard():
    if session.get('user'):
        #if tier in database for username = username in session is 1 then redirect to student dashboard
        if User.query.filter_by(username=session.get('user')).first().tier == 1:
            return redirect(url_for('ticket'))
        elif User.query.filter_by(username=session.get('user')).first().tier == 2:
            return redirect(url_for('supervisor_dash'))
        elif User.query.filter_by(username=session.get('user')).first().tier == 3:
            return render_template('doc_comm_dashboard.html')
        elif User.query.filter_by(username=session.get('user')).first().tier == 4:
            return render_template('hoau_dashboard.html')
        elif User.query.filter_by(username=session.get('user')).first().tier == 5:
            return render_template('adordc_dashboard.html')
        elif User.query.filter_by(username=session.get('user')).first().tier == 6:
            return render_template('dr_a_dashboard.html')
        else:
            return render_template('login.html')
    return redirect(url_for('login'))

#ticket route that checks if tier in database for username = username in session is 1 and redirects to dashboard if not
@app.route('/ticket', methods=['GET', 'POST'])
def ticket():
    if User.query.filter_by(username=session.get('user')).first().tier == 1:
        if request.method == 'POST':
            #get data from form
            AU = request.form['AU']
            studentid = request.form['studentid']
            date_of_registration = request.form['date_of_registration']
            GATE = request.form['GATE']
            project_title = request.form['project_title']
            date_of_irb = request.form['date_of_irb']
            date_of_progress_present = request.form['date_of_progress_present']
            supervisorX = request.form['supervisorX']
            supervisorY = request.form['supervisorY']
            supervisorZ = request.form['supervisorZ']
            committeeX = request.form['committeeX']
            committeeY = request.form['committeeY']
            committeeZ = request.form['committeeZ']
            committeeA = request.form['committeeA']
            file = request.files['file']
            publications = request.form['publications']
            conferences = request.form['conferences']
            #check if file is present and save file to uploads folder with filename as studentid and get file path to save in database
            if file:
                filename = studentid
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            #save data to database
            new_project = project(AU=AU, studentid=studentid, date_of_registration=date_of_registration, GATE=GATE, project_title=project_title, date_of_irb=date_of_irb, date_of_progress_present=date_of_progress_present, file_path=file_path, publications=publications, conferences=conferences)
            db.session.add(new_project)
            db.session.commit()
            #take projectid from project table and store in variable
            projectid = project.query.filter_by(studentid=studentid).first().projectid
            new_supervisor = supervisors(projectid=projectid, supervisorX=supervisorX, supervisorY=supervisorY, supervisorZ=supervisorZ)
            db.session.add(new_supervisor)
            db.session.commit()
            new_committee = committee(projectid=projectid, committeeX=committeeX, committeeY=committeeY, committeeZ=committeeZ, committeeA=committeeA)
            db.session.add(new_committee)
            db.session.commit()
            return redirect(url_for('ticket'))
        return render_template('ticket.html')
    return redirect(url_for('dashboard'))

@app.route('/supervisor_dash', methods=['GET', 'POST'])
def supervisor_dash():
    #if tier in database for username = username in session is 2 then redirect to supervisor dashboard
    if User.query.filter_by(username=session.get('user')).first().tier == 2:
        #for each project in project table if supervisorX, supervisorY or supervisorZ in database for projectid = projectid in project table is username in session then add project to list
        projects = []
        for project in project.query.all():
            if supervisors.query.filter_by(projectid=project.projectid).first().supervisorX == session.get('user') or supervisors.query.filter_by(projectid=project.projectid).first().supervisorY == session.get('user') or supervisors.query.filter_by(projectid=project.projectid).first().supervisorZ == session.get('user'):
                projects.append(project)
        #pass projects list to supervisor dashboard template
        return render_template('supervisor_dashboard.html', projects=projects)
    return redirect(url_for('dashboard'))

@app.route('/supervisor_dash/<int:projectid>', methods=['GET', 'POST'])
def supervisor_dash_project(projectid):
    #pass  
    if request.method == 'POST':
        worktillprev = request.form['worktillprev']
        worktillnext = request.form['worktillnext']
        #add worktillprev and worktillnext to database for projectid = projectid in url
        project.query.filter_by(projectid=projectid).update(dict(worktillprev=worktillprev, worktillnext=worktillnext))
        db.session.commit()
        remarks = request.form['remarks']
        date = datetime.datetime.now()
        remarksby = session.get('user')
        new_remarks = remarks(projectid=projectid, remarks=remarks, date=date, remarksby=remarksby)
        db.session.add(new_remarks)
        db.session.commit()
        if request.form['submit'] == 'Approve':
            #if supervisorX in database for projectid = projectid in url is username in session then update supervisorX to approved
            if supervisors.query.filter_by(projectid=projectid).first().supervisorX == session.get('user'):
                supervisors.query.filter_by(projectid=projectid).update(dict(supervisorX='approved'))
                db.session.commit()
            #if supervisorY in database for projectid = projectid in url is username in session then update supervisorY to approved
            elif supervisors.query.filter_by(projectid=projectid).first().supervisorY == session.get('user'):
                supervisors.query.filter_by(projectid=projectid).update(dict(supervisorY='approved'))
                db.session.commit()
            #if supervisorZ in database for projectid = projectid in url is username in session then update supervisorZ to approved
            elif supervisors.query.filter_by(projectid=projectid).first().supervisorZ == session.get('user'):
                supervisors.query.filter_by(projectid=projectid).update(dict(supervisorZ='approved'))
                db.session.commit()
        elif request.form['submit'] == 'Reject':
            return 0

@app.route('/committee_dash', methods=['GET', 'POST'])
def committee_dash():
    if User.query.filter_by(username=session.get('user')).first().tier == 3:
        projects = []
        for project in project.query.all():
            if committee.query.filter_by(projectid=project.projectid).first().committeeX == session.get('user') or committee.query.filter_by(projectid=project.projectid).first().committeeY == session.get('user') or committee.query.filter_by(projectid=project.projectid).first().committeeZ == session.get('user') or committee.query.filter_by(projectid=project.projectid).first().committeeA == session.get('user'):
                projects.append(project)
        #pass projects list to committee dashboard template
        return render_template('committee_dashboard.html', projects=projects)
    return redirect(url_for('dashboard'))

@app.route('/committee_dash/<int:projectid>', methods=['GET', 'POST'])
def committee_dash_project(projectid):
    if request.method == 'POST':
        remarks = request.form['remarks']
        date = datetime.datetime.now()
        remarksby = session.get('user')
        new_remarks = remarks(projectid=projectid, remarks=remarks, date=date, remarksby=remarksby)
        db.session.add(new_remarks)
        db.session.commit()
        if request.form['submit'] == 'Approve':
            if committee.query.filter_by(projectid=projectid).first().committeeX == session.get('user'):
                committee.query.filter_by(projectid=projectid).update(dict(committeeX='approved'))
                db.session.commit()
            elif committee.query.filter_by(projectid=projectid).first().committeeY == session.get('user'):
                committee.query.filter_by(projectid=projectid).update(dict(committeeY='approved'))
                db.session.commit()
            elif committee.query.filter_by(projectid=projectid).first().committeeZ == session.get('user'):
                committee.query.filter_by(projectid=projectid).update(dict(committeeZ='approved'))
                db.session.commit()
            elif committee.query.filter_by(projectid=projectid).first().committeeA == session.get('user'):
                committee.query.filter_by(projectid=projectid).update(dict(committeeA='approved'))
                db.session.commit()
        elif request.form['submit'] == 'Reject':
            return 0


#logout route that pops user from session and redirects to login page
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
