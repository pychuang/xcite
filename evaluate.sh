while read LINE <&3; do echo $LINE; ./extract.py -R rules.json -r 0.6 -t 150 $LINE; read -n 1 -p CONTINUE; done  3< list.txt
