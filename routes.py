from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash

from models import db, User, Job, Application, Company

bp = Blueprint('main', __name__)


@bp.route('/')
def home():
    return render_template('home.html')


@bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        existing_user = User.query.filter_by(email=request.form['email']).first()

        if existing_user:
            flash("Email already registered.")
            return redirect(url_for('main.signup'))

        user = User(
            name=request.form['name'],
            email=request.form['email'],
            password=generate_password_hash(request.form['password']),
            role='student'
        )

        db.session.add(user)
        db.session.commit()

        flash("Signup successful!")
        return redirect(url_for('main.login'))

    return render_template('signup.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()

        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            flash("Login successful!")
            return redirect(url_for('main.dashboard'))

        flash("Invalid email or password")

    return render_template('login.html')


@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))


@bp.route('/dashboard')
@login_required
def dashboard():
    jobs = Job.query.all()

    applied_jobs = [
        application.job_id for application in Application.query.filter_by(user_id=current_user.id).all()
    ]

    return render_template('dashboard.html', jobs=jobs, applied_jobs=applied_jobs)


@bp.route('/apply/<int:job_id>')
@login_required
def apply(job_id):
    existing = Application.query.filter_by(
        user_id=current_user.id,
        job_id=job_id
    ).first()

    if existing:
        flash("You have already applied for this job!")
        return redirect(url_for('main.dashboard'))

    application = Application(
        user_id=current_user.id,
        job_id=job_id
    )

    db.session.add(application)
    db.session.commit()

    flash("Applied successfully!")
    return redirect(url_for('main.dashboard'))


@bp.route('/add_job', methods=['GET', 'POST'])
@login_required
def add_job():
    if current_user.role != 'admin':
        return "Access denied", 403

    if request.method == 'POST':
        job = Job(
            title=request.form['title'],
            description=request.form['description'],
            company_id=1
        )

        db.session.add(job)
        db.session.commit()

        flash("Job added successfully!")
        return redirect(url_for('main.dashboard'))

    return render_template('add_job.html')


@bp.route('/delete_job/<int:job_id>')
@login_required
def delete_job(job_id):
    if current_user.role != 'admin':
        return "Access denied", 403

    job = Job.query.get(job_id)

    if job:
        Application.query.filter_by(job_id=job_id).delete()
        db.session.delete(job)
        db.session.commit()

        flash("Job deleted successfully!")

    return redirect(url_for('main.dashboard'))