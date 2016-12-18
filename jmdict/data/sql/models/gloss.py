#! /usr/bin/env python

from sqlalchemy import Column, Integer, Unicode
from sqlalchemy.schema import ForeignKey

from meta import Base

metadata = Base.metadata


class Gloss(Base):
    '''Within each sense will be one or more "glosses", i.e. target-language
    words or phrases which are equivalents to the Japanese word. This element
    would normally be present, however it may be omitted in entries which are
    purely for a cross-reference.'''

    __tablename__ = 'gloss'

    id = Column(Integer, primary_key=True, autoincrement=True)
    sense_id = Column(Integer, ForeignKey('sense.id'))
    lang = Column(Unicode)
    gloss = Column(Unicode)

    def __str__(self):
        return u'lang: %s: %s' % (self.gloss)
