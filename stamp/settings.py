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
                         os.environ.get('STAMP_DB_FILE', 'default')) + '.db'
FILE_DIR = os.path.expanduser(os.environ.get('STAMP_FILE_DIR', DEFAULT_DIR))
REPORT_DIR = os.path.expanduser(os.environ.get('STAMP_REPORT_DIR', DEFAULT_DIR))

# User settings
MINIMUM_HOURS = int(os.getenv('STAMP_MINIMUM_HOURS') or 2)
HOURS = os.getenv('STAMP_HOURS') or '08:00-16:00'
LUNCH = os.getenv('STAMP_LUNCH') or '00:30'
STANDARD_COMPANY = os.getenv('STAMP_STANDARD_COMPANY') or 'Not specified'
WAGE_PER_HOUR = int(os.getenv('STAMP_WAGE_PER_HOUR') or 300)
CURRENCY = os.getenv('STAMP_CURRENCY') or 'NKR'
