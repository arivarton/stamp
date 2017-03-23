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

engine = create_engine('sqlite:///workhours.db')
Base = declarative_base()


class Workday(Base):
    __tablename__ = 'workday'

    id = Column(Integer, primary_key=True)
    start = Column(DateTime)
    end = Column(DateTime)
    company = Column(String)

    tags = relationship('Tag', order_by='Tag.recorded')


class Tag(Base):
    __tablename__ = 'tag'

    id = Column(Integer, primary_key=True)
    recorded = Column(DateTime)
    tag = Column(String)

    workday_id = Column(ForeignKey('workday.id'))

Base.metadata.create_all(engine)
session = sessionmaker(bind=engine)
