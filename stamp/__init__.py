import os

from mappings import session

__version__ = '0.3.2'
DB_SESSION = session()

# User settings
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MINIMUM_HOURS = int(os.getenv('STAMP_MINIMUM_HOURS') or 2)
REPORT_DIR = os.getenv('STAMP_REPORT_DIR') or BASE_DIR
HOURS = os.getenv('STAMP_HOURS') or '08:00-16:00'
LUNCH = os.getenv('STAMP_LUNCH') or '00:30'
STANDARD_COMPANY = os.getenv('STAMP_STANDARD_COMPANY') or 'Not specified'
WAGE_PER_HOUR = int(os.getenv('STAMP_WAGE_PER_HOUR') or 300)
CURRENCY = os.getenv('STAMP_CURRENCY') or 'NKR'
