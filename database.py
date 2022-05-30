from numpy import genfromtxt
from sqlalchemy.engine import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, ForeignKey, Integer, String, Float, DateTime, null
from datetime import datetime 



Base = declarative_base()

def Load_Data(file_name):
    data = genfromtxt(file_name, delimiter=',', skip_header=1, converters={0: lambda s: str(s)})
    return data.tolist()


class Question(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False, unique=True)
    op1 = Column(String(255), nullable=False)
    op2 = Column(String(255), nullable=False)
    op3 = Column(String(255), nullable=False)
    op4 = Column(String(255), nullable=False)
    ans = Column(String(255), nullable=False)
    category = Column(String(255),nullable=False)
    added_on = Column(DateTime, default=datetime.now)

    def __str__(self):
        return self.title

class User(Base):
    __tablename__="users"
    id =Column(Integer,primary_key =True)
    email = Column(String(200), nullable=False, unique=True)
    name = Column(String(200), nullable=False, unique=True)
    password = Column(String(200), nullable=False, unique=True)
    added_on = Column(DateTime,default=datetime.now)

class Score(Base):
    __tablename__= "Scores"
    id = Column(Integer,primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id')) 
    score = Column(Integer,default=0)
    created_on=Column(DateTime, default=datetime.now)

    def __str__(self):
        return self.title          
   

if __name__ == "__main__":
    engine = create_engine("sqlite:///db.sqlite",echo=True)
    Base.metadata.create_all(engine)
   