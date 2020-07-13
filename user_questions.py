from sqlalchemy import create_engine, Column, Integer, String, Text, TIMESTAMP, Boolean
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from datetime import datetime  # to populate TimeStamp
import random
import string

engine = create_engine('sqlite:///user_questions.sqlite', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()
TABLE_NAME = "user_questions"

# FIX: check db to get the exact number
QID_Start = 100

courses_offered = {
    'CSE-109': 'CSE109',
    'CSE-216': 'CSE216'
}
q_str = {
    'p': "problem",
    's': "subject",
    'e': "error"
}

def count_unread(uid=None, course=None):
    print('log: count_unread() - User-{} course={}'.format(uid, course))
    queryStr = ("SELECT COUNT(*) " +
                "FROM {} ".format(TABLE_NAME) +
                "WHERE uid=\"{}\" AND has_answered=\"{}\" AND has_seen=\"{}\";".format(uid, 1, 0))
    count = None
    with engine.connect() as conn:
        results = conn.execute(queryStr)
        for result in results:
            count = (result.items()[0])[1]
            print("unread result is " + (str)(count))

    return (str)(count)

def count_unanswered(uid=None, course=None):
    print('log: count_unanswered() - User-{} course={}'.format(uid, course))
    queryStr = ("SELECT COUNT(*) " +
                "FROM {} ".format(TABLE_NAME) +
                "WHERE uid=\"{}\" AND has_answered=\"{}\";".format(uid, 0))
    count = None
    with engine.connect() as conn:
        results = conn.execute(queryStr)
        for result in results:
            count = (result.items()[0])[1]
            print("unanswered result is " + (str)(count))

    return (str)(count)

# Insert unanswered question into database
def insert_question(uid=None, course=None, problem=None):
    print('log: insert_question() - User-{} course={}, problem={}'.format(uid, course, problem))
    current_time = datetime.now()
    # FIXME: should check db after generated, leave it as now for MVP
    # uid = _get_random_number(11)
    qid = QID_Start + (int)(_get_random_number(4))
    course = course.lower()

    queryStr = "INSERT into {} VALUES (\"{}\", \"{}\", \"{}\", \"{}\",\"{}\",\"{}\",\"{}\");" \
        .format(TABLE_NAME, qid, uid, course, problem, current_time, 0, 0)
    print('queryStr: {}'.format(queryStr))

    # VALUES("165441325", "cse109", "What's my name?", "2020-07-12 17:38:12", "0", "1")
    with engine.connect() as conn:
        results = conn.execute(queryStr)
        print("result is " + (str)(results))

    return results


def _get_random_number(rLength=3):
    return ''.join((random.choice(string.digits) for i in range(rLength)))


# Data Schema for pending questions
class pendingQ(Base):
    __tablename__ = "user_questions"
    id = Column(Integer, primary_key=True, unique=True)
    uid = Column(Integer)
    course = Column(String, default=None)
    problem = Column(String(200), default=None)
    timestamp = Column(TIMESTAMP, default=None)
    has_answered = Column(Boolean, default=False)
    has_seen = Column(Boolean, default=False)

    def __init__(self, _id, uid, course, problem, timestamp, has_answered, has_seen):
        self.id = _id
        self.uid = uid,
        self.course = course
        self.problem = problem
        self.timestamp = timestamp
        self.has_answered = has_answered
        self.has_seen = has_seen

    # Print out the row properly
    def __repr__(self):
        return "<id:{0}, uid:{1}), course:{2}, timestamp:{3} /" \
               "has_answered:{}, has_seen:{}\nproblem:{}>\n\n" \
            .format(self.id, self.uid, self.course, self.timestamp,
                    self.has_answered, self.has_seen, self.problem)


def init_db():
    Base.metadata.create_all(bind=engine)
