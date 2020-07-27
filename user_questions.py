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

def query_insert_tutor_answer(course=None, qid=None, answer=None):
    queryStr = ("UPDATE user_questions " +
                " SET has_answered =\"{}\", answer = \"{}\"".format(1, answer) +
                " WHERE course = \"{}\" AND id = \"{}\";".format(course, qid))
    with engine.connect() as conn:
        results = conn.execute(queryStr)


    print('log: Insert with query-[{}]'.format(queryStr))
    return "insert success"


def set_question_status(has_answered=None, has_seen=None, id=None):
    if has_answered is None and has_seen is None: # Validate at least there's one valid parameter
        return
    a_str = None
    s_str = None
    set_str = None
    if has_answered is not None and has_answered > 0:
        a_str = 'has_answered = {}'.format(has_answered)
    elif has_answered == 0: # resetting the question itself as student reject it
        a_str = 'has_answered = {}, answer = Null'.format(has_answered)

    if has_seen is not None and has_seen >= 0:
        s_str = 'has_seen = {}'.format(has_seen)

    print(a_str, ' ', s_str, ' ', set_str)

    if a_str and s_str:
        set_str = a_str + ' , ' + s_str
    else:
        set_str = a_str if a_str else s_str

    queryStr = ("UPDATE user_questions " +
                " SET " + set_str +
                " WHERE id = \"{}\";".format(id))
    with engine.connect() as conn:
        results = conn.execute(queryStr)

    print('log: Updated question_status with query-[{}]'.format(queryStr))
    return "update success"

def query_question_by_id(qid=None):
    print('log: getting info for id-{}'.format(qid))
    queryStr = ("SELECT course, problem, answer " +
                "FROM {} ".format(TABLE_NAME) +
                "WHERE id =\"{}\";".format(qid))
    ret = None
    with engine.connect() as conn:
        results = conn.execute(queryStr)
        for result in results:
            # print(result.items())
            ret = result
            return ret
    return ret


def query_count_course_unanswered(course=None):
    print('log: count_unanswered() - course={}'.format(course))
    queryStr = ("SELECT COUNT(*) " +
                "FROM {} ".format(TABLE_NAME) +
                "WHERE course=\"{}\" AND has_answered=\"{}\";"
                .format(course, 0))
    count = None
    with engine.connect() as conn:
        results = conn.execute(queryStr)
        for result in results:
            count = (result.items()[0])[1]
            print("count-course-unanswered is " + (str)(count))

    return (str)(count)


def query_course_unanswered_posts(course=None):
    print('log: posts_unanswered() - course={}'.format(course))
    queryStr = ("SELECT id, course, problem, timestamp " +
                "FROM {} ".format(TABLE_NAME) +
                "WHERE course=\"{}\" AND has_answered=\"{}\";"
                .format(course, 0))
    posts = []
    with engine.connect() as conn:
        results = conn.execute(queryStr)
        for result in results:
            print("post: " + (str)(result))
            posts.append({"qid": result[0], "post": result[2], "timestamp": result[3]})
    return posts

    pass


def posts_unread(uid=None, course=None):
    print('log: posts_unread() - User-{} course={}'.format(uid, course))
    queryStr = ("SELECT id, course, problem, timestamp " +
                "FROM {} ".format(TABLE_NAME) +
                "WHERE uid=\"{}\" AND course=\"{}\" AND has_answered=\"{}\" AND has_seen=\"{}\";"
                .format(uid, course, 1, 0))
    posts = []
    with engine.connect() as conn:
        results = conn.execute(queryStr)
        for result in results:
            print("posts_unread-result: " + (str)(result))
            posts.append({"qid": result[0], "post": result[2], "timestamp": result[3]})
    return posts


def posts_unanswered(uid=None, course=None):
    print('log: posts_unanswered() - User-{} course={}'.format(uid, course))
    queryStr = ("SELECT id, course, problem, timestamp " +
                "FROM {} ".format(TABLE_NAME) +
                "WHERE uid=\"{}\" AND course=\"{}\" AND has_answered=\"{}\";"
                .format(uid, course, 0))
    posts = []
    with engine.connect() as conn:
        results = conn.execute(queryStr)
        for result in results:
            print("posts_unanswered-result: " + (str)(result))
            posts.append({"qid": result[0], "post": result[2], "timestamp": result[3]})
    return posts


def count_unread(uid=None, course=None):
    print('log: count_unread() - User-{} course={}'.format(uid, course))
    queryStr = ("SELECT COUNT(*) " +
                "FROM {} ".format(TABLE_NAME) +
                "WHERE uid=\"{}\" AND course=\"{}\" AND has_answered=\"{}\" AND has_seen=\"{}\";"
                .format(uid, course, 1, 0))
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
                "WHERE uid=\"{}\" AND course=\"{}\" AND has_answered=\"{}\";"
                .format(uid, course, 0))
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

    queryStr = "INSERT into {} VALUES (\"{}\", \"{}\", \"{}\", \"{}\",\"{}\",\"{}\",\"{}\",\"{}\");" \
        .format(TABLE_NAME, qid, uid, course, problem, current_time, 0, 0, 'NULL')
    print('queryStr: {}'.format(queryStr))

    # VALUES("165441325", "cse109", "What's my name?", "2020-07-12 17:38:12", "0", "1", "NULL")
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
