##############################
#
#    Database mappings for
#    a workday
#
##############################

import os
from sqlalchemy import create_engine, exc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship, sessionmaker
from .settings import DATA_DIR

db_file = os.path.join(DATA_DIR, 'stamp.db')
engine = create_engine('sqlite:///' + db_file)
Base = declarative_base()


class Workday(Base):
    __tablename__ = 'workday'

    id = Column(Integer, primary_key=True)
    start = Column(DateTime)
    end = Column(DateTime, default=None)
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


try:
    Base.metadata.create_all(engine)
except exc.OperationalError as err:
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        Base.metadata.create_all(engine)
    else:
        raise err

session = sessionmaker(bind=engine)
