#! /usr/bin/evn python

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

metadata = None
Session = sessionmaker()

Base = declarative_base()

def init_model(connection_string, echo=False):
    engine = create_engine(connection_string, echo=echo)
    Session.configure(autoflush=True, autocommit=True, bind=engine)
    Base.metadata.create_all(engine, checkfirst=True) 
    metadata = Base.metadata