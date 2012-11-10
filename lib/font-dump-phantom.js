
'use strict';

/*global phantom, $, Raphael*/
var fs = require('fs');
var system = require('system');

var svg_template =
  '<svg height="${height}px" width="${width}px"' +
  ' xmlns="http://www.w3.org/2000/svg">' + "\n" +
  '  <g>' + "\n" +
  '    <path d="${path}" />' + "\n" +
  '  </g>' + "\n" +
  '</svg>';

var GLYPH_SIZE = 1000;

var page = require('webpage').create();

// jquery initialized only on html page
page.content = '<html><body></body></html>';
page.injectJs("../vendor/jquery-1.8.2.min.js");
page.injectJs("../vendor/raphael.js");

page.onConsoleMessage = function (msg) {
  return console.log(msg);
};

page.onError = function (msg, trace) {
  var msgStack = ["ERROR: " + msg];
  if (trace) {
    msgStack.push("TRACE:");
    trace.forEach(function (t) {
      msgStack.push(" -> " + t.file + ": " + t.line + (t.function ? " (in function '" + t.function + "')" : ""));
    });
  }
  console.error(msgStack.join("\n"));
  phantom.exit(1);
};

//
//
// Main :)
//
//

if (system.args.length !== 2) {
  console.log('Bad arguments');
  phantom.exit(1);
}

var params_file = system.args[1]
  , f
  , params = {}
  , font;

try {
  f = fs.open(params_file, "r");
  params = JSON.parse(f.read());
  f.close();
} catch (e) {
  console.log('Cannot open ' + params_file + ': ' + e);
  phantom.exit(1);
}

// read source font
//
try {
  f = fs.open(params.src_font, "r");
  font = f.read();
  f.close();
} catch (e) {
  console.log('Cannot open ' + params.src_font + ': ' + e);
  phantom.exit(1);
}

// Patch glyph codes spelling
//
font = font.replace(/unicode="&#x([a-f0-9]+);"/g, 'unicode="0x$1"');

// fetch glyphs
//
var glyphs = page.evaluate(function (font, glyph_size, params) {

  var R = Raphael
    , ascent = parseInt($(font).find('font-face').attr('ascent'), 10)
    , descent = -parseInt($(font).find('font-face').attr('descent'), 10)
    , font_horiz_adv_x = $(font).find('font').attr('horiz-adv-x')

  var matrix
    , result = []

  $(font).find('glyph').each(function () {

    var path = $(this).attr('d');
    var width = $(this).attr('horiz-adv-x') || font_horiz_adv_x
      , height = ascent + descent
      , scale = glyph_size / height

    var unicode = $(this).attr('unicode');

    if (!unicode) {
      return;
    }

    // if 1 char -> direct definition
    if (1 == unicode.length) {
      unicode = unicode.charCodeAt(0);
    } else {
      unicode = parseInt($(this).attr('unicode'), 16);
    }

    if (!unicode) {
      return;
    }

    var name = $(this).attr('name') || unicode.toString(16);

    if (!name) {
      return;
    }

    // Build final matrix, to transform in single step
    // (!) chained matrixes should go in reverce order

    matrix = R.matrix();

    // mirror vertically
    //
    matrix.scale(1, -1, 0, glyph_size / 2);

    // scale to default height
    //
    matrix.scale(scale);
    height = height * scale;
    width = width * scale;

    // compensate descent shift
    //
    matrix.translate(0, descent);

    path = R.mapPath(path, matrix);

    //
    // Now main normalisation done.
    // Follow with additional tweaks & cleanup
    //

    // Calculate bounding box for image
    //
    var bbox = R.pathBBox(path);

    // Skip empty glyphs (when real width ot height = 0)
    //
    if (!bbox.width || !bbox.height) {
      return;
    }

    // trim width, if required
    //
    if (params.hcrop && (bbox.width < width)) {
      matrix = R.matrix();
      matrix.translate(-bbox.x, 0);
      path = R.mapPath(path, matrix);
      width = bbox.width;
    }

    // center glyphs vertically, if requested
    //
    if (params.vcenter) {
      // Realign
      matrix = R.matrix();
      matrix.translate(0, ((height - bbox.height) / 2) - bbox.y);
      path = R.mapPath(path, matrix);
    }




    // convert coordinates back to relative, to reduce size
    //
    path = R.pathToRelative(path);

    // replace commas with spaces, to make inscape understand such path
    //
    path = String(path).replace(/,/g, ' ');

    result.push({
      unicode: unicode,
      name: name,
      path: path,
      width: width,
      height: height
    });
  });

  return result;
}, font, GLYPH_SIZE, params);

// Serialaze calculated glyphs and sabe to disk
//
f = fs.open(params_file + '.out.json', "w");
f.writeLine(JSON.stringify(glyphs));
f.close();

// save glyph files
/*glyphs.forEach(function (glyph) {
  f = fs.open(params.glyphs_dir + '/' + glyph.name + '.svg', "w");
  f.writeLine(
    svg_template
    .replace('${path}', glyph.path)
    .replace('${width}', glyph.width)
    .replace('${height}', glyph.height)
  );
  f.close();
});
*/

phantom.exit();
