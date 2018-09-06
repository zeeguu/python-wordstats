from sys import stdout

import sqlalchemy.orm
import sqlalchemy
from sqlalchemy import Column, Integer, String, UniqueConstraint, Boolean

from .base_service import Base, SimplifiedQuery

# structure for reviewed cognates
class CognateDatabase(SimplifiedQuery, Base):
    __tablename__ = 'cognate_database'
    __table_args__ = {'mysql_collate': 'utf8_bin'}

    id = Column(Integer, primary_key=True)

    word_primary = Column(String(255), nullable =False, index = True)
    word_secondary = Column(String(255), nullable=False, index=True)
    primary = Column(String(20), nullable =False, index = True)
    secondary = Column(String(20), nullable=False, index=True)
    author = Column(String(255), nullable=False, index=True)
    whitelist = Column(Boolean)

    UniqueConstraint(word_primary, word_secondary, primary, secondary, author)

    def __init__(self, word_primary, word_secondary, primary, secondary, whitelist, author: str = ""):
        self.word_primary = word_primary
        self.word_secondary = word_secondary
        self.primary = primary
        self.secondary = secondary
        self.whitelist = whitelist
        self.author = author

    def __str__(self):
        result = "info: {2} ({0} {1}, whitelist: {3}, author: {4})".format(
            self.word_primary,
            self.word_secondary,
            self.primary + self.secondary,
            self.whitelist,
            self.author)

        result = result.encode(stdout.encoding)
        return result

    @classmethod
    def find(cls, word, primary, secondary, author: str = ""):
        word = word.lower()
        try:
            return (cls.query().filter(cls.word_primary == word).\
                    filter(cls.primary == primary).\
                    filter(cls.secondary == secondary). \
                    filter(cls.author == author). \
                    one())
        except sqlalchemy.orm.exc.NoResultFound:
            return None

    @classmethod
    def find_all(cls, primary, secondary, author: str = ""):
        return cls.query().filter(cls.primary == primary).\
            filter(cls.secondary == secondary). \
            filter(cls.author == author). \
            all()

    @classmethod
    def clear_entries(cls, primary, secondary, author: str = ""):
        cls.query().filter(cls.primary == primary). \
            filter(cls.secondary == secondary).filter(cls.author == author).\
            delete(synchronize_session=False)
