#!/usr/bin/env python

import sys
from sys import stderr
import argparse
import yaml
import fontforge

parser = argparse.ArgumentParser(description='Font remap tool')
parser.add_argument('-c', '--config',   type=str, required=True,
    help='Config example: ../config.yml')
parser.add_argument('-i', '--src_font', type=str, required=True,
    help='Input font')
parser.add_argument('-o', '--dst_font', type=str, required=True,
    help='Output font')

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

# prepare config to view:
# [(from_code1, to_code1), (from_code2, to_code2), ...]
remap_config = [(glyph.get('from', glyph['code']), glyph['code'])
                    for glyph in config['glyphs']]

# validate config: fetcy duplicate 'from' codes
src_codes = zip(*remap_config)[0]
if len(src_codes) != len(set(src_codes)):
    stderr.write("Error in file %s: glyph codes aren't unique:\n" % args.config)
    for code in set(src_codes):
        if src_codes.count(code) > 1:
            stderr.write("Duplicate 'from:' 0x%04x\n" % code)
    sys.exit(1)

try:
    font = fontforge.open(args.src_font)
    # set font encoding so we can select any unicode code point
    font.encoding = 'UnicodeFull'
except:
    stderr.write("Error: Fontforge can't open source %s" % args.src_font)
    sys.exit(1)

new_font = fontforge.font()
new_font.encoding = 'UnicodeFull'

# load font properties from config
for key, value in config.get('font', {}).items():
    setattr(new_font, key, value)


for from_code, to_code in remap_config:
    try:
        font[from_code]
    except TypeError:
        stderr.write("Warning: no such glyph in the source font (code=0x%04x)\n" %
            from_code)
        continue

    font.selection.select(("unicode",), from_code)
    font.copy()
    new_font.selection.select(("unicode",), to_code)
    new_font.paste()

try:
    new_font.generate(args.dst_font)
except:
    stderr.write("Cannot write to file %s\n" % args.dst_font)
    sys.exit(1)
