# By importing the base service, we create the engine, and the session
from .base_service import BaseService, Base

# By importing here all the model classes, we make sure that they get
# acquinted with the Base because later the Base needs to know about
# them when it does the reflection thing to create the DB tables
from .word_info import WordInfo
from .language_info import LanguageInfo

# Create all tables in the engine. equivalent to "Create Table" in SQL
Base.metadata.create_all(BaseService.engine)

from .word_stats import Word