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

    def __init__(self, *args, **kwargs):
        self.sep = '^'

    @property
    def kanas(self):
        return self.kana.split(self.sep)

    @property
    def kanjis(self):
        return self.kanji.split(self.sep)

    @property
    def parts_of_speech(self):
        return self.pos.split(self.sep)

    @property
    def miscs(self):
        return self.misc.split(self.sep)

    @property
    def glosses(self):
        return self.gloss.split(self.sep)

    @property
    def langs(self):
        return self.lang.split(self.sep)

    def __str__(self):
        return u'{}'.format(self.entry_id)
