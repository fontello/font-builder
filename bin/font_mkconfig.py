#!/usr/bin/env python

import argparse
import yaml
import fontforge

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

font = fontforge.open(args.src_font)

# add comment
config = """---
# This is configuration file for font builder and other support scripts.
# Format is descriped below.
#
#
# css-prefix: "icon-"             # prefix for css-generated classes
# demo-columns: 4                 # used for html demo page generation
#
# font:                           # all vars from here will be used as font
#                                 # params in fontforge
#                                 # http://fontforge.sourceforge.net/python.html
#   version: "1.0"
#
#   # use !!!small!!! letters a-z, or Opera will fail under OS X
#   # fontname will be also used as file name.
#   fontname: myfont
#
#   fullname: MyFont
#   familyname: Myfont
#
#   copyright: Copyright (C) 2012 by xxxxxxxx
#
#   ascent: 1638
#   descent: 410
#   weight: Medium
#
#
#
# # Optional. You can apply global resize + offset to all font glyphs.
# # Param values ar 0..1, where 1 = 100%. 
# #
# transform:
#   baseline: 0.2                 # baseline for rescale. Default value calculated
#                                 # from ascent/decsent
#   rescale: 0.68                 # rescale glyphs and center around baseline
#   offset: -0.1                  # shift up/down
#
# glyphs:
#   - glyph1_file:                # file name, without extention
#       from: 0xNNN               # Symbol code 0x - hex, original
#       code: 0xNNN               # Symbol code 0x - hex, remapped
#       css: icon-gpyph1-name     # For generated CSS
#       search: [word1, word2]    # Search aliases (array). CSS name will be
#                                 # included automatically
#
#       transform:                # personal glyph transformation.
#         rescale_rel: 0.9        # *_rel - applyed after global.
#         offset: 0.2             # without *_rel - override global
#
################################################################################
#
# Mapping rules:
#
# 1. Downshift 1Fxxx -> Fxxx, because 1Fxxx codes not shown in Chrome/Opera
#
"""

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
config += """

css-prefix: "icon-"
demo-columns: 4

transform:
  rescale: 1.0
  offset: 0.0

font:
  version: "{version}"

  # use !!!small!!! letters a-z, or Opera will fail under OS X
  # fontname will be also used as file name.
  fontname: "{fontname}"

  fullname: "{fullname}"
  familyname: "{familyname}"

  copyright: "{copyright}"

  ascent: {ascent}
  descent: {descent}
  weight: "{weight}"


""".format(**get_attrs(font, font_attrs))

# add glyphs part
config += """glyphs:
"""

for i, glyph in enumerate(font.glyphs()):
    if glyph.unicode == -1:
        continue

    code = '0x%04x' % glyph.unicode

    config += """
  - glyph{i}:
      code: {code}
""".format(i=i, code=code)


open(args.config, "w").write(config)
