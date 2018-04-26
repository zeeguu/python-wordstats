from sys import stdout

import sqlalchemy.orm
import sqlalchemy
from sqlalchemy import Column, Integer, String, UniqueConstraint, Boolean
from sqlalchemy import Float

from .base_service import Base, SimplifiedQuery


class UnknownCognateInfo(object):
    """ Default values if  we have no information about
    a given word """
    def __init__(self):
        self.blacklist = False
        self.whitelist = False


class CognateCandidatesInfo(SimplifiedQuery, Base):
    __tablename__ = 'candidates_info'
    __table_args__ = {'mysql_collate': 'utf8_bin'}

    id = Column(Integer, primary_key=True)
    method = Column(String(255), nullable=False, index=True)

    word_from = Column(String(255), nullable =False, index = True)
    word_to = Column(String(255), nullable=False, index=True)
    language_ids = Column(String(4), nullable =False, index = True)

    UniqueConstraint(word_from, word_to, language_ids, method)

    def __init__(self, word_from, word_to, language_ids, method):
        self.word_from = word_from
        self.word_to = word_to
        self.language_ids = language_ids
        self.method = method

    def __str__(self):
        result = "info: {2} {3} ({0} {1})".format(
            self.word_from,
            self.word_to,
            self.language_ids,
            self.method)

        result = result.encode(stdout.encoding)
        return result

    @classmethod
    def find(cls, word, language_ids, method):
        word = word.lower()
        try:
            return (cls.query().filter(cls.word_from == word)
                    .filter(cls.language_ids == language_ids).filter(cls.method == method)
                    .one())
        except sqlalchemy.orm.exc.NoResultFound:
            return None

    @classmethod
    def find_all(cls,language_ids, method):
        return cls.query().filter(cls.language_ids == language_ids).filter(cls.method == method).all()


class CognateWhiteListInfo(SimplifiedQuery, Base):
    __tablename__ = 'cognate_whitelist_info'
    __table_args__ = {'mysql_collate': 'utf8_bin'}

    id = Column(Integer, primary_key=True)

    word_from = Column(String(255), nullable =False, index = True)
    word_to = Column(String(255), nullable=False, index=True)
    language_ids = Column(String(4), nullable =False, index = True)

    whitelist = Column(Boolean)

    UniqueConstraint(word_from, word_to, language_ids)

    def __init__(self, word_from, word_to, language_ids, whitelist):
        self.word_from = word_from
        self.word_to = word_to
        self.language_ids = language_ids
        self.whitelist = whitelist

    def __str__(self):
        result = "info: {2} ({0} {1}, whitelist: {3})".format(
            self.word_from,
            self.word_to,
            self.language_ids,
            self.whitelist)

        result = result.encode(stdout.encoding)
        return result

    @classmethod
    def find(cls, word, language_ids):
        word = word.lower()
        try:
            return (cls.query().filter(cls.word_from == word)
                    .filter(cls.language_ids == language_ids)
                    .one())
        except sqlalchemy.orm.exc.NoResultFound:
            return None

    @classmethod
    def find_all(cls,language_ids):
        return cls.query().filter(cls.language_ids == language_ids).all()


