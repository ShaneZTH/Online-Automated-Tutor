from sqlalchemy import create_engine, Column, Integer, String, Text, TIMESTAMP, Boolean
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('sqlite:///pendingQ.sqlite', convert_unicode=True)
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

# Data Schema for pending questions
class pendingQ(Base):
    __tablename__ = "pending_q"
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

