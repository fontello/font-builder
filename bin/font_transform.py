#!/usr/bin/env python

import sys
import argparse
import yaml
import fontforge
import psMat


error = sys.stderr.write


# returns dict representing duplicate values of seq
# in seq = [1,1,2,3,3,3,3,4,5], out dict {1: 2, 3: 4}
def get_dups(seq):
    count = {}
    for s in seq:
        count[s] = count.get(s, 0) + 1
    dups = dict((k, v) for k, v in count.iteritems() if v > 1)
    return dups


# returns list of tuples:
# [(code1, {'rescale': 1.0, 'offset': 0.0}), (code2, {}), ...]
def get_transform_config(config):
    font_transform = config.get('transform', {})

    def get_transform_item(glyph):
        name, glyph = glyph.items()[0]
        transform = font_transform.copy()
        transform.update(glyph.get('transform', {}))
        return (glyph.get('code'), transform)

    return [get_transform_item(glyph) for glyph in config['glyphs']]


if __name__ == '__main__':
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
        error("Cannot open %s: %s\n" % (args.config, strerror))
        sys.exit(1)
    except yaml.YAMLError, e:
        if hasattr(e, 'problem_mark'):
            mark = e.problem_mark
            error("YAML parser error in file %s at line %d, col %d" %
                (args.config, mark.line + 1, mark.column + 1))
        else:
            error("YAML parser error in file %s: %s" % (args.config, e))
        sys.exit(1)

    transform_config = get_transform_config(config)

    codes = zip(*transform_config)[0]

    # validate config: codes
    dups = get_dups(codes)
    if len(dups) > 0:
        error("Error in file %s: glyph codes aren't unique\n" % args.config)
        for k in sorted(dups.keys()):
            error("Duplicate 'code:' 0x%04x\n" % k)
        sys.exit(1)

    transform_attrs = set([
        'baseline', 'rescale', 'offset',
        'baseline_rel', 'rescale_rel', 'offset_rel'
    ])
    has_transform = lambda x: transform_attrs & set(x)
    codes_to_transform = [i for i in transform_config if has_transform(i[1])]

    try:
        font = fontforge.open(args.src_font)
    except:
        sys.exit(1)

    # set ascent/descent
    ascent = config.get('font', {}).get('ascent', None)
    descent = config.get('font', {}).get('descent', None)

    if ascent:
        font.ascent = ascent
    if descent:
        font.descent = descent

    # set font encoding so we can select any unicode code point
    font.encoding = 'UnicodeFull'

    def apply_rescale(glyph, baseline, scale):
        # bbox: a tuple representing a rectangle (xmin,ymin, xmax,ymax)
        bbox = glyph.boundingBox()

        # center of bbox
        x, y = (bbox[0] + bbox[2]) / 2, (bbox[1] + bbox[3]) / 2

        # scale origin point
        sx, sy = 0, (font.ascent + font.descent) * baseline - font.descent

        # move scale origin point to (0, 0)
        translate_matrix = psMat.translate(-sx, -sy)
        glyph.transform(translate_matrix)

        # scale around (0, 0)
        scale_matrix = psMat.scale(scale)
        glyph.transform(scale_matrix)

        # scale width and vwidth as well
        glyph.width *= scale
        glyph.vwidth *= scale

        # move scale origin point back to its old position
        translate_matrix = psMat.translate(sx, sy)
        glyph.transform(translate_matrix)

    def apply_offset(glyph, offset):
        # shift the selected glyph vertically
        offset_y = offset * (font.ascent + font.descent)
        translate_matrix = psMat.translate(0, offset_y)
        glyph.transform(translate_matrix)

    default_baseline = font.descent / (font.ascent + font.descent)

    # apply transformations
    for code, transform in codes_to_transform:
        try:
            glyph = font[code]
        except TypeError:
            error("Warning: no such glyph (code=0x%04x)\n" % code)
            continue

        #font.selection.select(("unicode",), code)

        if 'rescale' in transform:
            baseline = transform.get('baseline', default_baseline)
            scale    = transform['rescale']
            apply_rescale(glyph, baseline, scale)

        if 'offset' in transform:
            apply_offset(glyph, transform['offset'])

        if 'rescale_rel' in transform:
            baseline = transform.get('baseline_rel', default_baseline)
            scale    = transform['rescale_rel']
            apply_rescale(glyph, baseline, scale)

        if 'offset_rel' in transform:
            apply_offset(glyph, transform['offset_rel'])

    try:
        font.generate(args.dst_font)
    except:
        error("Cannot write to file %s\n" % args.dst_font)
        sys.exit(1)

    sys.exit(0)
