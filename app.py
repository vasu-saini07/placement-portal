from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from models import db, User, Company, Job, Application

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret123'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db.init_app(app)


from flask_login import UserMixin
from flask_login import LoginManager, login_user, logout_user, login_required, current_user

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

from flask import render_template, request, redirect, flash

@app.route('/')
def home():
    return render_template('home.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        user = User(
            name=request.form['name'],
            email=request.form['email'],
            password=generate_password_hash(request.form['password']),
            role='student'
        )
        db.session.add(user)
        db.session.commit()
        flash("Signup successful! Please login.")
        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form['email']).first()

        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            flash("Login successful!")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid email or password")

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/dashboard')
@login_required
def dashboard():
    jobs = Job.query.all()

    applied_jobs = [
        app.job_id for app in Application.query.filter_by(user_id=current_user.id).all()
    ]

    return render_template('dashboard.html', jobs=jobs, applied_jobs=applied_jobs)


@app.route('/apply/<int:job_id>')
@login_required
def apply(job_id):

    existing = Application.query.filter_by(
        user_id=current_user.id,
        job_id=job_id
    ).first()

    if existing:
        flash("You have already applied for this job!")
        return redirect(url_for('dashboard'))

    application = Application(
        user_id=current_user.id,
        job_id=job_id
    )

    db.session.add(application)
    db.session.commit()

    flash("Applied successfully!")
    return redirect(url_for('dashboard'))


@app.route('/add_job', methods=['GET', 'POST'])
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
        return redirect(url_for('dashboard'))

    return render_template('add_job.html')


@app.route('/delete_job/<int:job_id>')
@login_required
def delete_job(job_id):
    if current_user.role != 'admin':
        return "Access denied", 403

    job = Job.query.get(job_id)

    if job:
        db.session.delete(job)
        db.session.commit()
        flash("Job deleted successfully!")

    return redirect(url_for('dashboard'))




if __name__ == '__main__':
    app.run(debug=True)
