from invoke import task
import fileinput
import sys
import os
import locale
from datetime import datetime

from stamp import __version__

SUPPORTED_LANGUAGES = ['is', 'en', 'nb']
LOCALE_DIR = 'locale'
if not os.path.exists(LOCALE_DIR):
    os.makedirs(LOCALE_DIR)
POTFILE = os.path.join(LOCALE_DIR, 'stamp.pot')
USER_LOCALE = locale.getlocale()

POT_CHANGES = [('SOME DESCRIPTIVE TITLE', 'STAMP'),
               ('YEAR THE PACKAGE\'S COPYRIGHT HOLDER', '{} arivarton'.format(str(datetime.now().year))),
               ('PACKAGE', 'stamp'),
               ('PACKAGE VERSION', str(__version__)),
               ('CHARSET', 'UTF-8')]



@task
def translate(c):
    c.run("find stamp -type f -name '*.py' \
                | xargs xgettext --language=python --add-comments --sort-output --default-domain=stamp --from-code=UTF-8 --keyword='_(' --output={}".format(POTFILE))
    for line in fileinput.input('{}'.format(POTFILE), inplace=True):
        try:
            if POT_CHANGES[0][0] in line:
                line = line.replace(*POT_CHANGES.pop(0))
        except IndexError:
            pass
        sys.stdout.write(line)
    for lang in SUPPORTED_LANGUAGES:
        po_file = os.path.join(LOCALE_DIR, lang + '.po')
        if not os.path.isfile(po_file):
            c.run("msginit --locale={locale} --no-translator --input={input_file} --output={output_file}".format(locale=lang,
                                                                                                                 input_file=POTFILE,
                                                                                                                 output_file=po_file))
        else:
            c.run("msgmerge --update {output_file} {input_file}".format(output_file=po_file,
                                                                        input_file=POTFILE))

@task
def test(c):
    c.run("python tests/test_cli2.py", in_stream=False)
