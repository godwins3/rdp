# -*- coding: utf-8 -*-

from scripts import tabledef
from flask import session
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import bcrypt


@contextmanager
def session_scope():
    """Provide a transactional scope around a series of operations."""
    s = get_session()
    s.expire_on_commit = False
    try:
        yield s
        s.commit()
    except:
        s.rollback()
        raise
    finally:
        s.close()


def get_session():
    return sessionmaker(bind=tabledef.engine)()


def get_user():
    username = session['username']
    with session_scope() as s:
        user = s.query(tabledef.User).filter(tabledef.User.username.in_([username])).first()
        return user


def add_user(email, surname, othername, mobile, idnumber, D_O_B, gender, county, constituency):
    with session_scope() as s:
        u = tabledef.User(email=email, 
                          surname=surname, 
                          othername=othername, 
                          mobile=mobile, 
                          idnumber=idnumber, 
                          D_O_B=D_O_B, 
                          gender=gender, 
                          county=county,
                          constituency=constituency)
        s.add(u)
        s.commit()

def credentials_valid(idnumber, mobile):
    with session_scope() as s:
        user = s.query(tabledef.User).filter(tabledef.User.idnumber.in_([idnumber])).first()
        if user:
            return bcrypt.checkpw(mobile.encode('utf8'), user.mobile.encode('utf8'))
        else:
            return False


def id_taken(idnumber):
    with session_scope() as s:
        return s.query(tabledef.User).filter(tabledef.User.idnumber.in_([idnumber])).first()
    
def contact_us(email, message):
    with session_scope() as s:
        u = tabledef.Contact_us(email = email, message = message)
        s.add(u)
        s.commit()
