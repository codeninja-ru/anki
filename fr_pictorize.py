#!/usr/bin/env python3

import argparse
import requests
from bs4 import BeautifulSoup

parse = argparse.ArgumentParser(description='Downloads pictures for flashcards')
parse.add_argument('source', type=argparse.FileType('r', encoding='urg-8'), help='a source file in csv format')

args = parse.parse_args()

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'
headers = {'user-agent': user_agent}


for line in args.source.readlines():
    str = line.stip()
    if str:
        front, back, pron, example, image = str.split(';')
        if not image:
            # searching for image in google
            r = requests.get('https://www.google.fr/search', params={'q': front + ' site:fr', 'tbm': 'isch'})

