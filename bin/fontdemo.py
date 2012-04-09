#!/usr/bin/env python

import argparse
import yaml
import pystache
import math

parser = argparse.ArgumentParser(description='Generate file by mustache template')
parser.add_argument('-c', '--config', type=str, help='Config example: ../config.yml', required=True)
parser.add_argument('template', type=str, help='Mustache template')
parser.add_argument('output', type=str, help='Output file')

args = parser.parse_args()

data = yaml.load(open(args.config, 'r'))

glyphs = []

for glyph in data['glyphs']:

    # use giph name if css field is absent
    if (not 'css' in glyph):
        glyph['css'] = glyph['file']

    # code to unicode char
    glyph['chr'] = unichr(glyph['code']);

    # code to sting in hex format
    glyph['hex'] = "\\" + hex(glyph['code'])[2:]

    glyphs.append(glyph)

data['glyphs'] = glyphs

data['font.fontname'] = data['font']['fontname']
data['demo.css_prefix'] = data['demo']['css_prefix']

chunk_size = int(math.ceil(len(glyphs) / float(data['demo']['columns'])))
data['columns'] = [{'glyphs': glyphs[i:i + chunk_size]} for i in range(0, len(glyphs), chunk_size)]

template = open(args.template, 'r').read()

output = pystache.render(template, data).encode('utf-8');

f = open(args.output, 'w')
f.write(output)
