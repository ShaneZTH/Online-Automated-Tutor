from flask import Flask, render_template, abort, redirect, url_for, request, jsonify, session
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SelectField, SelectMultipleField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from bs4 import BeautifulSoup as soup
import requests
import json
from knowledge import get_answer
from user_questions import insert_question, count_unanswered, count_unread, posts_unanswered, posts_unread, \
    query_count_course_unanswered, query_course_unanswered_posts, get_question_by_id, set_question_status
import dummy_gen as dg

app = Flask(__name__)
app.config.from_json('config.json', silent=False)

bootstrap = Bootstrap(app)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

courses_offered = {
    # 'CSE-109': 'CSE109',
    # 'CSE-216': 'CSE216',
    # 'ECE-033': 'ECE033',
    # 'ECE-081': 'ECE081'
    'CSE109',
    'CSE216',
    'ECE033',
    'ECE081'
}
major_courses = [
    {'major': 'cse', 'course': '109'},
    {'major': 'cse', 'course': '216'},
    {'major': 'ece', 'course': '033'},
    {'major': 'ece', 'course': '081'}
]
account_types = [('', 'Select your account type'), ('counselor', 'Counselor'),
                 ('student', 'Student'), ('tutor', 'Tutor')]
years = [('', 'Select your year'), ('freshman', 'Freshman'), ('sophomore', 'Sophomore'),
         ('junior', 'Junior'), ('senior', 'Senior'), ('N/A', 'N/A')]
majors = [('', 'Select your major'), ('cse', 'Computer Science Engineering'), ('ece', 'Electrical Engineering'),
          ('N/A', 'N/A')]
courses = [('', 'Select your course(s)'), ('CSE109', 'CSE-109'), ('CSE216', 'CSE-216'), ('N/A', 'N/A')]

######################################################################
'''
    Fetch user's major and available courses
'''


######################################################################
# @login_required
@app.route('/academic/v1/user/major-courses', methods=['GET'])
def user_major_courses():
    uid = current_user.id
    print('uid = ', uid)
    major = _get_user_major(uid)
    filter_courses = list(filter(lambda x: (x['major'] == major), major_courses))

    courses = []
    for c in filter_courses:
        courses.append(c['course'])

    print('\tmajor courses: {}'.format(courses))

    return jsonify({"major": major, "courses": courses})


def _get_user_major(uid):
    user = User.query.filter_by(id=uid).first()
    if user.account_type == 'student' or user.account_type == 'tutor':
        major = user.major
    else:
        major = None

    print('User-{}: [major={}]'.format(uid, major))
    return major


#
# Generate desired amount of users into Users Database
#
def dummy_users_gen(num):
    users = dg.users_gen(num)
    with open('resources/users.txt', 'a+') as out:
        for u in users:
            line = json.dumps(u)
            out.write(line + '\n')
        out.close()

    for u in users:
        new_user = User(id=u[0], username=u[1], email=u[2], password=u[3], account_type=u[4], major=u[5], year=u[6])
        # password = u[-1]
        db.session.add(new_user)
        db.session.commit()
    print("{} users have been imported".format(len(users)))


class User(UserMixin, db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    account_type = db.Column(db.String(30))
    major = db.Column(db.String(30))
    year = db.Column(db.String(15))
    last_login = db.Column(db.String(25))
    courses = db.Column(db.String(30))


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
    year = SelectField(u'Year', validators=[InputRequired()],
                       default='', choices=years)
    major = SelectField(u'Major', validators=[InputRequired()],
                        choices=majors)
    # TODO: use 'selectMutipleField' instead
    course = SelectField(u'Course(s)', validators=[InputRequired()],
                         choices=courses)


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
        print('user: ', user)
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)

                if user.account_type == 'student':
                    major = user.major
                else:
                    major = None
                print('[User:{}] login as {}, [major:{}]\n'.format(user.id, user.account_type, major))
                return redirect(url_for('dashboard', major=major))

        # TODO: "Incorrect Login" handling.
        return '<h1>Invalid username or password</h1>'
    else:
        print('ERROR: login form is invalid ([username:{}]'.format(form.username.data))
        flash_errors(form)

    return render_template('login.html', form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()
    # If user indicated counselor, don't require major and year.
    if (form.account_type.data == 'counselor'):
        form.major.validators = []
        form.year.validators = []
        del form.major
        del form.year
        print('Validators for major & year has been deactivated')
    elif (form.account_type.data == 'tutor'):
        form.year.validators = []
        del form.year
        print('Validators for year has been deactivated')
    elif (form.account_type.data == 'student'):
        form.course.validators = []
        del form.course
        print('Validators for course has been deactivated')

    # print(form.validate())
    # print(form.email.data, form.account_type.data, form.year.data, form.major.data, form.course.data)

    if form.validate_on_submit():
        hashed_password = generate_password_hash(
            form.password.data, method='sha256')
        print('Adding [user:{}] as {}'.format(form.username.data, form.account_type.data))
        # If user indicated counselor or tutor, leave major and year as null.
        if (form.account_type.data == 'counselor'):
            app.logger.info(form.major.data)
            new_user = User(username=form.username.data, email=form.email.data,
                            password=hashed_password, account_type=form.account_type.data)
        elif (form.account_type.data == 'tutor'):
            new_user = User(username=form.username.data, email=form.email.data, password=hashed_password,
                            account_type=form.account_type.data, major=form.major.data, courses=form.course.data)
        else:  # If student, require major and year
            new_user = User(username=form.username.data, email=form.email.data, password=hashed_password,
                            account_type=form.account_type.data, major=form.major.data, year=form.year.data)

        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for('dashboard'))
    else:
        print('ERROR: signup form is invalid ([username:{}]'.format(form.username.data))
        flash_errors(form)
    return render_template('signup.html', form=form)


def flash_errors(form):
    """Flashes form errors"""
    for field, errors in form.errors.items():
        for error in errors:
            print(u"\tError in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), 'error')


@app.route('/dashboard')
@login_required
def dashboard():
    if (current_user.account_type == 'counselor'):
        return render_template('counselor_dashboard.html', name=current_user.username)
    else:
        return render_template('academic_dashboard.html', name=current_user.username)


@app.route('/404')
def error_404():
    return render_template('404.html')


@app.route('/logout')
@login_required
def logout():
    print('User-{} logging out'.format(current_user.id))
    logout_user()

    return redirect(url_for('index'))


# TODO: Hansen's part
#  Router for when student selects emotional support upon logging in.
# @app.route('/emotional_support')
# @login_required
# def emotional_support():
#     if (current_user.account_type == 'counselor'):
#         return redirect(url_for('dashboard'))
#     else:
#         return render_template('student_counseling_dash.html', name=current_user.username)


######################################################################
#
#   Tutors' Functions
#
######################################################################
# Get the total number of unanswered question in the user_questions DB for the specific course
@app.route('/academic/api/v1/tutor/course-unanswered-count', methods=['POST'])
@login_required
def get_course_unanswered_count():
    course = ((str)(request.form['course'])).lower()
    ret = query_count_course_unanswered(course=course)
    print('Log: Course={} has {} unanswered questions'.format(ret, course))
    return ret


# Fetch ALL unanswered question in the user_questions DB for the specific course
@app.route('/academic/api/v1/tutor/course-unanswered-questions', methods=['POST'])
# @login_required
def get_course_unanswered_posts():
    course = ((str)(request.form['course'])).lower()
    ret = query_course_unanswered_posts(course=course)
    print('Log: Course-{}\'s unanswered-questions:\n{}'.format(course, ret))
    js_data = json.dumps(ret)
    return js_data


# Direct TUTOR to the questions page
@app.route('/academic/api/v1/<course>/tutor', methods=['GET', 'POST'])
@login_required
def tutor_course_handler(course):
    if current_user.account_type != 'tutor':
        return redirect(url_for('error_404'))

    print('v1/{}/tutor: redirecting the tutor-main..'.format(course))
    return render_template("tutor-main-v1.html", name=current_user.username, course=course)


# Tutor's Academic Dashboard Redirection
@app.route('/academic_dash')
@login_required
def academic_dash():
    if (current_user.account_type == 'counselor'):
        return redirect(url_for('dashboard'))
    else:
        if (current_user.account_type == 'tutor'):
            # return render_template('tutor_academic_dash.html', name=current_user.username)
            return redirect(url_for('tutor_dash_redirect', name=current_user.username))
        elif (current_user.account_type == 'student'):
            # return render_template('student_academic_dash.html', name=current_user.username)
            return redirect(url_for('student_dash_redirect', name=current_user.username))
        else:
            print('ERROR: encounter errors when redirecting user with [type:{}]'.format(current_user.account_type))
            return redirect(url_for('error_404'))


# Go to TUTOR Dashboard
@app.route('/tutor/academic/dashboard')
@login_required
def tutor_dash_redirect():
    return render_template('tutor_academic_dash.html', name=current_user.username)


######################################################################
#
#   Students' Functions
#
######################################################################
# Go to STUDENT Dashboard
@app.route('/student/academic/dashboard')
@login_required
def student_dash_redirect():
    return render_template('student_academic_dash.html', name=current_user.username)


# Direct STUDENT to the Q&A page, if & only if the course is offered
@app.route('/academic/api/v1/<course>/help', methods=['GET', 'POST'])
@login_required
def student_course_handler(course):
    if current_user.account_type == 'student':
        global courses_offered

        print('[course-{}] getting help'.format(course))
        if course not in courses_offered:
            print("course not found")
            return redirect(url_for('error_404'))
            # TODO: Error handling should be improve

        return render_template("academic-main-v2.html", name=current_user.username, course=course)

    else:
        return redirect(url_for('error_404'))


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


# Get answer for STUDENT's question
@app.route('/academic/api/v1/answer', methods=['POST'])
@login_required
def get_answer_handler():
    # course = courses_offered[request.form['course']]

    course = ((str)(request.form['course'])).upper()
    question = request.form['question']
    print('Getting answer for [course:{}]\n\tQuestion: {}'.format(course, question))
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
        print('Log: get_answer_handler() - knowledge retrieved: {}'.format(answer))
        if answer:
            return answer
        else:
            insert_question(uid=current_user.id, course=course, problem=question)
            return 'Sorry, answer is not available. Please wait for a tutor to answer.'
    else:
        # TODO: Error handling should be improve
        # TODO: log current action
        print('ERROR: [course:{}] does not exist in the system'.format(course))
        return "Some errors occurred!"


@app.route('/academic/api/v1/count-unanswered', methods=['POST'])
# @login_required
def get_unanswered_count():
    uid = current_user.id
    course = ((str)(request.form['course'])).lower()
    ret = count_unanswered(uid=uid, course=course)
    print('Log: User-{} has {} unanswered questions for [course={}]'.format(uid, ret, course))
    return ret


@app.route('/academic/api/v1/count-unread', methods=['POST'])
# @login_required
def get_unread_count():
    uid = current_user.id
    course = ((str)(request.form['course'])).lower()
    ret = count_unread(uid=uid, course=course)
    print('Log: User-{} has {} unread questions for [course={}]'.format(uid, ret, course))
    return ret


@app.route('/academic/api/v1/posts/unanswered', methods=['POST'])
# @login_required
def get_unanswered_posts():
    uid = current_user.id
    course = ((str)(request.form['course'])).lower()
    ret = posts_unanswered(uid=uid, course=course)
    print('Log: User-{}\'s unanswered-posts for [course={}]:\n{}'.format(uid, course, ret))
    js_data = json.dumps(ret)
    return js_data


@app.route('/academic/api/v1/posts/unread', methods=['POST'])
# @login_required
def get_unread_posts():
    uid = current_user.id
    course = ((str)(request.form['course'])).lower()
    ret = posts_unread(uid=uid, course=course)
    print('Log: User-{}\'s unread-posts for [course={}]:\n{}'.format(uid, course, ret))
    js_data = json.dumps(ret)
    return js_data


@app.route('/academic/api/v1/set/current-qid', methods=['POST'])
@login_required
def set_current_qid():
    qid = (int)(request.form['qid'])
    session['qid'] = qid
    print('Log: User-{}\'s current qid is set as {}'.format(current_user.id, qid))
    return ("Current qid is set as " + (str)(qid))


# else:
#     # TODO: Improve error handling
#     abort(404, description="Resource not found")

@app.route('/academic/api/v1/post/unread-feedback', methods=['POST'])
@login_required
def unread_post_feedback_handler():
    if 'qid' in session:
        feedback = request.form['feedback'].lower().strip()
        print('Log: User-{}\'s feedback for qid-{} is {}'.format(current_user.id, session['qid'], feedback))

        print('[{}]'.format(feedback))
        if feedback == 'satisfied':
            # TODO: implement this query statement in user-question.py
            print(set_question_status(has_seen=1, id=session['qid']))
            data = get_question_by_id(qid=session['qid'])
            course = data[0]
            question = data[1]
            answer = data[2]

            new_q = {
                'course': course,
                'question': question,
                'answer': answer
            }
            j_str = json.dumps(new_q)+',\n'
            print(j_str)
            _write_to_file(fname='new_knowledge.txt', type='a+', content=j_str)
        else:
            set_question_status(has_answered=0,id=session['qid'])
            print(" log: Question-{}'s answer and status has been reset".format(session['qid']))
            pass

        return "Feedback has been successfully handled"
    else:
        print('Resource[\'qid\'] not found')
        # TODO: Improve error handling
        abort(404, description="Resource['qid'] not found")

def _write_to_file(fname=None, type=None, content=None):
    with open(fname, type) as f:
        f.write(content)

# @app.route('/academic/api/v1/major-courses', methods=['POST'])
# @login_required
# def get_major_courses():
#     # major = request.data['major']
#     # print(major)
#     js_data = request.get_json()
#     major = (str)(js_data["major"])
#     matched_data = list(filter(lambda c: c['major'] == major, major_courses))
#     res = []
#     for d in matched_data:
#         res.append(d['course'])
#
#     return jsonify({"courses": res})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
