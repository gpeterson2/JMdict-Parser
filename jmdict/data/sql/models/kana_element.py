from sqlalchemy import Column, Integer, Unicode
# from sqlalchemy.schema import ForeignKey

from .meta import Base

metadata = Base.metadata


class KanaElement(Base):
    '''this element content is restricted to kana and related characters such
    as chouon and kurikaeshi. Kana usage will be consistent between the keb
    and reb elements; e.g. if the keb contains katakana, so too will the reb.'''

    __tablename__ = 'kana'

    id = Column(Integer, primary_key=True, autoincrement=True)
    kana = Column(Unicode)

    # TODO - get back to this.
    #entry_id = Column(Integer, ForeignKey('entry.id'))

    def __str__(self):
        return self.kana
