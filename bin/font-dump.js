#!/usr/bin/env node

'use strict';

var fs = require('fs');
var path = require('path');
var crypto = require('crypto');
var _ = require('underscore');
var yaml = require('yamljs');
var font_dump = require('../lib/font-dump');
var Svgo = require('svgo');
var ArgumentParser = require('argparse').ArgumentParser;

var svg_template =
    '<svg height="${height}px" width="${width}px"' +
      ' xmlns="http://www.w3.org/2000/svg">' + "\n" +
      '    <path d="${path}" transform="${transform}" />' + "\n" +
    '</svg>';


var parser = new ArgumentParser({
  version: '0.0.1',
  addHelp: true,
  description: 'Dump glyphs from font'
});
parser.addArgument(
  ['--hcrop'],
  {
    help: 'Crop free space from left and right',
    action: 'storeTrue'
  }
);
parser.addArgument(
  ['--vcenter'],
  {
    help: 'Realign glyphs vertically',
    action: 'storeTrue'
  }
);
parser.addArgument(
  [ '-c', '--config' ],
  {
    help: 'Font config file'
  }
);
parser.addArgument(
  [ '-i', '--src_font' ],
  {
    help: 'Source font path',
    required: true
  }
);
parser.addArgument(
  [ '-o', '--glyphs_dir' ],
  {
    help: 'Glyphs output folder',
    required: true
  }
);
parser.addArgument(
  [ '-d', '--diff_config' ],
  {
    help: 'Difference config output file'
  }
);
parser.addArgument(
  [ '-f', '--force' ],
  {
    help: 'Force override glyphs from config',
    action: 'storeTrue'
  }
);

var args = parser.parseArgs(),
    params = {
      src_font: args.src_font,
      glyphs_dir: args.glyphs_dir,
      hcrop: args.hcrop,
      vcenter: args.vcenter,
    };

font_dump(params, function(glyphs) {

  var config,
      diff = [],
      svgo = new Svgo();

  if (args.config) {
    config = yaml.load(args.config);
  }

  console.log('Writing output:\n\n');

  glyphs.forEach(function(glyph) {

    var exists,
        glyph_out = {};

    // if got config from existing font, then write only missed files
    if (config) {
      exists = _.find(config.glyphs, function(element) {
        //console.log('---' + element.from + '---' + glyph.unicode)
        return (element.from || element.code) == glyph.unicode;
      });

      if (exists && !args.force) {
        console.log((glyph.unicode.toString(16)) + ' exists, skipping');
        return;
      }
    }

    glyph.svg = svg_template
      .replace('${path}', glyph.path)
      .replace('${transform}', glyph.transform)
      .replace('${width}', glyph.width)
      .replace('${height}', glyph.height);

    if (exists) {
      // glyph exists in config, but we forced dump
      fs.writeFileSync(path.join(params.glyphs_dir, (exists.file || exists.css) + '.svg'), glyph.svg);
      console.log((glyph.unicode.toString(16)) + ' - Found, but override forced');
      return;
    }

    // Completely new glyph

    glyph_out = {
      css: glyph.name,
      code: '0x' + glyph.unicode.toString(16),
      uid: crypto.randomBytes(16).toString('hex'),
      search: []
    }

    console.log((glyph.unicode.toString(16)) + ' - NEW glyph, writing...');

    svgo.fromString(glyph.svg)
      .then(function(result) {
        fs.writeFile(path.join(params.glyphs_dir, glyph.name + '.svg'), result.data);
      })
      .done();

    diff.push(glyph_out);

  });

  // Create config template for new glyphs, if option set
  if (args.diff_config) {

    if (!diff.length) {
      console.log("No new glyphs, skip writing diff");
      return;
    }

    fs.writeFileSync(args.diff_config, yaml.stringify({glyphs: diff}, 10, 2));
  }

});
