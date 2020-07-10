import os

import platform
import tempfile
import logging as log

tempdir = "/tmp" if platform.system() == "Darwin" else tempfile.gettempdir()

db_uri = 'sqlite:///' + tempdir  + '/wordinfo.db'

log.debug("running with DB URI: " + db_uri )

# for mysql, we want to declare the default character encoding
# for comm. with the db
if db_uri.startswith("mysql"):
    db_uri += '?charset=utf8'

DATA_HERMIT_FOLDER = 'language_data/hermitdave/2016'

package_directory = os.path.dirname(os.path.abspath(__file__))
DATA_COMMON_FOLDER = package_directory + os.sep +'language_data/common'

MAX_WORDS = 10000
