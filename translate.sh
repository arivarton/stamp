#! /bin/bash

find stamp -type f -name '*.py' | xargs xgettext --language=python --add-comments --sort-output --default-domain=stamp --from-code=UTF-8 --keyword='_(' --output=locale/is/LC_MESSAGES/stamp.po
msgfmt locale/is/LC_MESSAGES/stamp.po -o locale/is/LC_MESSAGES/stamp.mo
test -f $@ || msginit --locale=$* --no-translator --input=$< --output=$@
