#!/bin/sh

find $PWD/../wget-crawler/data/ \( -iname '*.htm' -o -iname '*.html' -o -iname '*.shtml' \) -type f -print0 | xargs -0 -n 1 -I % sh -c 'echo PROCESS: % ; ./extract.py -r rules.json -t 0.6 % | ../ParsCit/bin/parseRefStrings.pl - | ./index.py'
