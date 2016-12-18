#! /usr/bin/env python

from sqlalchemy import Column, Integer, Unicode
from sqlalchemy.schema import ForeignKey

from meta import Base

metadata = Base.metadata

# TODO add ke_inf and ke_pri


class KanjiElement(Base):
    '''The kanji element, or in its absence, the reading element, is the
    defining component of each entry. The overwhelming majority of entries
    will have a single kanji element associated with a word in Japanese.
    Where there are multiple kanji elements within an entry, they will be
    orthographical variants of the same word, either using variations in
    okurigana, or alternative and equivalent kanji. Common "mis-spellings"
    may be included, provided they are associated with appropriate
    information fields. Synonyms are not included; they may be indicated
    in the cross-reference field associated with the sense element.'''

    __tablename__ = 'kanji_element'

    id = Column(Integer, primary_key=True, autoincrement=True)
    element = Column(Unicode)

    entry_id = Column(Integer, ForeignKey('entry.id'))

    def __str__(self):
        return u'%s' % (self.element)
