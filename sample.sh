find ../wget-crawler/data/ \( -iname '*.htm' -o -iname '*.html' -o -iname '*.shtml' \) -type f | shuf | head -1056 > list.txt
