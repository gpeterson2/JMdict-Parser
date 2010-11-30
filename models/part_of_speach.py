#! /usr/bin/env python

from sqlalchemy import Column, Integer, Table, Unicode
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey

from meta import Base, metadata

metadata = Base.metadata

class PartOfSpeach(Base):
    ''' Part-of-speech information about the entry/sense. Should use 
    appropriate entity codes. In general where there are multiple senses in 
    an entry, the part-of-speech of an earlier sense will apply to later 
    senses unless there is a new part-of-speech indicated.
    '''

    __tablename__ = 'part_of_speach'

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(Unicode) # The short character code
    text = Column(Unicode) # A full text explanation

    def __str__(self):
        return self.text

