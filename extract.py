#!/usr/bin/env python

import argparse
import lxml.html
import re

# ( init, multiplier, up_score, attr_rules)
rules = {
    'a': (0, 0, 100, {'href': '\.pdf$|acm|ieee|arxiv|springer'}),
    'li': (100, 1, 0, {}),
}

scores = {}

def propagate_up(e, up_score):
    if e is None:
        return
    if e.tag in rules:
        (init, mul, up, pattern) = rules[e.tag]
        scores[e] += mul * up_score
    propagate_up(e.getparent(), up_score)

def process(doc):
    for e in doc.iter():
        scores[e] = 0
        if e.tag in rules:
            #print e, e.attrib
            (init, mul, up, arules) = rules[e.tag]
            matched = True
            for attr, pattern in arules.iteritems():
                #print 'ATTR', attr, 'PATTERN', pattern
                if attr not in e.attrib or not re.search(pattern, e.attrib[attr]):
                    matched = False
                    break
            if not matched:
                continue
            #print 'MATCHED'
            scores[e] = init
            if up:
                propagate_up(e.getparent(), up)

def main(fname):
    with open(fname) as f:
        doc = lxml.html.parse(f)
        process(doc)

    print '================================='
    for e, score in sorted(scores.iteritems(), key=lambda (k,v): (v,k), reverse=True):
        if score:
            print e, score
            print e.text_content()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='extract citations')
    parser.add_argument('input_file', help='input HTML file')

    args = parser.parse_args()
    main(args.input_file)
