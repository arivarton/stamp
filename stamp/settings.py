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
