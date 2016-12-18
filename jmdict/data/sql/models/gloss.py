#! /usr/bin/env python

from sqlalchemy import Column, Integer, Unicode
# from sqlalchemy.schema import ForeignKey

from .meta import Base

metadata = Base.metadata


class Gloss(Base):
    '''Within each sense will be one or more "glosses", i.e. target-language
    words or phrases which are equivalents to the Japanese word. This element
    would normally be present, however it may be omitted in entries which are
    purely for a cross-reference.'''

    __tablename__ = 'gloss'

    id = Column(Integer, primary_key=True, autoincrement=True)

    # FIXME - A given gloss will have a part of speech (i.e. it's a noun) but there
    # might be multiple for a given element representing differnt languages. So
    # there should be a single sense object with multiple glosses under it.
    #
    # The parts of speech are also known quanties (although I'm not sure if they
    # can be directly read from the xml), so they should be insert and referenced
    # rather than being included in the table here.
    #
    # Not doing that here to save time during developing.
    #sense_id = Column(Integer, ForeignKey('sense.id'))
    pos = Column(Unicode)

    gloss = Column(Unicode)
    lang = Column(Unicode)

    def __str__(self):
        return u'lang: %s: %s' % (self.gloss)
