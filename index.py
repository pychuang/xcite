#!/usr/bin/env python3

import argparse
import lxml.etree
import sys

def process_citation(c):
    print(c)
    citation = {}
    for e in c.iter():
        if e.tag == 'author':
            if 'authors' not in citation:
                citation['authors'] = []
            citation['authors'].append(e.text)
        elif e.tag == 'title':
            citation['title'] = e.text
        elif e.tag in ['booktitle', 'journal']:
            citation['venue'] = e.text
        elif e.tag == 'date':
            citation['year'] = e.text
    print(citation)

def process(doc):
    for c in doc.iter('citation'):
        process_citation(c)

def main(input_file):
    doc = lxml.etree.parse(input_file)
    process(doc)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='read ParsCit ouput XML and then index into Solr')
    parser.add_argument('input_file', nargs='?', help='ParsCit XML file')

    args = parser.parse_args()
    if args.input_file:
        input_file = open(args.input_file)
    else:
        input_file = sys.stdin

    main(input_file)
