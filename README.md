# Online-Automated-Tutor

This is a summer research project where the goal is to create an automated tutor and emotional support platform for students.

## Automated Tutor

The automated tutor will receive questions from students and use machine learning to find a past Piazza post that answers the question.

## Emotional Support Platform

The emotional support platform will help students during times where their mental health may be strained.
This platform will have counselors regularly log in, directing them to a dashboard.
On the dashboard, randomly allocated distress messages from students will be displayed, one at a time.
The counselors must respond to a message to see the next one.
Once the counselors respond, the message/response pair is stored in the database and archived in the counselor and student's message history.

## Tools/Dependencies Used

- [Flask](https://flask.palletsprojects.com/en/1.1.x/)
- [Flask-BootStrap](https://pythonhosted.org/Flask-Bootstrap/)
- [Flask-WTF](https://flask-wtf.readthedocs.io/en/stable/)
- [Flask-SQLAlchemy](https://flask-sqlalchemy.palletsprojects.com/en/2.x/)
- [Flask-Login](https://flask-login.readthedocs.io/en/latest/)
- [Werkzeug-security](https://www.programcreek.com/python/example/82817/werkzeug.security.generate_password_hash)
- [WTForms](https://wtforms.readthedocs.io/en/2.3.x/)

## Run the App

- Manually install all dependencies through pip, or use the bash script provided (run "sh install_deps.sh").
- If db.sqlite does not exist, run Python. Type the following in the Python console:
  `from app import db`
  `db.create_all()`
- Run "python app.py" and visit localhost in the web browser.

