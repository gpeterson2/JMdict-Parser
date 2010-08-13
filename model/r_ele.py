#! /usr/bin/env python

from sqlalchemy import Column, Integer, Table, Unicode
from sqlalchemy.orm import relation
from sqlalchemy.schema import ForeignKey

from meta import Base, metadata

metadata = Base.metadata

class R_ele(Base):
    '''this element content is restricted to kana and related characters such 
    as chouon and kurikaeshi. Kana usage will be consistent between the keb 
    and reb elements; e.g. if the keb contains katakana, so too will the reb.'''

    __tablename__ = 'r_elem'

    id = Column(Integer, primary_key=True, autoincrement=True)
    entry_id = Column(Integer, ForeignKey('entry.id'))
    reb = Column(Unicode)
        
    def __str__(self):
        return u'%s' % (self.reb) 

