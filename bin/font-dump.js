#!/usr/bin/env node

'use strict';

var fs = require('fs');
var path = require('path');
var childProcess = require('child_process');

var FsTools = require('fs-tools');

var phantomjs = require('phantomjs');
var binPath = phantomjs.path;

var ArgumentParser = require('argparse').ArgumentParser;

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

var config = {
  src_font: args.src_font,
  glyphs_dir: args.glyphs_dir
};

var tmp_dir = FsTools.tmpdir('/tmp/font-dumpXXX');
var tmp_config_file = path.join(tmp_dir, 'config.json');

fs.mkdirSync(tmp_dir);
fs.writeFileSync(tmp_config_file, JSON.stringify(config));

var childArgs = [
  path.join(__dirname, '../lib/font-dump-phantom.js'),
  tmp_config_file
];

childProcess.execFile(binPath, childArgs, function (err, stdout, stderr) {
  if (err) {
    console.log(err);
    FsTools.remove(tmp_dir, function (err) {
      if (err) {
        console.log(err);
      }
      process.exit(1);
    });
  }
  console.log(stdout);
  FsTools.remove(tmp_dir, function (err) {
    if (err) {
      console.log(err);
      process.exit(1);
    }
    console.log('Done');
  });
});
