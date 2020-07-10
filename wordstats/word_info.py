from sys import stdout

import sqlalchemy.orm
import sqlalchemy
from sqlalchemy import Column, Integer, String, UniqueConstraint
from sqlalchemy import Float

from .base_service import Base, SimplifiedQuery


class UnknownWordInfo(object):
    """ Default values if  we have no information about
    a given word """
    def __init__(self):
        self.frequency = 0
        self.importance = 0
        self.difficulty = 1
        self.klevel = 100
        self.rank = 100000


class WordInfo(SimplifiedQuery, Base):
    __tablename__ = 'word_info'
    __table_args__ = {'mysql_collate': 'utf8_bin'}

    id = Column(Integer, primary_key=True)

    word = Column(String(255), nullable =False, index = True)
    language_id = Column(String(2), nullable =False, index = True)

    frequency = Column(Integer)
    importance = Column(Integer)
    difficulty = Column(Float)
    rank = Column(Integer)
    klevel = Column(Integer)

    UniqueConstraint(word, language_id)

    def __init__(self, word, language_id, frequency, difficulty, importance, rank, klevel):
        self.word = word
        self.language_id = language_id
        self.frequency = frequency
        self.importance = importance
        self.difficulty = difficulty
        self.klevel = klevel
        self.rank = rank

    def __str__(self):
        result = "{0}: (lang: {1}, rank: {5}, freq: {2}, imp: {3}, diff: {4}, klevel: {6})".format(
            self.word,
            self.language_id,
            self.frequency,
            self.importance,
            self.difficulty,
            self.rank,
            self.klevel)

        return result

    @classmethod
    def find(cls, word, language_id):
        word = word.lower()
        try:
            return (cls.query().filter(cls.word == word)
                    .filter(cls.language_id == language_id)
                    .one())
        except sqlalchemy.orm.exc.NoResultFound:
            return None

    @classmethod
    def find_all(cls,language_id):
        return cls.query().filter(cls.language_id == language_id).all()


