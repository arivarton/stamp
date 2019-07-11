import sys
import os
import gettext
import locale

from .constants import (DEFAULT_DIR, INVOICE_DIR, FILE_DIR,
                        CONFIG_DIR, SUPPORTED_LANGUAGES, SYSTEM_LOCALE_DIR,
                        VERSION)

__version__ = VERSION

# Create necessary paths
if not os.path.exists(DEFAULT_DIR):
    os.makedirs(DEFAULT_DIR)

if not os.path.exists(INVOICE_DIR):
    os.makedirs(INVOICE_DIR)

if not os.path.exists(FILE_DIR):
    os.makedirs(FILE_DIR)

if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)


# Set language
gettext.install('stamp')

user_locale = locale.getlocale()[0].split('_')[0]

if user_locale in SUPPORTED_LANGUAGES:
    trans = gettext.translation('stamp', SYSTEM_LOCALE_DIR, languages=[user_locale])
    trans.install()
