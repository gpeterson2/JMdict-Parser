#! /usr/bin/env python

from sqlalchemy import Column, Integer, Table, Unicode
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey

from meta import Base, metadata

from gloss import Gloss
from entry import Entry

metadata = Base.metadata

sense_pos_table = Table('sense_pos', Base.metadata,
    Column('sense_id', Integer, ForeignKey('sense.id')),
    Column('pos_id', Integer, ForeignKey('part_of_speach.id'))
)

class Sense(Base):
    '''The sense element will record the translational equivalent of the 
    Japanese word, plus other related information. Where there are several 
    distinctly different meanings of the word, multiple sense elements will 
    be employed.'''

    __tablename__ = 'sense'

    id = Column(Integer, primary_key=True, autoincrement=True)
    gloss = relationship(Gloss, backref='sense') 
    pos = relationship('PartOfSpeach',
        secondary=sense_pos_table,
        backref='sense')

    entry_id = Column(Integer, ForeignKey('entry.id'))

    def __str__(self):
        return u'%s' % (u', '.join([g for g in self.gloss])) 

