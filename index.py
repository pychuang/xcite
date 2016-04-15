#!/usr/bin/env python3

import argparse
import json
import lxml.etree
import requests
import sys


def index(data):
    if not data:
        return
    URL = 'http://csxstaging01.ist.psu.edu:9000/solr/pychuang/update'
    headers = {'Content-type': 'application/json'}
    data_json = json.dumps(data)
    r = requests.post(URL, data=data_json, headers=headers)
    print(r)
    if r.status_code != 200:
        print(r.text)

    # commit
    params = { 'commit': 'true' }
    r = requests.get(URL, params)
    print(r)
    if r.status_code != 200:
        print(r.text)

def process_citation(c):
    citation = {}
    for e in c.iter():
        if e.tag == 'author':
            if 'author' not in citation and e.text:
                citation['author'] = []
            citation['author'].append(e.text)
        elif e.tag == 'title' and e.text:
            citation['title'] = e.text
        elif e.tag in ['booktitle', 'journal'] and e.text:
            citation['venue'] = e.text
        elif e.tag == 'date' and e.text:
            citation['year'] = int(e.text)
    if 'author' not in citation:
        return None
    if 'title' not in citation:
        return None
    if 'venue' not in citation:
        return None
    print(citation)
    citation['id'] = citation['title']
    return citation

def process(doc):
    citations = []
    for c in doc.iter('citation'):
        citation = process_citation(c)
        if not citation:
            continue
        citations.append(citation)
    return citations

def main(input_file):
    try:
        doc = lxml.etree.parse(input_file)
        citations = process(doc)
        index(citations)
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
