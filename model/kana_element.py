#! /usr/bin/env python

from sqlalchemy import Column, Integer, Table, Unicode
from sqlalchemy.orm import relation
from sqlalchemy.schema import ForeignKey

from meta import Base, metadata

from entry import Entry

metadata = Base.metadata

class KanaElement(Base):
    '''this element content is restricted to kana and related characters such 
    as chouon and kurikaeshi. Kana usage will be consistent between the keb 
    and reb elements; e.g. if the keb contains katakana, so too will the reb.'''

    __tablename__ = 'kana_element'

    id = Column(Integer, primary_key=True, autoincrement=True)
    element = Column(Unicode)

    def __str__(self):
        return u'%s' % (self.element) 

