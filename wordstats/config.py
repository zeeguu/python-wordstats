db_uri = 'sqlite:///wordinfo.db'

# for mysql, we want to declare the default character encoding
# for comm. with the db
if db_uri.startswith("mysql"):
    db_uri += '?charset=utf8'

DATA_FOLDER= 'language_data/hermitdave/2016'

MAX_WORDS = 10000