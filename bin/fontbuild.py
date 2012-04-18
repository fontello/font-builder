#!/usr/bin/env python

import sys
from sys import stderr
import argparse
import yaml
import fontforge

KERNING = 15

parser = argparse.ArgumentParser(description='Font builder tool')
parser.add_argument('-c', '--config', type=str, help='Config example: ../config.yml', required=True)
parser.add_argument('-t', '--sfd_template', type=str, help='SFD template file', required=True)
parser.add_argument('-i', '--svg_dir', type=str, help='Input svg file', required=True)
parser.add_argument('-o', '--ttf_file', type=str, help='Output ttf file', required=True)

args = parser.parse_args()

try:
    config = yaml.load(open(args.config, 'r'))
except IOError as (errno, strerror):
    stderr.write("Cannot open %s: %s\n" % (args.config, strerror))
    sys.exit(1)
except yaml.YAMLError, e:
    if hasattr(e, 'problem_mark'):
        mark = e.problem_mark
        stderr.write("YAML parser error in file %s at line %d, col %d\n" %
            (args.config, mark.line + 1, mark.column + 1))
    else:
        stderr.write("YAML parser error in file %s: %s\n" % (args.config, e))
    sys.exit(1)

font = fontforge.font()

# load font properties from config
for key, value in config['font'].items():
    setattr(font, key, value)

# process glyphs
for glyph in config['glyphs']:
    c = font.createChar(int(glyph['code']))

    c.importOutlines(args.svg_dir + '/' + glyph['file'] + '.svg')
    c.left_side_bearing = KERNING
    c.right_side_bearing = KERNING

    # small optimization, should not affect quality
    c.simplify()
    c.round()
#    c.addExtrema()

try:
    font.generate(args.ttf_file)
except:
    stderr.write("Cannot write to file %s\n" % args.ttf_file)
    sys.exit(1)
