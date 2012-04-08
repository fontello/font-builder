#!/usr/bin/env python

import sys
import argparse
import yaml
import fontforge


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
# [(from_code1, to_code1), (from_code2, to_code2), ...]
def get_remap_config(config):
    def get_remap_item(glyph):
        name, glyph = glyph.items()[0]
        return (glyph.get('from', glyph['code']), glyph['code'])
    return [get_remap_item(glyph) for glyph in config['glyphs']]


if __name__ == '__main__':
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
        error("Cannot open %s: %s\n" % (args.config, strerror))
        sys.exit(1)
    except yaml.YAMLError, e:
        if hasattr(e, 'problem_mark'):
            mark = e.problem_mark
            error("YAML parser error in file %s at line %d, col %d\n" %
                (args.config, mark.line + 1, mark.column + 1))
        else:
            error("YAML parser error in file %s: %s\n" % (args.config, e))
        sys.exit(1)

    remap_config = get_remap_config(config)

    from_codes, to_codes = zip(*remap_config)

    # validate config: 'from:' codes
    dups = get_dups(from_codes)
    if len(dups) > 0:
        error("Error in file %s: glyph codes aren't unique:\n" % args.config)
        for k in sorted(dups.keys()):
            error("Duplicate 'from:' 0x%04x\n" % k)
        sys.exit(1)

    # validate config: 'code:' codes
    dups = get_dups(to_codes)
    if len(dups) > 0:
        error("Error in file %s: glyph codes aren't unique:\n" % args.config)
        for k in sorted(dups.keys()):
            error("Duplicate 'code:' 0x%04x\n" % k)
        sys.exit(1)

    try:
        font = fontforge.open(args.src_font)
    except:
        sys.exit(1)

    # tmp font for cut()/paste()
    tmp_font = fontforge.font()
    tmp_font.encoding = 'UnicodeFull'

    # set font encoding so we can select any unicode code point
    font.encoding = 'UnicodeFull'

    for from_code, to_code in remap_config:
        try:
            font[from_code]
        except TypeError:
            error("Warning: no such glyph in the source font (code=0x%04x)\n" %
                from_code)
            continue

        if from_code == to_code:
            continue

        font.selection.select(("unicode",), from_code)
        font.cut()
        tmp_font.selection.select(("unicode",), to_code)
        tmp_font.paste()

    for from_code, to_code in remap_config:
        if from_code == to_code:
            continue

        tmp_font.selection.select(("unicode",), to_code)
        tmp_font.cut()
        font.selection.select(("unicode",), to_code)
        font.paste()

    try:
        font.generate(args.dst_font)
    except:
        error("Cannot write to file %s\n" % args.dst_font)
        sys.exit(1)

    sys.exit(0)
