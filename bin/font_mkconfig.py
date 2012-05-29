#!/usr/bin/env python

import argparse
import yaml
import fontforge
import string
import random

parser = argparse.ArgumentParser(description='Font config generation tool')
parser.add_argument('-i', '--src_font', type=str, required=True,
    help='Input font')
parser.add_argument('-c', '--config', type=str, required=True,
    help='Output config')

def get_attrs(font, attrs):
    result = {}
    for a in attrs:
        result[a] = getattr(font, a)
    return result

args = parser.parse_args()

try:
    font = fontforge.open(args.src_font)
except:
    stderr.write("Error: fontforge can't open source font from %s" % args.src_font)
    sys.exit(1)


font_attrs = [
    "version",
    "fontname",
    "fullname",
    "familyname",
    "copyright",
    "ascent",
    "descent",
    "weight"
]

# add beginning part
config = """

meta:
  author:
  homepage:
  email:
  licence:
  licence_url:

  css_prefix: "icon-"
  columns: 4

transform:
  baseline: 0.5
  rescale: 1.0
  offset: 0.0

font:
  version: "{version}"

  # use !!!small!!! letters a-z, or Opera will fail under OS X
  # fontname will be also used as file name.
  fontname: {fontname}

  fullname: {fullname}
  familyname: {familyname}

  copyright: {copyright}

  ascent: {ascent}
  descent: {descent}
  weight: {weight}


""".format(**get_attrs(font, font_attrs))

# add glyphs part
config += """glyphs:
"""

glyph_template = """
  - css: glyph{i}
    code: {code}
    uuid: {uuid}
    from: {code}
    search:
"""

for i, glyph in enumerate(font.glyphs()):
    if glyph.unicode == -1:
        continue

    code = '0x%04x' % glyph.unicode

    uuid = ''.join(random.choice(string.ascii_lowercase+string.digits)
            for x in range(32))

    config += glyph_template.format(i=i, code=code, uuid=uuid)

try:
    open(args.config, "w").write(config)
except IOError as (errno, strerror):
    stderr.write("Cannot write %s: %s\n" % (args.config, strerror))
    sys.exit(1)

