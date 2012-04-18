#!/usr/bin/env python

import sys
from sys import stderr
import argparse
import fontforge
import os

parser = argparse.ArgumentParser(description='Font convertor tool')
parser.add_argument('-i', '--src_font', type=str,
    help='Input font file', required=True)
parser.add_argument('-o', '--fonts_dir', type=str,
    help='Output fonts folder', required=True)

args = parser.parse_args()

font_name = os.path.basename(args.src_font)[:-4]
font_name_template = args.fonts_dir + '/' + font_name

try:
    font = fontforge.open(args.src_font)
except:
    stderr.write("Error: Fontforge can't open source %s" % args.src_font)
    sys.exit(1)

try:
    font.generate(font_name_template + '.woff')
    font.generate(font_name_template + '.svg')
except:
    stderr.write("Cannot write files in to %s\n" % args.fonts_dir)
    sys.exit(1)
