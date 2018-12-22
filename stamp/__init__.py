import os
from .settings import DEFAULT_DIR, INVOICE_DIR, FILE_DIR, CONFIG_DIR

if not os.path.exists(DEFAULT_DIR):
    os.makedirs(DEFAULT_DIR)

if not os.path.exists(INVOICE_DIR):
    os.makedirs(INVOICE_DIR)

if not os.path.exists(FILE_DIR):
    os.makedirs(FILE_DIR)

if not os.path.exists(CONFIG_DIR):
    os.makedirs(CONFIG_DIR)

__version__ = '0.1.7'
