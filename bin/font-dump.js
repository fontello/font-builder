#!/usr/bin/env node

'use strict';

var fs = require('fs');
var path = require('path');

var Xml2js = require('xml2js');
var async = require('async');
var _ = require('underscore');

var ArgumentParser = require('argparse').ArgumentParser;


var glyph_template = '<svg width="1000" height="1000"' +
                     ' viewBox="0 0 1000 1000"' +
                     ' xmlns="http://www.w3.org/2000/svg">' + "\n" +
                     '  <g>' + "\n" +
                     '    <path fill="currentColor" d=":d_placehoder:" />' + "\n" +
                     '  </g>' + "\n" +
                     '</svg>';


// fetch glyph info from general object
//
function prepare_glyphs(glyphs) {
  var result = [];
  glyphs.forEach(function (glyph) {
    var glyph_name = glyph['$']['glyph-name'] ? glyph['$']['glyph-name'] : glyph['$']['unicode'];
    if (_.isString(glyph_name)) {
      glyph_name = glyph_name.replace(/^\s+|\s+$/g, "");
    }
    if (_.isEmpty(glyph_name)) {
      return;
    }

    result.push({
      name: glyph_name,
      d: glyph['$']['d']
    });
  });
  return result;
}

var parser = new ArgumentParser({
  version: '0.0.1',
  addHelp: true,
  description: 'Dump glyphs from font'
});
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

var args = parser.parseArgs();
if (!fs.existsSync(args.src_font)) {
  console.log('File ' + args.src_font + ' not found');
  process.exit(1);
}

var parser = new Xml2js.Parser();
fs.readFile(args.src_font, function (err, data) {
  data = data.toString().replace(/unicode="&#x([a-f0-9]+);"/g, 'unicode="0x$1"');

  parser.parseString(data, function (err, result) {
    var font_horiz_adv_x = result.svg.defs[0].font[0]['$']['horiz-adv-x'];

    var glyphs = prepare_glyphs(result.svg.defs[0].font[0].glyph);
    async.forEachSeries(glyphs, function (glyph, next_glyph) {
      var file_path = path.join(args.glyphs_dir, glyph.name + '.svg');
      // FIXME need some magic
      var data = glyph_template.replace(':d_placehoder:', glyph.d);
      fs.writeFile(file_path, data, next_glyph);
    }, function (err) {
      if (err) {
        console.log(err);
        process.exit(1);
      }
      console.log('Done');
    });
  });
});
