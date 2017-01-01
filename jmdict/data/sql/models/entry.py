from sqlalchemy import Column, Integer, Table
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey

from .meta import Base

from .kana_element import KanaElement
from .kanji_element import KanjiElement
from .sense import Sense

metadata = Base.metadata

# Might want to make this a stand-alone table to make insertions easier.
entry_kana_table = Table('entry_kana', Base.metadata,
                         Column('entry_id', Integer, ForeignKey('entry.id')),
                         Column('kana_id', Integer, ForeignKey('kana.id')))

entry_kanji_table = Table('entry_kanji', Base.metadata,
                          Column('entry_id', Integer, ForeignKey('entry.id')),
                          Column('kanji_id', Integer, ForeignKey('kanji.id')))

entry_sense_table = Table('entry_sense', Base.metadata,
                          Column('entry_id', Integer, ForeignKey('entry.id')),
                          Column('sense_id', Integer, ForeignKey('sense.id')))


class Entry(Base):
    '''Entries consist of kanji elements, reading elements, general
    information and sense elements. Each entry must have at least one reading
    element and one sense element. Others are optional.'''

    __tablename__ = 'entry'

    id = Column(Integer, primary_key=True, autoincrement=True)
    # TODO - rename after insert is normalized.
    ent_seq = Column(Integer, name='entry')

    kana = relationship(KanaElement, secondary=entry_kana_table, backref='entry')
    kanji = relationship(KanjiElement, secondary=entry_kanji_table, backref='entry')
    sense = relationship(Sense, backref='entry')

    def __str__(self):
        return '{}'.format(self.ent_seq)
