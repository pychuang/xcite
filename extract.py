#!/usr/bin/env python

import argparse
import lxml.html
import re

rules = {
    'a': [
        {
            'patterns': {
                'attr': {'href': '\.pdf$|acm|ieee|arxiv|springer'},
            },
            'score': 10,
            'importance': 0.9,
            'contribute-up': 100,
        },
    ],
    'li': [
        {
            'score': 100,
            'importance': 1.0,
        },
    ],
}

scores = {}
importance = {}

def attr_pattern_matched(e, attr, pattern):
    if attr not in e.attrib:
        return False
    if re.search(pattern, e.attrib[attr]):
        return True
    return False

def attr_patterns_matched(e, patterns):
    for attr, pattern in patterns.iteritems():
        if not attr_pattern_matched(e, attr, pattern):
            return False
    return True

def pattern_matched(e, ptype, pattern):
    if ptype == 'attr':
        return attr_patterns_matched(e, pattern)
    elif ptype == 'text':
        pass
    return False

def patterns_matched(e, rule):
    if 'patterns' not in rule:
        return True

    patterns = rule['patterns']
    for ptype, pattern in patterns.iteritems():
        if not pattern_matched(e, ptype, pattern):
            return False
    return True

def propagate_up(e, score):
    if e is None:
        return
    scores[e] += importance[e] * score
    propagate_up(e.getparent(), score)

def contribute_up(e, rule):
    if 'contribute-up' not in rule:
        return
    up_score = rule['contribute-up']
    propagate_up(e.getparent(), up_score)

def process_element(e):
    scores[e] = 0
    importance[e] = 0
    if e.tag not in rules:
        return

    for rule in rules[e.tag]:
        if not patterns_matched(e, rule):
            continue
        scores[e] += rule['score']
        importance[e] += rule['importance']
        contribute_up(e, rule)

def process(doc):
    for e in doc.iter():
        process_element(e)

def main(fname):
    with open(fname) as f:
        doc = lxml.html.parse(f)
        process(doc)

    print '================================='
    for e, score in sorted(scores.iteritems(), key=lambda (k,v): (v,k), reverse=True):
        if score:
            print e, score
            content = e.text_content()
            print ' '.join(content.split())

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='extract citations')
    parser.add_argument('input_file', help='input HTML file')

    args = parser.parse_args()
    main(args.input_file)
