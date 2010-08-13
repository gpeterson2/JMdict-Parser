#! /usr/bin/env python

from sqlalchemy import Column, Integer, Table, Unicode
from sqlalchemy.orm import relation
from sqlalchemy.schema import ForeignKey

from meta import Base, metadata

from sense import Sense
from k_ele import K_ele
from r_ele import R_ele

metadata = Base.metadata

# TODO add info

class Entry(Base):
    '''Entries consist of kanji elements, reading elements, general 
    information and sense elements. Each entry must have at least one reading 
    element and one sense element. Others are optional.'''

    __tablename__ = 'entry'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ent_seq = Column(Integer)

    k_ele = relation(K_ele, backref='k_ele')
    r_ele = relation(R_ele, backref='r_ele')
    sense = relation(Sense, backref='sense')

    def __str__(self):
        return u'k_ele: %s r_ele: %s sense: %s' % (
            u', '.join([s for s in self.k_ele]),
            u', '.join([s for s in self.r_ele]),
            u', '.join([s for s in self.sense])
        )

