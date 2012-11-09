#!/usr/bin/env node

'use strict';

var fs = require('fs');
var path = require('path');
var childProcess = require('child_process');
var crypto = require('crypto');

var _ = require('underscore');
var yaml = require('yamljs');
var fstools = require('fs-tools');

var phantomjs = require('phantomjs');
var binPath = phantomjs.path;

var svg_template =
  '<svg height="${height}px" width="${width}px"' +
  ' xmlns="http://www.w3.org/2000/svg">' + "\n" +
  '  <g>' + "\n" +
  '    <path d="${path}" />' + "\n" +
  '  </g>' + "\n" +
  '</svg>';

var ArgumentParser = require('argparse').ArgumentParser;

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


var args = parser.parseArgs();

var params = {
  src_font: args.src_font,
  glyphs_dir: args.glyphs_dir,
  hcrop: args.hcrop,
  vcenter: args.vcenter,
};

//console.log(config.toObject());
//process.exit();

var tmp_dir = fstools.tmpdir('/tmp/font-dumpXXX');
var tmp_config_file = path.join(tmp_dir, 'config.json');

fs.mkdirSync(tmp_dir);
fs.writeFileSync(tmp_config_file, JSON.stringify(params));

var childArgs = [
  path.join(__dirname, '../lib/font-dump-phantom.js'),
  tmp_config_file
];

childProcess.execFile(binPath, childArgs, function (err, stdout, stderr) {
  if (err) {
    console.log(err);
    fstools.removeSync(tmp_dir);
    process.exit(1);
  }

  console.log(stdout);

  // Load generated glyphs from json output
  var glyphs = require(path.join(tmp_dir, 'config.json.out.json'));

  fstools.removeSync(tmp_dir);

  var config
    , diff = [];
  
  if (args.config) {
    config = yaml.load(args.config);
  }

  console.log('Writing output:\n\n');

  _.each(glyphs, function(glyph) {

    var exists
      , glyph_out = {};

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
      .replace('${width}', glyph.width)
      .replace('${height}', glyph.height);

    if (exists) {
      // glyph exists in config, but we forced dump
      fs.writeFileSync(path.join(params.glyphs_dir, (exists.file || exists.css) + '.svg'), glyph.svg);
      console.log((glyph.unicode.toString(16)) + ' - Found, but override forced');
      return;
    }

    // Completely new glyph
    //
    console.log((glyph.unicode.toString(16)) + ' - NEW glyph, writing...');

    glyph_out = {
      css: glyph.name,
      code: '0x' + glyph.unicode.toString(16),
      uid: crypto.randomBytes(16).toString('hex'),
      search: []
    }

    fs.writeFileSync(path.join(params.glyphs_dir, glyph.name + '.svg'), glyph.svg);

    diff.push(glyph_out);
  });

  // Create config template for new glyphs, if option set
  if (args.diff_config) {
    fs.writeFileSync(args.diff_config, yaml.stringify({glyphs: diff}, 10, 2));
  }
});
