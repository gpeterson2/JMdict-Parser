from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

__all__ = ['Base', 'metadata', 'Session', 'init_model']

metadata = None
Session = sessionmaker()

Base = declarative_base()


class init_model(object):
    def __init__(self, connection_string, echo=False):
        self.engine = create_engine(connection_string, echo=echo)
        Session.configure(autoflush=True, autocommit=True, bind=self.engine)
        self.session = Session

        # Base.metadata.create_all(engine, checkfirst=True)
        # metadata = Base.metadata

    def create_all(self):
        Base.metadata.create_all(self.engine, checkfirst=True)

    def drop_all(self):
        Base.metadata.drop_all(self.engine)
