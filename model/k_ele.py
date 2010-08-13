#! /usr/bin/env python

from sqlalchemy import Column, Integer, Table, Unicode
from sqlalchemy.orm import relation
from sqlalchemy.schema import ForeignKey

from meta import Base, metadata

metadata = Base.metadata

# TODO add ke_inf and ke_pri

class K_ele(Base):
    '''The kanji element, or in its absence, the reading element, is the 
    defining component of each entry. The overwhelming majority of entries 
    will have a single kanji element associated with a word in Japanese. 
    Where there are multiple kanji elements within an entry, they will be 
    orthographical variants of the same word, either using variations in 
    okurigana, or alternative and equivalent kanji. Common "mis-spellings" 
    may be included, provided they are associated with appropriate 
    information fields. Synonyms are not included; they may be indicated 
    in the cross-reference field associated with the sense element.'''

    __tablename__ = 'k_ele'

    id = Column(Integer, primary_key=True, autoincrement=True)
    entry_id = Column(Integer, ForeignKey('entry.id'))
    keb = Column(Unicode)
        
    def __str__(self):
        return u'%s' % (self.keb) 

