from sys import stdout

import sqlalchemy.orm
import sqlalchemy
from sqlalchemy import Column, Integer, String, UniqueConstraint

from .base_service import Base, SimplifiedQuery

# structure for rules
class TransformRules(SimplifiedQuery, Base):
    __tablename__ = 'transform_rules'
    __table_args__ = {'mysql_rules': 'utf8_bin'}

    id = Column(Integer, primary_key=True)

    primary = Column(String(20), nullable =False, index = True)
    secondary = Column(String(20), nullable=False, index=True)

    fromString = Column(String(255), nullable =False, index = True)
    toString = Column(String(255), nullable=False, index=True)
    author = Column(String(255), nullable=False, index=True)

    UniqueConstraint(primary, secondary, fromString, toString, author)

    def __init__(self, primary, secondary, fromString, toString, author:str = ""):
        self.primary = primary
        self.secondary = secondary
        self.fromString = fromString
        self.toString = toString
        self.author = author

    def __str__(self):
        result = "info: {2} ({0} {1}), {3}".format(
            self.fromString,
            self.toString,
            self.primary + self.secondary,
            self.author
            )

        result = result.encode(stdout.encoding)
        return result

    @classmethod
    def find_all(cls, primary, secondary, author:str = ""):
        return cls.query().filter(cls.primary == primary).\
            filter(cls.secondary == secondary). \
            filter(cls.author == author). \
            all()