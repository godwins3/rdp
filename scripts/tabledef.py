# -*- coding: utf-8 -*-

import sys
import os
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

# Local
SQLALCHEMY_DATABASE_URI = 'sqlite:///accounts.db'

# Heroku
#SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']

Base = declarative_base()


def db_connect():
    """
    Performs database connection using database settings from settings.py.
    Returns sqlalchemy engine instance
    """
    return create_engine(SQLALCHEMY_DATABASE_URI)


class User(Base):
    __tablename__ = "user"

    email = Column(String(50), unique=True) 
    surname =Column(String(50))
    othername = Column(String(50))
    mobile =Column(Integer, unique=True)
    idnumber =Column(Integer, unique=True, primary_key=True)
    D_O_B = Column(String(50))
    gender =Column(String(50))
    county = Column(String(50))
    constituency =Column(String(50))
                   
    
    def __repr__(self):
        return '<User %r>' % self.idnumber


class Events(base):
    __tablename__="Events"

    id = Column(Integer, unique=True)
    event_name = Column(String(50))
    date = Column(String(50))
    time = Column(String(50))
    location = Column(String(50))

    def __repr__(self):
        return '<Events %r>' % self.id

engine = db_connect()  # Connect to database
Base.metadata.create_all(engine)  # Create models
