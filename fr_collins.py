#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests
from bs4 import BeautifulSoup
import os
from os.path import basename, splitext
from urllib.parse import urlparse
import cloudscraper

import argparse

parse = argparse.ArgumentParser(description='Parses collinsdicrionary and makes cvs to import into Anki')
parse.add_argument('source', type=argparse.FileType('r', encoding="utf-8"), help='a file with a list of words')
parse.add_argument('dest', type=argparse.FileType('w', encoding="utf-8"), help='the destionation file name')
parse.add_argument('--rewrite-media', action="store_true", help="will rewrite all media files", dest="rewrite_media")
args = parse.parse_args();

user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36'
host = 'www.collinsdictionary.com'
headers = {'user-agent': user_agent}
scraper = cloudscraper.create_scraper()  # returns a CloudScraper instance

def get(url):
    #requests.get(url, headers=headers, verify=False)
    return scraper.get(url)

def field(val):
    if val:
        return val
    else:
        return ''

def parse_name(soup):
    name = soup.select_one('h2.h2_entry .orth')
    if name:
        return name.string

def parse_pron(soup):
    pron = soup.select_one('.mini_h2 .pron')
    if pron:
        return pron.contents[0]
    else:
        return ''

def parse_word_forms(soup):
    forms = soup.select('.inflected_forms .orth')
    if forms:
        return " ".join([x.string for x in forms])
    return ''

    
def parse_mp3(soup, word):
    pron = soup.select_one('.mini_h2 .pron')
    if pron:
        mp3 = pron.select_one('[data-src-mp3]')
        if not mp3:
            return ''
        mp3 = mp3['data-src-mp3']
        if mp3:
            mp3_file = word.replace(' ', '_') + '.mp3'
            to_file = 'collection.media/' + mp3_file
            if not os.path.exists(to_file) or args.rewrite_media:
                mp3r = get(mp3)
                open(to_file, 'wb').write(mp3r.content)
            return "[sound:%s]" % mp3_file
    else:
        return ''


def parse_back(soup):
    back = soup.select_one('.sense > .cit.type-translation.quote')
    if back:
        return back.contents[0].string.strip()
    else:
        return ''

def parse_type(soup):
    type = soup.select_one('.hom .pos')
    if type:
        return type.string
    else:
        return ''


def parse_example(soup):
    example = soup.select_one('.sense .cit.type-example')
    if example:
        ex = [field(x.string).strip() for x in example if field(x.string).strip() != '']
        if len(ex) == 2:
            return "{} ({})".format(*ex)
        elif len(ex) == 1:
            return ex[0]
    return ''

def parse_image(soup, word):
    image = soup.select_one('#images img')
    if image:
        src = image['data-image']
        _, ext = splitext(urlparse(src).path)
        to_file = 'collection.media/{}{}'.format(word.replace(' ', '_'), ext)
        if not os.path.exists(to_file) or args.rewrite_media:
            imgr = get('https://{0}/{1}'.format(host, src))
            open(to_file, 'wb').write(imgr.content)
        return '<img src="{}">'.format(basename(to_file))
    else:
        return ''

def scrape_word(word):
    url = u'https://{0}/dictionary/french-english/{1}'.format(host, word.lower().replace(' ', '+'))
    r = get(url)
    if r.status_code == 200:
        soup = BeautifulSoup(r.content, 'html.parser')
    
        front = parse_name(soup)
        if not front:
            # skipping
            # print(word)
            return
        word = front = front.strip()

        pron = parse_pron(soup)
        audio = parse_mp3(soup, word)
        pron = pron + audio
        back = parse_back(soup)
        forms = parse_word_forms(soup)

        if not back:
            # parse link to another word
            another = soup.select_one('.sense .xr a')
            if another:
                back = another.string

        type = parse_type(soup)

        if type == 'masculine noun':
            front = "un %s" % front
        elif type == 'feminine noun':
            front = "une %s" % front

        example = parse_example(soup)
        image = parse_image(soup, word)

        out = ";".join([field(x) for x in [front, back, pron, example, image, forms]])
        print(out)
        return out

for line in args.source.readlines():
    word = line.strip().split(';')[0]
    out = scrape_word(word.strip())
    if out:
        args.dest.write(out + "\n")
