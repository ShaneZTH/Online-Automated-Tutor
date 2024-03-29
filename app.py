from flask import Flask, render_template, abort, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_restful import reqparse
from bs4 import BeautifulSoup as soup
import requests
import json
from database import get_answer

app = Flask(__name__)
app.config.from_json('config.json', silent=False)

bootstrap = Bootstrap(app)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

courses_offered = {
    'CSE-109': 'CSE109',
    'CSE-216': 'CSE216'
}
account_types = [('', ''), ('counselor', 'Counselor'),
                 ('student', 'Student'), ('tutor', 'Tutor')]
years = [('', 'Select your year'), ('freshman', 'Freshman'), ('sophomore',
                                                              'Sophomore'), ('junior', 'Junior'), ('senior', 'Senior'),
         ('N/A', 'N/A')]


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    account_type = db.Column(db.String(30))
    major = db.Column(db.String(30))
    year = db.Column(db.String(15))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[
        InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[
        InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('Remember me')


class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(
        message='Invalid email'), Length(max=50)])
    username = StringField('Username', validators=[
        InputRequired(), Length(min=4, max=15)])
    password = PasswordField('Password', validators=[
        InputRequired(), Length(min=8, max=80)])
    account_type = SelectField(u'I am a...', choices=account_types, validators=[
        InputRequired()], default='')
    major = StringField('Major', validators=[InputRequired()], render_kw={
        "placeholder": "Enter your Major..."})
    year = SelectField(u'Year', validators=[
        InputRequired()], default='', choices=years)


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                return redirect(url_for('dashboard'))

        # TODO: "Incorrect Login" handling.
        return '<h1>Invalid username or password</h1>'

    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    # If user indicated counselor, don't require major and year.
    if (form.account_type.data == 'counselor'):
        form.major.validators = []
        form.year.validators = []
    if form.validate_on_submit():
        # If user indicated counselor, leave major and year as null.
        if (form.account_type.data == 'counselor'):
            hashed_password = generate_password_hash(
                form.password.data, method='sha256')
            app.logger.info(form.major.data)
            new_user = User(username=form.username.data, email=form.email.data,
                            password=hashed_password, account_type=form.account_type.data)
            db.session.add(new_user)
            db.session.commit()
        else:  # If not counselor, require major and year
            hashed_password = generate_password_hash(
                form.password.data, method='sha256')
            new_user = User(username=form.username.data, email=form.email.data, password=hashed_password,
                            account_type=form.account_type.data, major=form.major.data, year=form.year.data)
            db.session.add(new_user)
            db.session.commit()

        login_user(new_user)
        return redirect(url_for('dashboard'))
    return render_template('signup.html', form=form)


@app.route('/dashboard')
@login_required
def dashboard():
    if (current_user.account_type == 'counselor'):
        return render_template('counselor_dashboard.html', name=current_user.username)
    else:
        return render_template('student_dash_init.html', name=current_user.username)

@app.route('/404')
def error_404():
    return render_template('404.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

# TODO: Hansen's part
#  Router for when student selects emotional support upon logging in.
@app.route('/emotional_support')
@login_required
def emotional_support():
    if(current_user.account_type == 'counselor'):
        return redirect(url_for('dashboard'))
    else:
        return render_template('student_counseling_dash.html', name=current_user.username)

# TODO:Taohan's part
#  Router for when student selects academic tutor upon logging in.
@app.route('/academic_tutor')
@login_required
def academic_tutor():
    if(current_user.account_type == 'counselor'):
        return redirect(url_for('dashboard'))
    else:
        return render_template('student_academic_dash.html', name=current_user.username)

#
#   Let user choose which specific course to receive help from
#
@app.route('/student/academic/dashboard')
@login_required
def academic_help():
    return render_template('student_academic_dash.html', name=current_user.username)


# Direct user to the Q&A page, if & only if the course is offered
@app.route('/academic/api/v1/<course>/help', methods=['GET', 'POST'])
@login_required
def handle_course_selection(course):
    global courses_offered

    # TODO: log current action
    print("course_help: ", course)
    if course not in courses_offered:
        print("course not found")
        return redirect(url_for('error_404'))
        # TODO: Error handling should be improve

    return render_template("academic-main-v2.html", name=current_user.username, course=course)


# Extract values from wit response
def parse_arg_from_wit(response):
    r_json = json.loads(response)
    entities = r_json['entities']
    p_content = []
    s_content = []
    e_content = []
    # TODO: add confidence check before appending
    if 'problem:problem' in entities:
        problems = entities['problem:problem']
        for problem in problems:
            p_content.append(problem['value'])
    if 'subject:subject' in entities:
        subjects = entities['subject:subject']
        for subject in subjects:
            s_content.append(subject['value'])
    if 'error:error' in entities:
        errors = entities['error:error']
        for error in errors:
            e_content.append(error['value'])
    # print(p_content, s_content, e_content)
    return p_content, s_content, e_content


@app.route('/academic/api/v1/answer', methods=['POST'])
@login_required
def get_answer_handler():
    course = courses_offered[request.form['course']]
    question = request.form['question']

    WIT = app.config['WIT_APPS']
    if course in WIT:
        token = WIT[course]['Server_Access_Token']
        v = WIT[course]['v']
        url = 'https://api.wit.ai/message?v={0}&q={1}'.format(v, question)
        headers = {
            "Authorization": "Bearer " + token
        }
        response = requests.get(url=url, headers=headers)

        problems, subjects, errors = parse_arg_from_wit(response.text)
        answer = get_answer(course, problems, subjects, errors)
        print(answer)
        return answer
    else:
        # TODO: Error handling should be improve
        # TODO: log current action
        return "Some errors occurred!"

    return course + " : " + question_content


if __name__ == '__main__':
    app.run(debug=True, port=5000)
