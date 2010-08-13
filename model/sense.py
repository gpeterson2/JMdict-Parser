#! /usr/bin/env python

from sqlalchemy import Column, Integer, Table, Unicode
from sqlalchemy.orm import relation
from sqlalchemy.schema import ForeignKey

from meta import Base, metadata

from gloss import Gloss

metadata = Base.metadata

class Sense(Base):
    '''The sense element will record the translational equivalent of the 
    Japanese word, plus other related information. Where there are several 
    distinctly different meanings of the word, multiple sense elements will 
    be employed.'''

    __tablename__ = 'sense'

    id = Column(Integer, primary_key=True, autoincrement=True)
    entry_id = Column(Integer, ForeignKey('entry.id'))
    gloss = relation(Gloss, backref='sense') 
        
    def __str__(self):
        return u'%s' % (u', '.join([g for g in self.gloss])) 

