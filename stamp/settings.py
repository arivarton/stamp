import os


# Directories
DEFAULT_DIR = os.path.join(os.environ.get('HOME'), '.stamp')
CONFIG_DIR = os.path.join(os.environ.get('XDG_CONFIG_HOME',
                                         os.path.join(os.environ.get('HOME'),
                                                      '.config/')),
                          'stamp/')
CONFIG_FILE = os.environ.get('STAMP_DEV_CONFIG_FILE',
                             os.environ.get('STAMP_CONFIG_FILE', 'config'))
DATA_DIR = os.path.join(os.environ.get('XDG_DATA_HOME',
                                       os.path.join(os.environ.get('HOME'),
                                                    '.local/share/')),
                        'stamp/')
DB_FILE = os.environ.get('STAMP_DEV_DB_FILE',
                         os.environ.get('STAMP_DB_FILE', 'default'))
FILE_DIR = os.path.expanduser(os.environ.get('STAMP_FILE_DIR', DEFAULT_DIR))
INVOICE_DIR = os.path.expanduser(os.environ.get('STAMP_INVOICE_DIR',
                                                '~/Documents/stamp/Invoices'))

# User settings
MINIMUM_HOURS = int(os.getenv('STAMP_MINIMUM_HOURS') or 2)
STANDARD_HOURS = os.getenv('STAMP_STANDARD_HOURS') or '08:00-16:00'
LUNCH = os.getenv('STAMP_LUNCH') or '00:30'
STANDARD_CUSTOMER = os.getenv('STAMP_STANDARD_CUSTOMER')
STANDARD_PROJECT = os.getenv('STAMP_STANDARD_PROJECT')
WAGE_PER_HOUR = int(os.getenv('STAMP_WAGE_PER_HOUR') or 300)
CURRENCY = os.getenv('STAMP_CURRENCY') or ',-'
ORG_NR = os.getenv('STAMP_ORG_NR')
COMPANY_NAME = os.getenv('STAMP_NAME')
COMPANY_ADDRESS = os.getenv('STAMP_ADDRESS')
COMPANY_ZIP_CODE = os.getenv('STAMP_ZIP_CODE')
COMPANY_ACCOUNT_NUMBER = os.getenv('STAMP_ACCOUNT_NUMBER')
PHONE = os.getenv('STAMP_PHONE')
MAIL = os.getenv('STAMP_MAIL')
