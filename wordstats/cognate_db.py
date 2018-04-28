from sys import stdout

import sqlalchemy.orm
import sqlalchemy
from sqlalchemy import Column, Integer, String, UniqueConstraint, Boolean

from .base_service import Base, SimplifiedQuery


class UnknownCognateInfo(object):
    """ Default values if  we have no information about
    a given cognate pair """
    def __init__(self):
        self.word_from = ""
        self.word_to = ""
        self.blacklist = False
        self.whitelist = False


# structure for cognate candidates not reviewed by the user
class CognateCandidatesInfo(SimplifiedQuery, Base):
    __tablename__ = 'candidates_info'
    __table_args__ = {'mysql_collate': 'utf8_bin'}

    id = Column(Integer, primary_key=True)
    method = Column(String(255), nullable=False, index=True)

    word_from = Column(String(255), nullable =False, index = True)
    word_to = Column(String(255), nullable=False, index=True)
    languageFrom = Column(String(20), nullable =False, index = True)
    languageTo = Column(String(20), nullable=False, index=True)

    UniqueConstraint(word_from, word_to, languageFrom, languageTo, method)

    def __init__(self, word_from, word_to, languageFrom, languageTo, method):
        self.word_from = word_from
        self.word_to = word_to
        self.languageFrom = languageFrom
        self.languageTo = languageTo
        self.method = method

    def __str__(self):
        result = "info: {2} {3} ({0} {1})".format(
            self.word_from,
            self.word_to,
            self.languageFrom + self.languageTo,
            self.method)

        result = result.encode(stdout.encoding)
        return result

    @classmethod
    def find(cls, word, languageFrom, languageTo, method):
        word = word.lower()
        try:
            return (cls.query().filter(cls.word_from == word).\
                    filter(cls.languageFrom == languageFrom).\
                    filter(cls.languageTo == languageTo).\
                    filter(cls.method == method)
                    .one())
        except sqlalchemy.orm.exc.NoResultFound:
            return None

    @classmethod
    def find_all(cls, languageFrom, languageTo, method):
        return cls.query().filter(cls.languageFrom == languageFrom).\
            filter(cls.languageTo == languageTo).\
            filter(cls.method == method).all()


# structure for reviewed cognates
class CognateWhiteListInfo(SimplifiedQuery, Base):
    __tablename__ = 'cognate_whitelist_info'
    __table_args__ = {'mysql_collate': 'utf8_bin'}

    id = Column(Integer, primary_key=True)

    word_from = Column(String(255), nullable =False, index = True)
    word_to = Column(String(255), nullable=False, index=True)
    languageFrom = Column(String(20), nullable =False, index = True)
    languageTo = Column(String(20), nullable=False, index=True)

    whitelist = Column(Boolean)

    UniqueConstraint(word_from, word_to, languageFrom, languageTo)

    def __init__(self, word_from, word_to, languageFrom, languageTo, whitelist):
        self.word_from = word_from
        self.word_to = word_to
        self.languageFrom = languageFrom
        self.languageTo = languageTo
        self.whitelist = whitelist

    def __str__(self):
        result = "info: {2} ({0} {1}, whitelist: {3})".format(
            self.word_from,
            self.word_to,
            self.languageFrom + self.languageTo,
            self.whitelist)

        result = result.encode(stdout.encoding)
        return result

    @classmethod
    def find(cls, word, languageFrom, languageTo):
        word = word.lower()
        try:
            return (cls.query().filter(cls.word_from == word).\
                    filter(cls.languageFrom == languageFrom).\
                    filter(cls.languageTo == languageTo).\
                    one())
        except sqlalchemy.orm.exc.NoResultFound:
            return None

    @classmethod
    def find_all(cls, languageFrom, languageTo):
        return cls.query().filter(cls.languageFrom == languageFrom).\
            filter(cls.languageTo == languageTo).\
            all()
