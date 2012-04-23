#!/usr/bin/env python
import sys
from sys import stderr
import argparse
import yaml
import fontforge

parser = argparse.ArgumentParser(description='Merges glyphs from '
        'several fonts, as specified in config.')
parser.add_argument('-c', '--config',   type=str, required=False,
        help='Config file in json or yml format. If missed, then '
        'loaded from stdin. '
        'example: ../config.json')
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
    # yaml parser undestend both formats
    config = yaml.load(unparsed_config)

except yaml.YAMLError, e:

    config_file_name = '' if args.config is None else args.config
    if hasattr(e, 'problem_mark'):
        mark = e.problem_mark
        stderr.write("YAML parser error in config %s at line %d, col %d\n" %
            (config_file_name, mark.line + 1, mark.column + 1))
    else:
        stderr.write("YAML parser error in config %s: %s\n" % (config_file_name, e))
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
remap_config = [(glyph.get('from', glyph['code']),
                glyph['code'], glyph['src'])
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
