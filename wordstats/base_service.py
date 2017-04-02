from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import db_uri

# This thing will be the superclass of all our model classes
Base = declarative_base()


# This is where we'll be using the session from
class BaseService(object):
    # assumes the existence of a ./wordranks/config.cfg

    engine = create_engine(db_uri, encoding='utf-8')
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
        Base.metadata.create_all(cls.engine)



class SimplifiedQuery(object):

    @classmethod
    def query(cls):
        return BaseService.session.query(cls)