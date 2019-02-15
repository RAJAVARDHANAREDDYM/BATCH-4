from sqlalchemy import ForeignKey, Integer, String, Column
import os
import sys
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()



class User(Base):
    """docstring for User"""
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(30), nullable=False)
    email = Column(String(20), nullable=False)
    user_pic = Column(String(250), nullable=False)
    role=Column(String(20),nullable=False)

    @property
    def serialize(self):
        return {
            'name': self.name,
            'email': self.email,
            'user_pic': self.user_pic,
            'role' : self.role,
        }















engine = create_engine('sqlite:///questionpaper.db')

Base.metadata.create_all(engine)
