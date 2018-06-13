import os


# Directories
DEFAULT_DIR = os.path.join(os.environ.get('HOME'), '.stamp')
CONFIG_DIR = os.path.join(os.environ.get('XDG_CONFIG_HOME',
                                         os.path.join(os.environ.get('HOME'),
                                                      '.config/')),
                          'stamp/')
DATA_DIR = os.path.join(os.environ.get('XDG_DATA_HOME',
                                       os.path.join(os.environ.get('HOME'),
                                                    '.local/share/')),
                        'stamp/')
DB_FILE = os.environ.get('STAMP_DEV_DB_FILE',
                         os.environ.get('STAMP_DB_FILE', 'default'))
FILE_DIR = os.path.expanduser(os.environ.get('STAMP_FILE_DIR', DEFAULT_DIR))
REPORT_DIR = os.path.expanduser(os.environ.get('STAMP_REPORT_DIR', DEFAULT_DIR))

# User settings
MINIMUM_HOURS = int(os.getenv('STAMP_MINIMUM_HOURS') or 2)
STANDARD_HOURS = os.getenv('STAMP_STANDARD_HOURS') or '08:00-16:00'
LUNCH = os.getenv('STAMP_LUNCH') or '00:30'
STANDARD_CUSTOMER = os.getenv('STAMP_STANDARD_CUSTOMER') or None
STANDARD_PROJECT = os.getenv('STAMP_STANDARD_PROJECT') or None
WAGE_PER_HOUR = int(os.getenv('STAMP_WAGE_PER_HOUR') or 300)
CURRENCY = os.getenv('STAMP_CURRENCY') or ',-'
ORG_NR = os.getenv('STAMP_ORG_NR') or 'Not set'
COMPANY_NAME = os.getenv('STAMP_NAME') or 'Not set'
COMPANY_ADDRESS = os.getenv('STAMP_ADDRESS') or 'Not set'
COMPANY_ZIP_CODE = os.getenv('STAMP_ZIP_CODE') or 'Not set'
COMPANY_ACCOUNT_NUMBER = os.getenv('STAMP_ACCOUNT_NUMBER') or 'Not set'
PHONE = os.getenv('STAMP_PHONE') or 'Not set'
MAIL = os.getenv('STAMP_MAIL') or 'Not set'
