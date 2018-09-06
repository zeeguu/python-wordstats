from sys import stdout

import sqlalchemy.orm
import sqlalchemy
from sqlalchemy import Column, Integer, String, UniqueConstraint, Boolean

from .base_service import Base, SimplifiedQuery

# structure for cognate candidates not reviewed by the user
class TranslationDatabase(SimplifiedQuery, Base):
    __tablename__ = 'translation_database'
    __table_args__ = {'mysql_collate': 'utf8_bin'}

    id = Column(Integer, primary_key=True)

    word_primary = Column(String(255), nullable =False, index = True)
    word_secondary = Column(String(255), nullable=False, index=True)
    primary = Column(String(20), nullable =False, index = True)
    secondary = Column(String(20), nullable=False, index=True)

    UniqueConstraint(word_primary, word_secondary, primary, secondary)

    def __init__(self, word_primary, word_secondary, primary, secondary):
        self.word_primary = word_primary
        self.word_secondary = word_secondary
        self.primary = primary
        self.secondary = secondary

    def __str__(self):
        result = "info: {2} {3} ({0} {1})".format(
            self.word_primary,
            self.word_secondary,
            self.primary + self.secondary)

        result = result.encode(stdout.encoding)
        return result

    @classmethod
    def find(cls, word, primary, secondary):
        word = word.lower()
        try:
            return (cls.query().filter(cls.word_primary == word).\
                    filter(cls.primary == primary).\
                    filter(cls.secondary == secondary).\
                    one())
        except sqlalchemy.orm.exc.NoResultFound:
            return None

    @classmethod
    def find_all(cls, primary, secondary):
        return cls.query().filter(cls.primary == primary).\
            filter(cls.secondary == secondary).\
            all()

    @classmethod
    def clear_entries(cls, primary, secondary):
        cls.query().filter(cls.primary == primary). \
            filter(cls.secondary == secondary).delete(synchronize_session=False)