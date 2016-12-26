from sqlalchemy import Column, Integer, Unicode

from .meta import Base

metadata = Base.metadata


# TODO - there should still be some references to the other bulk tables. Or
#        not if this ends up being performant enough.
class Warehouse(Base):

    __tablename__ = 'warehouse'

    id = Column(Integer, primary_key=True, autoincrement=True)

    entry_id = Column(Integer)
    kana = Column(Unicode)
    kanji = Column(Unicode)
    pos = Column(Unicode)
    misc = Column(Unicode)
    gloss = Column(Unicode)
    lang = Column(Unicode)

    def __str__(self):
        return u'{}'.format(self.entry_id)
