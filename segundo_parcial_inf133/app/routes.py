from flask import render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from models import app, db, Patient, User

@app.route('/users', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        hashed_password = generate_password_hash(password, method='sha256')
        new_user = User(username=username, password=hashed_password, role=role)
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('patients'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/patients')
@login_required
def patients():
    if current_user.role == 'doctor':
        patients = Patient.query.all()
    else:
        patients = Patient.query.all()  # Should filter by team in a real scenario
    return render_template('patients.html', patients=patients)

@app.route('/patients/create', methods=['GET', 'POST'])
@login_required
def create_patient():
    if request.method == 'POST':
        name = request.form['name']
        lastname = request.form['lastname']
        ci = request.form['ci']
        birth_date = request.form['birth_date']
        new_patient = Patient(name=name, lastname=lastname, ci=ci, birth_date=birth_date)
        db.session.add(new_patient)
        db.session.commit()
        return redirect(url_for('patients'))
    return render_template('create_patient.html')

@app.route('/patients/<int:id>/update', methods=['GET', 'POST'])
@login_required
def update_patient(id):
    patient = Patient.query.get_or_404(id)
    if request.method == 'POST':
        patient.name = request.form['name']
        patient.lastname = request.form['lastname']
        patient.ci = request.form['ci']
        patient.birth_date = request.form['birth_date']
        db.session.commit()
        return redirect(url_for('patients'))
    return render_template('update_patient.html', patient=patient)

@app.route('/patients/<int:id>/delete', methods=['POST'])
@login_required
def delete_patient(id):
    patient = Patient.query.get_or_404(id)
    db.session.delete(patient)
    db.session.commit()
    return redirect(url_for('patients'))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
