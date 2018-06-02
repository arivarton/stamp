##############################
#
#    Database mappings for
#    a workday
#
##############################

import os
from sqlalchemy import create_engine, exc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship, sessionmaker
from .settings import DATA_DIR, DB_FILE

db_path = os.path.join(DATA_DIR, DB_FILE)
engine = create_engine('sqlite:///' + db_path)
Base = declarative_base()


class Customer(Base):
    __tablename__ = 'customer'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    contact_person = Column(String, default=None)
    org_nr = Column(String, default=None)
    address = Column(String, default=None)
    mail = Column(String, default=None)
    phone = Column(String, default=None)

    workdays = relationship('Workday', order_by='Workday.start',
                            cascade='all, delete, delete-orphan', lazy='dynamic')
    projects = relationship('Project', order_by='Project.id',
                            cascade='all, delete, delete-orphan', lazy='dynamic')


class Project(Base):
    __tablename__ = 'project'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    link = Column(String)

    customer_id = Column(ForeignKey('customer.id'))

    workdays = relationship('Workday', order_by='Workday.start',
                            cascade='all, delete, delete-orphan', lazy='dynamic')


class Workday(Base):
    __tablename__ = 'workday'

    id = Column(Integer, primary_key=True)
    start = Column(DateTime)
    end = Column(DateTime, default=None)
    company = Column(String)
    paid = Column(Boolean, default=False)

    project_id = Column(ForeignKey('project.id'))
    customer_id = Column(ForeignKey('customer.id'))

    tags = relationship('Tag', order_by='Tag.recorded',
                        cascade='all, delete, delete-orphan', lazy='dynamic')


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
