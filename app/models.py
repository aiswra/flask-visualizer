from sqlalchemy import Table, Column, Integer, String, Float
from sqlalchemy.orm import mapper
from database import Base,metadata, db_session

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    email = Column(String(120), unique=True)

    def __init__(self, name=None, email=None):
        self.name = name
        self.email = email

    def __repr__(self):
        return f'<User {self.name!r}>'

class Dummy(object):
    query = db_session.query_property()

    def __init__(self, x=None, y=None, group=None):
        self.x = x
        self.y = y
        self.group = group

    def __repr__(self):
        return f'<Dummy {self.x!r}>'

dummys = Table('Dummy', metadata,
    Column('index', Integer, primary_key=True),
    Column('group', String(50), unique=False),
    Column('x', Float, unique=False),
    Column('y', Float, unique=False)
)
mapper(Dummy, dummys)
