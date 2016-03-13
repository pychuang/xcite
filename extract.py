#!/usr/bin/env python

import argparse
import json
import lxml.html
import re
import sys

rules = None
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

def main(input_file):
    doc = lxml.html.parse(input_file)
    process(doc)

    print '================================='
    for e, score in sorted(scores.iteritems(), key=lambda (k,v): (v,k), reverse=True):
        if score:
            print e, score
            content = e.text_content()
            print ' '.join(content.split())

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='extract citations')
    parser.add_argument('-r', '--rules', required=True, help='rules JSON file')
    parser.add_argument('input_file', nargs='?', help='input HTML file')

    args = parser.parse_args()
    if args.input_file:
        input_file = open(args.input_file)
    else:
        input_file = sys.stdin

    rules = json.load(open(args.rules))
    main(input_file)
