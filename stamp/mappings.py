##############################
#
#    Database mappings for
#    a workday
#
##############################

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
engine = create_engine('sqlite:///' + os.path.join(BASE_DIR, 'workhours.db'))
Base = declarative_base()


class Workday(Base):
    __tablename__ = 'workday'

    id = Column(Integer, primary_key=True)
    start = Column(DateTime)
    end = Column(DateTime)
    company = Column(String)

    tags = relationship('Tag', order_by='Tag.recorded', cascade='all, delete, delete-orphan',
                        lazy='dynamic')


class Tag(Base):
    __tablename__ = 'tag'

    id = Column(Integer, primary_key=True)
    recorded = Column(DateTime)
    tag = Column(String)

    workday_id = Column(ForeignKey('workday.id'))
    id_under_workday = Column(Integer)

Base.metadata.create_all(engine)
session = sessionmaker(bind=engine)
