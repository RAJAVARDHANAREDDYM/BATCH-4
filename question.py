import os
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

Base = declarative_base()

class Question(Base):
		__tablename__='manager'
		id = Column(Integer,primary_key=True)
		name = Column(String(500),nullable=False)
		level = Column(String(500))
		co = Column(String(500))
		unit = Column(String(500))

		@property
		def serialize(self):
			return{
			'name':self.name,
			'id':self.id,
			'level':self.level,
			'co':self.co,
			'unit':self.unit
			}

engin = create_engine('sqlite:///question.db')
Base.metadata.create_all(engin)

