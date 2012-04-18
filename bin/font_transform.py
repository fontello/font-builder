#!/usr/bin/env python

import sys
from sys import stderr
import argparse
import yaml
import fontforge
import psMat
from pprint import pprint


def apply_rescale(glyph, origin, scale):
    """Rescale glyph"""
    # move scale origin point to (0, 0)
    sx, sy = origin
    translate_matrix = psMat.translate(-sx, -sy)
    glyph.transform(translate_matrix)

    # scale around (0, 0)
    scale_matrix = psMat.scale(scale)
    glyph.transform(scale_matrix)

    # move scale origin point back to its old position
    translate_matrix = psMat.translate(origin)
    glyph.transform(translate_matrix)


parser = argparse.ArgumentParser(description='Font transform tool')
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
        stderr.write("YAML parser error in file %s at line %d, col %d" %
            (args.config, mark.line + 1, mark.column + 1))
    else:
        stderr.write("YAML parser error in file %s: %s" % (args.config, e))
    sys.exit(1)


# fetch genral rules
base = config.get('transform', {}).items()
# merge local and general rules
merge = lambda glyph: dict(base + glyph.get('transform', {}).items())
# prepare config to view:
# [(code1, {'rescale': 1.0, 'offset': 0.0}), (code2, {}), ...]
transform_config = [(glyph.get('code'), merge(glyph)) for glyph in config['glyphs']]


# validate config: fetch duplicate codes
codes = zip(*transform_config)[0]
if len(codes) != len(set(codes)):
    stderr.write("Error in file %s: glyph codes aren't unique:\n" % args.config)
    for code in set(codes):
        if codes.count(code) > 1:
            stderr.write("Duplicate 'from:' 0x%04x\n" % code)
    sys.exit(1)

try:
    # source font
    font = fontforge.open(args.src_font)
    # set font encoding so we can select any unicode code point
    font.encoding = 'UnicodeFull'
except:
    stderr.write("Error: fontforge can't open source font from %s" % args.src_font)
    sys.exit(1)

# set ascent/descent
ascent = config.get('font', {}).get('ascent', font.ascent)
descent = config.get('font', {}).get('descent', font.descent)
font.ascent = ascent
font.descent = descent

default_baseline = float(descent) / (ascent + descent)

origin_point = lambda baseline: (0, (ascent + descent) * baseline - descent)
offset_matrix = lambda offset: psMat.translate(0, offset * (ascent + descent))
# apply transformations
for code, transform in transform_config:
    try:
        glyph = font[code]
    except TypeError:
        stderr.write("Warning: no such glyph (code=0x%04x)\n" % code)
        continue

    if 'rescale' in transform:
        baseline = transform.get('baseline', default_baseline)
        scale    = transform['rescale']
        apply_rescale(glyph, origin_point(baseline), scale)

    if 'offset' in transform:
        glyph.transform(offset_matrix(transform['offset']))

    if 'rescale_rel' in transform:
        baseline = transform.get('baseline_rel', default_baseline)
        scale    = transform['rescale_rel']
        apply_rescale(glyph, origin_point(baseline), scale)

    if 'offset_rel' in transform:
        glyph.transform(offset_matrix(transform['offset_rel']))

try:
    font.generate(args.dst_font)
except:
    stderr.write("Cannot write to file %s\n" % args.dst_font)
    sys.exit(1)
