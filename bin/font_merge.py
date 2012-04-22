#!/usr/bin/env python
import sys
from sys import stderr
import argparse
import json
import fontforge

parser = argparse.ArgumentParser(description='Font merge tool')
parser.add_argument('-c', '--config',   type=str, required=False,
        help='Config example: ../config.yml. If missed, then loaded from stdin')
parser.add_argument('-o', '--dst_font', type=str, required=True,
        help='Output font')

args = parser.parse_args()

if args.config is not None:
    try:
        unparsed_config = open(args.config, 'r')

    except IOError as (errno, strerror):
        stderr.write("Cannot open %s: %s\n" % (args.config, strerror))
        sys.exit(1)
else:
    unparsed_config = sys.stdin

try:
    config = json.load(unparsed_config)
except ValueError, e:
    stderr.write("JSON parser error in file %s: %s\n" % (args.config, e))
    sys.exit(1)


# init new font
new_font = fontforge.font()
new_font.encoding = 'UnicodeFull'

# load font properties from config
for key, value in config['font'].iteritems():
    setattr(new_font, key, value)

try:
    # read source fonts
    src_fonts = {}
    for name, path in config['src_fonts'].iteritems():
        src_fonts[name] = fontforge.open(path)
except:
    stderr.write("Error: fontforge can't open source font from %s" % path)
    sys.exit(1)

# prepare config to view:
# [(from_code1, to_code1, src), (from_code2, to_code2, src), ...]
remap_config = [(int(glyph.get('from', glyph['code']), 0),
                int(glyph['code'], 0), glyph['src'])
                    for glyph in config['glyphs']]


for from_code, to_code, src in remap_config:
    try:
        src_fonts[src][from_code]
    except TypeError:
        stderr.write("Warning: no such glyph in the source font (code=0x%04x)\n" %
            from_code)
        continue

    src_fonts[src].selection.select(("unicode",), from_code)
    src_fonts[src].copy()
    new_font.selection.select(("unicode",), to_code)
    new_font.paste()

try:
    new_font.generate(args.dst_font)
except:
    stderr.write("Cannot write to file %s\n" % args.dst_font)
    sys.exit(1)
