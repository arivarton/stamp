##############################
#
#    Database mappings for
#    a workday
#
##############################

from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship

Base = declarative_base()


class Customer(Base):
    __tablename__ = 'customer'

    id = Column(Integer, primary_key=True)
    name = Column('Customer name', String, unique=True)
    contact_person = Column('Contact person', String, default=None)
    org_nr = Column('Organisation number', String, default=None)
    address = Column('Address', String, default=None)
    zip_code = Column('ZIP Code', String, default=None)
    mail = Column('Invoice e-mail', String, default=None)
    phone = Column('Phone number', String, default=None)

    workdays = relationship('Workday', order_by='Workday.start',
                            cascade='all, delete, delete-orphan', lazy='dynamic',
                            backref='customer')
    projects = relationship('Project', order_by='Project.id',
                            cascade='all, delete, delete-orphan', lazy='dynamic')


class Project(Base):
    __tablename__ = 'project'

    id = Column(Integer, primary_key=True)
    name = Column('Project name', String)
    link = Column('Project url', String, default=None)

    customer_id = Column(ForeignKey('customer.id'))

    workdays = relationship('Workday', order_by='Workday.start', lazy='dynamic',
                            backref='project')


class Invoice(Base):
    __tablename__ = 'invoice'

    id = Column(Integer, primary_key=True)
    created = Column(DateTime, default=datetime.now())
    pdf = Column('PDF Directory', String, unique=True, default=None)
    paid = Column(Boolean, default=False)
    sent = Column(Integer, default=0)

    workdays = relationship('Workday', order_by='Workday.start',
                            backref='invoice')


class Workday(Base):
    __tablename__ = 'workday'

    id = Column(Integer, primary_key=True)
    start = Column(DateTime)
    end = Column(DateTime, default=None)

    customer_id = Column(ForeignKey('customer.id'))
    project_id = Column(ForeignKey('project.id'))
    invoice_id = Column(ForeignKey('invoice.id'), default=None)

    tags = relationship('Tag', order_by='Tag.recorded',
                        cascade='all, delete, delete-orphan', lazy='dynamic')


class Tag(Base):
    __tablename__ = 'tag'

    id = Column(Integer, primary_key=True)
    recorded = Column(DateTime)
    tag = Column(String)

    workday_id = Column(ForeignKey('workday.id'))
    id_under_workday = Column(Integer)
