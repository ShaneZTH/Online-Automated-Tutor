from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///QnA.sqlite', convert_unicode=True)
db_session = scoped_session(sessionmaker(autocommit=False,
                                         autoflush=False,
                                         bind=engine))
Base = declarative_base()
Base.query = db_session.query_property()


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

def get_answer(course=None, problems=None, subjects=None, errors=None):
    pass


# def init_db():
#     # import all modules here that might define models so that
#     # they will be registered properly on the metadata.  Otherwise
#     # you will have to import them first before calling init_db()
#     # import yourapplication.models
#     Base.metadata.create_all(bind=engine)
