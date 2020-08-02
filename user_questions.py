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
USER_QUESTIONS = "user_questions"
TUTORS_QUESTIONS = "tutors_questions"

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
tutors = {'97531419831', '97531419832', '97531419834'}
tutors_questions_count = {
    'cse109': {

    }, 'cse216': {

    }
}

def resultproxy_handler(resultproxy=None):
    d, a = {}, []
    for rowproxy in resultproxy:
        # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
        for column, value in rowproxy.items():
            # build up the dictionary
            d = {**d, **{column: value}}
        a.append(d)
    return a
######################################################################
# Update the number of tutors we currently have
#   and
# Initialize the tutors_questions_counts
def initialize_count():
    for key in tutors_questions_count.keys():
        for t in tutors:
            tutors_questions_count[key].setdefault(t, 0)
    print("Counts are initialized as:\n\t{}".format(tutors_questions_count))
    return

# Find the tutor with the least number of questions assigned
def find_next_tutor(course=None):
    curr_min = 1000
    curr_tut = None
    print('log: find_next_tutor() called with course-{}'.format(course))
    print(len(tutors_questions_count[course]))
    print(tutors_questions_count)
    for key in tutors_questions_count[course].keys():
        print(tutors_questions_count[course][key], str(curr_min))
        if tutors_questions_count[course][key] < curr_min:
            curr_tut = key
            curr_min = tutors_questions_count[course][key]

    print('\ttutor-{} has the least number of questions'.format(curr_tut))
    return curr_tut

def count_all_tutors_questions():
    print('log: count_all_tutors_questions()')
    queryStr = ("SELECT t_id, course, count() as count " +
                "FROM {} ".format(TUTORS_QUESTIONS) +
                "WHERE has_answered = \"{}\" ".format(0) +
                "GROUP BY course, t_id")
    initialize_count()
    with engine.connect() as conn:
        results = conn.execute(queryStr)
        for result in results:
            # print(result.items())
            t_id = (result.items()[0])[1]
            course = (result.items()[1])[1]
            count = (result.items()[2])[1]
            tutors_questions_count[course][str(t_id)] = count
            print(t_id, course, count)
    print('\t Count is done with result:\n\t\t{}'.format(tutors_questions_count))

    return 'Count-All Success'


# def count_all_tutors_questions(course=None):
#     print('log: count_all_tutors_questions() - course={}'.format(course))
#     queryStr = ("SELECT t_id, count()" +
#                 "FROM {} ".format(TUTORS_QUESTIONS) +
#                 "WHERE has_answered = \"{}\" AND course = \"{}\""
#                 .format(0, course))
#     with engine.connect() as conn:
#         results = conn.execute(queryStr)
#         for result in results:
#             t_id, count = (result.items()[0])
#             print(t_id, count)
#     # TODO: find a way to store data
#     #   NOT DONE YET, IN PROGRESS
#
#     pass

def count_tutor_questions(t_id=None, course=None):
    print('log: count_tutor_questions() - t_id-{} course={}'.format(t_id, course))
    queryStr = ("SELECT COUNT(*) " +
                "FROM {} ".format(TUTORS_QUESTIONS) +
                "WHERE t_id=\"{}\" AND course=\"{}\" AND has_answered=\"{}\";"
                .format(t_id, course, 0, 0))
    print('\tQuery: ' + queryStr)
    count = None
    with engine.connect() as conn:
        results = conn.execute(queryStr)
        for result in results:
            count = (result.items()[0])[1]
            print("\t query result is " + (str)(count))
    return (str)(count)

    pass

def assign_tutor_question(t_id=None, course=None, q_id=None):
    print('log: assign_tutor_question() - Tutor-{}, q_id-{}, course={}'
          .format(t_id, q_id, course))

    queryStr = "INSERT into {} VALUES (\"{}\", \"{}\", \"{}\",\"{}\");" \
        .format(TUTORS_QUESTIONS, t_id, q_id, course, 0)
    print('\tqueryStr: {}'.format(queryStr))

    with engine.connect() as conn:
        results = conn.execute(queryStr)
        return "Assign Success"


    return "Assign Failed"

def query_tutor_questions(t_id=None, course=None):
    print('log: query_tutor_questions() - TUTOR-{}, COURSE-{}'.format(t_id, course))
    queryStr = (" SELECT U.id, U.course, U.problem, U.timestamp " +
                " FROM user_questions as U  JOIN tutors_questions as T on U.id = T.q_id ".format(USER_QUESTIONS) +
                " WHERE T.has_answered={} AND T.t_id={} AND U.course=\"{}\" ".format(0, t_id, course) +
                " ORDER by U.timestamp;")
    print('\tQuery: ' + queryStr)
    posts = []
    with engine.connect() as conn:
        results = conn.execute(queryStr)
        for result in results:
            print("post: " + (str)(result))
            posts.append({"qid": result[0], "post": result[2], "timestamp": result[3]})
    return posts
    pass

# Data Model for tutors_questions
class tutors_question(Base):
    __tablename__ = "tutors_questions"
    t_id = Column(Integer, primary_key=True, nullable=False)
    q_id = Column(Integer, primary_key=True, unique=True, nullable=False)
    course = Column(String(50), default=None, nullable=False)

    def __init__(self, t_id, q_id, course):
        t_id = t_id
        q_id = q_id
        course = course

    def __repr__(self):
        return "<t_id-{}, q_id-{}, course-{}\n>".format(self.t_id, self.q_id, self.course)


######################################################################
def insert_tutor_answer(course=None, qid=None, answer=None):
    queryStr = ("UPDATE user_questions " +
                " SET has_answered =\"{}\", answer = \"{}\"".format(1, answer) +
                " WHERE course = \"{}\" AND id = \"{}\";".format(course, qid))

    with engine.connect() as conn:
        results = conn.execute(queryStr)
    print('log: Insert with query-[{}]'.format(queryStr))

    # queryStr_tutor = ("UPDATE tutors_questions " +
    #                   " SET has_answered=\"1\"" +
    #                   " WHERE q_id = \"{}\";".format(id))
    # with engine.connect as conn:
    #     results = conn.execute(queryStr_tutor)

    # print('log: Updated tutors_questions with query-[{}]'.format(queryStr_tutor))

    return "insert success"



def set_question_status(has_answered=None, has_seen=None, id=None):
    print('Log: set_question_status({},{},{}) is called'.format(has_answered, has_seen, id))
    if has_answered is None and has_seen is None: # Validate at least there's one valid parameter
        return
    a_str = None
    s_str = None
    set_str = None
    if has_answered is not None and has_answered > 0:
        a_str = 'has_answered = {}'.format(has_answered)
        # TODO: update tutors_questions table as well
        # Update tutors-questions
        queryStr_tutor = ("UPDATE tutors_questions " +
                    " SET has_answered=1" +
                    " WHERE q_id = \"{}\";".format(id))
        with engine.connect() as conn:
            results = conn.execute(queryStr_tutor)
            conn.close()
        print('log: Updated tutors_questions with query-[{}]'.format(queryStr_tutor))

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
                "FROM {} ".format(USER_QUESTIONS) +
                "WHERE id =\"{}\";".format(qid))
    ret = None
    with engine.connect() as conn:
        results = conn.execute(queryStr)
        for result in results:
            ret = result
            return ret
    return ret

def query_count_course_unanswered(course=None):
    print('log: count_unanswered() - course={}'.format(course))
    queryStr = ("SELECT COUNT(*) " +
                "FROM {} ".format(USER_QUESTIONS) +
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
                "FROM {} ".format(USER_QUESTIONS) +
                "WHERE course=\"{}\" AND has_answered=\"{}\";"
                .format(course, 0))
    posts = []
    with engine.connect() as conn:
        results = conn.execute(queryStr)
        for result in results:
            print("posts_unanswered_result: " + (str)(result))
            posts.append({"qid": result[0], "post": result[2], "timestamp": result[3]})
    return posts

def posts_unread(uid=None, course=None):
    print('log: posts_unread() - User-{} course={}'.format(uid, course))
    queryStr = ("SELECT id, course, problem, timestamp " +
                "FROM {} ".format(USER_QUESTIONS) +
                "WHERE uid=\"{}\" AND course=\"{}\" AND has_answered=\"{}\" AND has_seen=\"{}\";"
                .format(uid, course, 1, 0))
    posts = []
    with engine.connect() as conn:
        results = conn.execute(queryStr)
        for result in results:
            print("\tposts_unread-result: " + (str)(result))
            posts.append({"qid": result[0], "post": result[2], "timestamp": result[3]})
    return posts


def posts_unanswered(uid=None, course=None):
    print('log: posts_unanswered() - User-{} course={}'.format(uid, course))
    queryStr = ("SELECT id, course, problem, timestamp " +
                "FROM {} ".format(USER_QUESTIONS) +
                "WHERE uid=\"{}\" AND course=\"{}\" AND has_answered=\"{}\";"
                .format(uid, course, 0))
    posts = []
    with engine.connect() as conn:
        results = conn.execute(queryStr)
        for result in results:
            print("\tposts_unanswered-result: " + (str)(result))
            posts.append({"qid": result[0], "post": result[2], "timestamp": result[3]})
    return posts


def count_unread(uid=None, course=None):
    print('log: count_unread() - User-{} course={}'.format(uid, course))
    queryStr = ("SELECT COUNT(*) " +
                "FROM {} ".format(USER_QUESTIONS) +
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
    print('Log: count_unanswered() - User-{} course={}'.format(uid, course))
    queryStr = ("SELECT COUNT(*) " +
                "FROM {} ".format(USER_QUESTIONS) +
                "WHERE uid=\"{}\" AND course=\"{}\" AND has_answered=\"{}\";"
                .format(uid, course, 0))
    count = None
    with engine.connect() as conn:
        results = conn.execute(queryStr)
        for result in results:
            count = (result.items()[0])[1]
            print("\tunanswered result is " + (str)(count))

    return (str)(count)


# Insert unanswered question into database
def insert_question(uid=None, course=None, problem=None):
    print('Log: insert_question() - User-{} course={}, problem={}'.format(uid, course, problem))
    current_time = datetime.now()
    # FIXME: should check db after generated, leave it as now for MVP
    # uid = _get_random_number(11)
    qid = QID_Start + (int)(_get_random_number(4))
    course = course.lower()

    queryStr = "INSERT into {} VALUES (\"{}\", \"{}\", \"{}\", \"{}\",\"{}\",\"{}\",\"{}\",\"{}\");" \
        .format(USER_QUESTIONS, qid, uid, course, problem, current_time, 0, 0, 'NULL')
    print('queryStr: {}'.format(queryStr))

    # VALUES("165441325", "cse109", "What's my name?", "2020-07-12 17:38:12", "0", "1", "NULL")
    with engine.connect() as conn:
        results = conn.execute(queryStr)
        print("\tresult is " + (str)(results))
        conn.close()

    count_all_tutors_questions() # Refresh the count status
    tutor = find_next_tutor(course)
    if tutor:
        assign_tutor_question(tutor, course, qid)
        return results
    else:
        return "Insertion Failed: cannot find a tutor to answer questions"


def _get_random_number(rLength=3):
    return ''.join((random.choice(string.digits) for i in range(rLength)))

# Data Schema for user_questions
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
    count_all_tutors_questions()
