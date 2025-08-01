#!/usr/bin/env python

import argparse
import re
from collections import Counter
import math

import spacy

# do not forget
# pip3 install spacy
# python3 -m spacy download fr_core_news_md

reg_exp = "^([-]{0,1})(.{1,3}'){0,1}(.*)" # cleans -something m'appeler and etc
def clear_word(str):
    m = re.match(reg_exp, str)
    if m.group(3):
        return m.group(3)
    if m.group(2):
        return m.group(2)
    return str

parse = argparse.ArgumentParser(description='processes a text in French and prints top words used in the text')
parse.add_argument('source', type=argparse.FileType('r'), help='a source file in French')
parse.add_argument('--more', help='shows only words occured in the text more than N times', metavar='N', type=int, dest='more', default=0)
parse.add_argument('--less', help='shows only words occured in the text less than N times', metavar='N', type=int, dest='less', default=math.inf)
parse.add_argument('--min', help="will omit words less than M characters", metavar='M', type=int, dest='min', default=0)
parse.add_argument('--show-count', help="will show count of word usage", dest="show_count", action="store_true")

args = parse.parse_args()

nlp = spacy.load('fr_core_news_md')
nlp.max_length = 1500000 # for long texts

text = args.source.read()
args.source.close()

doc = nlp(text)
lemmas = [clear_word(t.lemma_) for t in doc if not t.is_stop 
        and not t.is_punct 
        and not t.is_space 
        and t.text.strip() != ''
        and not t.is_oov # out of vacab
        and len(t.text) > args.min
        and not t.is_digit]

freq = Counter(lemmas)

for word, count in freq.most_common():
    if count >= args.more and count <= args.less:
        if args.show_count:
            print("{0:15} {1:>2}".format(word, count))
        else:
            print(word)
