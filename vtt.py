#!/usr/bin/env python3

import argparse
import os.path
import sys
import os
import re

def is_valid_file(parser, arg):
    if not os.path.exists(arg):
        parser.error("The file %s does not exist!" % arg)
    else:
        return arg

parse = argparse.ArgumentParser(description='excepts part of subs in vtt format from stdin and cut the video of')
parse.add_argument('video', type=lambda x: is_valid_file(parse, x), help='path to the video file')

args = parse.parse_args();


time_re = re.compile('([\d]{2}:[\d]{2}:[\d]{2}.[\d]{3}) --> ([\d]{2}:[\d]{2}:[\d]{2}.[\d]{3})')

stdin = sys.stdin.read()
m = time_re.findall(stdin)
for (ss, to) in m:
    file_name = ss + '_' + to;
    file_name = file_name.replace(':', '-').replace('.', 'x')
    os.system('ffmpeg -i "{0}" -ss {1} -to {2} -codec:a libmp3lame -codec:v libx264 -crf 28 -vf scale=-1:152 -q:a 10 -q:v 5 -b:a 24k -movflags +faststart {3}'.format(args.video, ss, to, file_name + '.mp4'))
    os.system('ffmpeg -i "{0}" -ss {1} -to {2} -codec:a libmp3lame -q:a 10 -map a {3}'.format(args.video, ss, to, file_name + '.mp3'))
    os.system('ffmpeg -i "{0}" -ss {1} -to {2} -vframes 1 -q:v 10 {3}'.format(args.video, ss, to, file_name + '.jpg'))

