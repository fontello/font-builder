#!/usr/bin/env node


'use strict';


// stdlib
var path = require('path');


// 3rd-party
var ArgumentParser = require('argparse').ArgumentParser;
var yaml = require('js-yaml');
var _ = require('underscore');


////////////////////////////////////////////////////////////////////////////////


var cli = new ArgumentParser({
  prog:     'mincer',
  version:  require('../package.json').version,
  addHelp:  true
});


cli.addArgument(['files'], {
  help:     'Config file(s) to validate',
  metavar:  'FILE',
  nargs:    '+'
});


////////////////////////////////////////////////////////////////////////////////


function findDuplicates(arr, key) {
  var processed = Object(null);

  // group values by key
  arr.forEach(function (o) {
    var k = o[key];

    if (!processed[k]) {
      processed[k] = [];
    }

    processed[k].push(o);
  });

  // return only those who have
  // more than one element in group
  return _.filter(processed, function (o) {
    return 1 < o.length;
  });
}


////////////////////////////////////////////////////////////////////////////////


var found_glyphs  = [];
var args          = cli.parseArgs();


////////////////////////////////////////////////////////////////////////////////


args.files.forEach(function (filename) {
  var config;

  try {
    config = require(path.resolve(filename));
  } catch (err) {
    console.log('ERROR: Failed read file ' + filename);
    console.log(err.stack || String(err));
    process.exit(1);
  }

  if (!config.glyphs || !config.glyphs.length) {
    console.log('ERROR: No glyphs in config ' + filename);
    process.exit(1);
  }

  //
  // push glyphs into "all known glyphs" list
  //

  found_glyphs = found_glyphs.concat(config.glyphs.map(function (glyph) {
    glyph.filename = filename;
    return glyph;
  }));

  //
  // check for duplicate uid's
  //

  findDuplicates(config.glyphs, 'uid').forEach(function (duplicates) {
    console.log('Duplicate uid <' + duplicates[0].uid + '> (in: ' + filename + ')');

    duplicates.forEach(function (g) {
      console.log('  - ' + JSON.stringify({
        code_int: g.code,
        code_hex: '0x' + g.code.toString(16)
      }));
    });
  });

  //
  // check for duplicate name's
  //

  findDuplicates(config.glyphs, 'css').forEach(function (duplicates) {
    console.log('Duplicate css <' + duplicates[0].css + '> (in: ' + filename + ')');

    duplicates.forEach(function (g) {
      console.log('  - ' + JSON.stringify({
        code_int: g.code,
        code_hex: '0x' + g.code.toString(16)
      }));
    });
  });
});

//
// Search for duplicates across multiple configs
//

if (1 < args.files.length) {

  //
  // check for duplicate uid's
  //

  findDuplicates(found_glyphs, 'uid').forEach(function (duplicates) {
    console.log('Duplicate uid <' + duplicates[0].uid + '>');

    duplicates.forEach(function (g) {
      console.log('  - ' + JSON.stringify({
        code_int: g.code,
        code_hex: '0x' + g.code.toString(16),
        filename: g.filename
      }));
    });
  });

  //
  // check for duplicate name's
  //

  findDuplicates(found_glyphs, 'css').forEach(function (duplicates) {
    console.log('Duplicate css <' + duplicates[0].css + '>');

    duplicates.forEach(function (g) {
      console.log('  - ' + JSON.stringify({
        code_int: g.code,
        code_hex: '0x' + g.code.toString(16),
        filename: g.filename
      }));
    });
  });

}
