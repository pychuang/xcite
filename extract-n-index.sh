#!/bin/sh

find $PWD/../wget-crawler/data/ \( -iname '*.htm' -o -iname '*.html' -o -iname '*.shtml' \) -type f -print0 | xargs -0 -n 1 -P 12 ./extract-parse-index.py -R rules.json -r 0.6 -t 150
