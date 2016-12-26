from sqlalchemy import Column, Integer, Table
from sqlalchemy.orm import relationship
from sqlalchemy.schema import ForeignKey

from .meta import Base

from .gloss import Gloss
from .misc import Misc
from .part_of_speech import PartOfSpeech

metadata = Base.metadata

sense_entry_table = Table('sense_entry', Base.metadata,
                          Column('sense_id', Integer, ForeignKey('sense.id')),
                          Column('entry_id', Integer, ForeignKey('entry.id')))

sense_pos_table = Table('sense_pos', Base.metadata,
                        Column('sense_id', Integer, ForeignKey('sense.id')),
                        Column('pos_id', Integer, ForeignKey('part_of_speech.id')))

sense_gloss_table = Table('sense_gloss', Base.metadata,
                          Column('sense_id', Integer, ForeignKey('sense.id')),
                          Column('gloss_id', Integer, ForeignKey('gloss.id')))

sense_misc_table = Table('sense_misc', Base.metadata,
                         Column('sense_id', Integer, ForeignKey('sense.id')),
                         Column('misc_id', Integer, ForeignKey('misc.id')))


class Sense(Base):
    '''The sense element will record the translational equivalent of the
    Japanese word, plus other related information. Where there are several
    distinctly different meanings of the word, multiple sense elements will
    be employed.'''

    __tablename__ = 'sense'

    id = Column(Integer, primary_key=True, autoincrement=True)

    entry_id = Column(Integer, ForeignKey('entry.id'))
    pos = relationship(PartOfSpeech, secondary=sense_pos_table, backref='sense')
    gloss = relationship(Gloss, secondary=sense_gloss_table, backref='sense')
    misc = relationship(Misc, secondary=sense_misc_table, backref='sense')

    def __str__(self):
        return u'{}' % (u', '.join([g for g in self.gloss]))
