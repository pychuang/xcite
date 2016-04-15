#!/usr/bin/env python3

import argparse
import lxml.etree
import sys

def process_citation(c):
    citation = {}
    for e in c.iter():
        if e.tag == 'author':
            if 'authors' not in citation and e.text:
                citation['authors'] = []
            citation['authors'].append(e.text)
        elif e.tag == 'title' and e.text:
            citation['title'] = e.text
        elif e.tag in ['booktitle', 'journal'] and e.text:
            citation['venue'] = e.text
        elif e.tag == 'date' and e.text:
            citation['year'] = int(e.text)
    if 'authors' not in citation:
        return
    if 'title' not in citation:
        return
    if 'venue' not in citation:
        return
    print(citation)

def process(doc):
    for c in doc.iter('citation'):
        process_citation(c)

def main(input_file):
    try:
        doc = lxml.etree.parse(input_file)
        process(doc)
    except lxml.etree.XMLSyntaxError:
        pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='read ParsCit ouput XML and then index into Solr')
    parser.add_argument('input_file', nargs='?', help='ParsCit XML file')

    args = parser.parse_args()
    if args.input_file:
        input_file = open(args.input_file)
    else:
        input_file = sys.stdin

    main(input_file)
