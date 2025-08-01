#!/usr/bin/env python

import argparse
import json
import urllib.request
import sys

parse = argparse.ArgumentParser(description='processes list of words from stdin and put a tag to each word in anki')
parse.add_argument('--tag', type=str, help='tag to set on each word', dest='tag_name')
parse.add_argument('--anki', help='AnkiConnect address', dest='anki_url', default='localhost:8765')
parse.add_argument('source', type=argparse.FileType('r'), help='a source of words, each line conains a word', default=sys.stdin)
parse.add_argument('--notFoundFile', type=argparse.FileType('a'), help='a file to save not founded words', required=True, dest='not_found_file')

args = parse.parse_args()

def request(action, **params):
    return {'action': action, 'params': params, 'version': 6}

def invoke(action, **params):
    requestJson = json.dumps(request(action, **params)).encode('utf-8')
    response = json.load(urllib.request.urlopen(urllib.request.Request('http://' + args.anki_url, requestJson)))
    if len(response) != 2:
        raise Exception('response has an unexpected number of fields')
    if 'error' not in response:
        raise Exception('response is missing required error field')
    if 'result' not in response:
        raise Exception('response is missing required result field')
    if response['error'] is not None:
        raise Exception(response['error'])
    return response['result']

def findNotes(query):
    resp = invoke('findNotes', query=query)
    return resp

def notesInfo(notes):
    resp = invoke('notesInfo', notes=notes)
    return resp

def addTags(notes, tags):
    resp = invoke('addTags', notes=notes, tags=tags)
    return resp

def frQuery(word):
    return 'front:{0} OR front:un_{0} OR front:une_{0}'.format(word)

for word in args.source.readlines():
    word = word.strip()
    notes = findNotes(frQuery(word))
    if len(notes) == 0:
        print('word = "{0}" not found'.format(word))
        args.not_found_file.write(word + "\n")
    else:
        noteNames = list(map(lambda data: data['fields']['Front']['value'], notesInfo(notes)))
        tag_added = 'no tags added'
        if args.tag_name:
            addTags(notes, args.tag_name)
            tag_added = 'tag "{0}" added'.format(args.tag_name)

        print('word = "{0}", notes found: [{1}], {2}'.format(word, ', '.join(noteNames), tag_added))

args.not_found_file.close()
