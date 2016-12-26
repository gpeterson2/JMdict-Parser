from sqlalchemy import Column, Integer, Unicode

from .meta import Base

metadata = Base.metadata


class Misc(Base):
    '''This element is used for other relevant information about
    the entry/sense. As with part-of-speech, information will usually
    apply to several senses.'''

    __tablename__ = 'misc'

    id = Column(Integer, primary_key=True, autoincrement=True)

    misc = Column(Unicode)

    def __str__(self):
        return u'{}' % (self.misc)
