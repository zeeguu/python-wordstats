from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import declarative_base, sessionmaker
from .config import db_uri

# This thing will be the superclass of all our model classes
Base = declarative_base()


def create_tables(engine, attempts=3):
    """ create_all() checks for each table and then creates it, so processes
    importing wordstats at the same time (e.g. gunicorn workers booting on a
    fresh container) race: the loser gets "table word_info already exists".
    Retrying lets its existence check see the winner's table and skip it. """
    for attempt in range(attempts):
        try:
            Base.metadata.create_all(engine)
            return
        except OperationalError:
            if attempt == attempts - 1:
                raise


# This is where we'll be using the session from
class BaseService(object):
    # assumes the existence of a ./wordranks/config.cfg

    # db_uri already carries the charset for mysql (config.py); sqlite has
    # no charset option and warned about the appended one on every import
    engine = create_engine(db_uri, connect_args={'check_same_thread': False})
    Session = sessionmaker(bind=engine)
    session = Session()

    @classmethod
    def drop_tables(cls):
        # We have to do a commit() before the drop_all()
        # Otherwise the system just freezes sometimes!
        cls.session.commit()
        cls.session.close_all()

        # Initial cleanup
        Base.metadata.reflect(cls.engine)
        Base.metadata.drop_all(cls.engine)
        # Creating the tables again
        create_tables(cls.engine)



class SimplifiedQuery(object):

    @classmethod
    def query(cls):
        return BaseService.session.query(cls)