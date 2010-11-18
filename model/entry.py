#! /usr/bin/env python

from sqlalchemy import Column, Integer, Table, Unicode
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey

from meta import Base, metadata

#from sense import Sense
#from k_ele import K_ele
#from r_ele import R_ele

metadata = Base.metadata

# TODO add info

class Entry(Base):
    '''Entries consist of kanji elements, reading elements, general 
    information and sense elements. Each entry must have at least one reading 
    element and one sense element. Others are optional.'''

    __tablename__ = 'entry'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ent_seq = Column(Integer)

    kanji_id = Column(Integer, ForeignKey('kanji_element.id'))
    kana_id = Column(Integer, ForeignKey('kana_element.id'))
    sense_id = Column(Integer, ForeignKey('sense.id'))

    kanji = relationship('KanjiElement', backref='entry')
    kana = relationship('KanaElement', backref='entry')
    sense = relationship('Sense', backref='entry')

    def __str__(self):
        return u'k_ele: %s r_ele: %s sense: %s' % (
            u', '.join([s for s in self.kanji]),
            u', '.join([s for s in self.kana]),
            u', '.join([s for s in self.sense])
        )

