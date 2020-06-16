from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///QnA.sqlite', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()

courses_offered = {
    'CSE-109': 'CSE109',
    'CSE-216': 'CSE216'
}
q_str = {
    'p': "problem",
    's': "subject",
    'e': "error"
}


# Data model for CSE109
class CSE109(Base):
    __tablename__ = 'cse109'
    id = Column(Integer, primary_key=True, unique=True)
    problem = Column(String(50), default=None)
    subject = Column(String(50), default=None)
    error = Column(String(100), default=None)
    answer = Column(String(5000), nullable=False)

    def __init__(self, id, problem, subject, error, answer):
        self.id = id
        self.problem = problem
        self.subject = subject
        self.error = error
        self.answer = answer

    # Print out the row properly
    def __repr__(self):
        return "<Problem{0}: {1})>\n Subject: {2}\n Error: {3}\n Answer: {4}\n\n" \
            .format(self.id, self.problem, self.subject, self.error, self.answer)


# Data model for CSE216
class CSE216(Base):
    __tablename__ = 'cse216'
    id = Column(Integer, primary_key=True, unique=True)
    problem = Column(String(50), default=None)
    subject = Column(String(50), default=None)
    error = Column(String(100), default=None)
    answer = Column(String(5000), nullable=False)

    def __init__(self, id, problem, subject, error, answer):
        self.id = id
        self.problem = problem
        self.subject = subject
        self.error = error
        self.answer = answer

    # Print out the row properly
    def __repr__(self):
        return "<Problem{0}: {1})>\n Subject: {2}\n Error: {3}\n Answer: {4}\n\n" \
            .format(self.id, self.problem, self.subject, self.error, self.answer)


# Prepare problems, subjects, errors into proper sql statement
def __prepare_query(problems, subjects, errors):
    p = s = e = ""
    if problems:
        if len(problems) > 1:
            for problem in problems[:-1]:
                p += "{0} like '%{1}%' AND ".format(q_str['p'], problem)
            p += "{0} like '%{1}%'".format(q_str['p'], problems[-1])
        else:
            p = "{0} is '{1}'".format(q_str['p'], problems[0])
    else:
        p = ""

    if subjects:
        if len(subjects) > 1:
            for subject in subjects[:-1]:
                s += "{0} like '%{1}%' AND ".format(q_str['s'], subject)
            s += "{0} like '%{1}%'".format(q_str['s'], subjects[-1])
        else:
            s = "{0} is '{1}'".format(q_str['s'], subjects[0])
    else:
        s = ""

    if errors:
        if len(errors) > 1:
            for error in errors[:-1]:
                e += "{0} like '%{1}%' AND ".format(q_str['e'], error)
            e += "{0} like '%{1}%'".format(q_str['e'], errors[-1])
        else:
            e = "{0} is '{1}'".format(q_str['e'], errors[0])
    else:
        e = ""

    if p:
        if s:
            s = " AND " + s
        if e:
            e = " AND " + e
    elif s:
        if e:
            e = " AND " + e

    print('prepared query statement: ', p, s, e)
    return p, s, e


# Connect with database to retrieve the answer
def get_answer(course=None, problems=None, subjects=None, errors=None):
    print("Connecting DB to retrieve answers...")

    # Check parameters to avoid ALL null values
    if problems or subjects or errors:
        # Prepare the query statement
        p, s, e = __prepare_query(problems, subjects, errors)
        querystr = "SELECT answer " \
                   "FROM {0} " \
                   "WHERE {1} {2} {3};" \
            .format(course, p.strip(), s.strip(), e.strip())
        print('query_str: ', querystr)
    else:
        # TODO: log current action
        return "Not a valid question [doesn't match any existing keyword]"

    # Connect the database
    with engine.connect() as conn:
        results = conn.execute(querystr)
        ret: str = ""
        # FIXME: cannot retrieve text/response longer than 350 characters
        for row in results:
            print("LEN: ", len(str(row)))
            tmp = str(row).strip()[2:-3]
            ret = ret + tmp
        # TODO: log current action

    return ret if ret else "Answer not found"


def init_db():
    Base.metadata.create_all(bind=engine)


# print("ANSWER: ", get_answer('cse109', ['work'], ['fork()'], ''))
# __prepare_query( ['include', 'edit'],'','')
