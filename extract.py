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
    'h1': [
        {
            'patterns': {
                'text': 'publication',
            },
            'score': 100,
            'importance': 0.1,
            'contribute-forward': 600,
            'stop-at': ['h1'],
        },
    ],
    'h2': [
        {
            'patterns': {
                'text': 'publication',
            },
            'score': 100,
            'importance': 0.1,
            'contribute-forward': 500,
            'stop-at': ['h1', 'h2'],
        },
    ],
    'h3': [
        {
            'patterns': {
                'text': 'publication',
            },
            'score': 100,
            'importance': 0.1,
            'contribute-forward': 400,
            'stop-at': ['h1', 'h2', 'h3'],
        },
    ],
    'h4': [
        {
            'patterns': {
                'text': 'publication',
            },
            'score': 100,
            'importance': 0.1,
            'contribute-forward': 300,
            'stop-at': ['h1', 'h2', 'h3', 'h4'],
        },
    ],
    'h5': [
        {
            'patterns': {
                'text': 'publication',
            },
            'score': 100,
            'importance': 0.1,
            'contribute-forward': 200,
            'stop-at': ['h1', 'h2', 'h3', 'h4', 'h5'],
        },
    ],
    'h6': [
        {
            'patterns': {
                'text': 'publication',
            },
            'score': 100,
            'importance': 0.1,
            'contribute-forward': 100,
            'stop-at': ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'],
        },
    ],
}

scores = {}
importance = {}

def attr_pattern_matched(e, attr, pattern):
    if attr not in e.attrib:
        return False
    if re.search(pattern, e.attrib[attr], flags=re.IGNORECASE):
        return True
    else:
        return False

def attr_patterns_matched(e, patterns):
    for attr, pattern in patterns.iteritems():
        if not attr_pattern_matched(e, attr, pattern):
            return False
    return True

def text_pattern_matched(e, pattern):
    if not e.text_content():
        return False
    if re.search(pattern, e.text_content(), flags=re.IGNORECASE):
        return True
    else:
        return False

def pattern_matched(e, ptype, pattern):
    if ptype == 'attr':
        return attr_patterns_matched(e, pattern)
    elif ptype == 'text':
        return text_pattern_matched(e, pattern)
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

forward_score = 0
forward_activated = {}
forward_boundary_inverted = {}

def check_forward_boundary(stop_tag):
    if stop_tag not in forward_boundary_inverted:
        return

    global forward_score
    for start_tag in forward_boundary_inverted[stop_tag]:
        if start_tag not in forward_activated:
            continue
        forward_score -= forward_activated[start_tag]
        del forward_activated[start_tag]

def contribute_forward(tag, rule):
    if 'contribute-forward' not  in rule:
        return
    score = rule['contribute-forward']
    if tag not in forward_activated:
        forward_activated[tag] = 0
    forward_activated[tag] += score
    global forward_score
    forward_score += score
    if 'stop-at' not in rule:
        return
    stop_tags = rule['stop-at']
    for stop_tag in stop_tags:
        if stop_tag not in forward_boundary_inverted:
            forward_boundary_inverted[stop_tag] = set()
        forward_boundary_inverted[stop_tag].add(tag)

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

    scores[e] += importance[e] * forward_score
    check_forward_boundary(e.tag)
    for rule in rules[e.tag]:
        if not patterns_matched(e, rule):
            continue
        contribute_forward(e.tag, rule)

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
