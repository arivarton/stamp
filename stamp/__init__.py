import os

from .mappings import session
from .settings import DEFAULT_DIR, REPORT_DIR, FILE_DIR

if not os.path.exists(DEFAULT_DIR):
    os.makedirs(DEFAULT_DIR)

if not os.path.exists(REPORT_DIR):
    os.makedirs(REPORT_DIR)

if not os.path.exists(FILE_DIR):
    os.makedirs(FILE_DIR)

__version__ = '0.0.6'
DB_SESSION = session()
