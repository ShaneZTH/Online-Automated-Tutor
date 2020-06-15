from flask import Flask, render_template, abort, redirect, url_for, request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
app.config.from_object('config')

bootstrap = Bootstrap(app)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

courses_offered = ['CSE-109', 'CSE-216']

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])


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

        return '<h1>Invalid username or password</h1>'

    return render_template('login.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        login_user(new_user)
        return redirect(url_for('dashboard'))

    return render_template('signup.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.username)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

#
#   Let user choose which specific course to receive help from
#
@app.route('/course/selection')
@login_required
def academic_help():
    return render_template('choose.html', name=current_user.username)
    # return render_template('academic-help.html', name=current_user.username)



# @app.route('/academic/api/v1/set/<course>',methods=['GET','POST'])
# @login_required
# def set_course(course):
#     print(course)
#     # return render_template('dashboard.html', name=current_user.username)
#     return redirect(url_for('dashboard'))

@app.route('/academic/api/v1/<course>/help', methods=['GET','POST'])
@login_required
def handle_course_selection(course):
    global courses_offered
    print("course_help: ", course)
    if course not in courses_offered:
        print("course not found")
        return redirect(url_for('dashboard'))
    else:
        pass
        # TODO: render Q&A html
    return render_template('academic-help.html', name=current_user.username, course=course)

@app.route('/academic/api/v1/academic/help', methods=['POST'])
@login_required
def get_academic_help():
    data = request.json['data']
    if data:
        print(data)
    pass


if __name__ == '__main__':
    app.run(debug=True)
