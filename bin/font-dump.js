
'use strict';

/*global phantom, $, Raphael*/
var fs = require('fs');
var system = require('system');

var glyph_template = '<svg width="1000" height="1000"' +
                      ' viewBox="0 0 1000 1000"' +
                      ' xmlns="http://www.w3.org/2000/svg">' + "\n" +
                      '  <g>' + "\n" +
                      '    <path fill="currentColor" d=":path_placehoder:" />' + "\n" +
                      '  </g>' + "\n" +
                      '</svg>';

var GLYPH_SIZE = 1000;

var page = require('webpage').create();

// jquery initialized only on html page
page.content = '<html><body></body></html>';
page.injectJs("../vendor/jquery-1.8.2.min.js");
page.injectJs("../vendor/raphael-min.js");

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

var src_font,
    glyphs_dir;

// simple, stupid argument parser
// FIXME try to use argparse
if (system.args.length === 1) {
  console.log('Too few arguments');
  phantom.exit(1);
} else {
  system.args.forEach(function (arg, i) {
    if (arg === '-i' || arg === '--src_font') {
      src_font = system.args[i + 1];
      return;
    }
    if (arg === '-o' || arg === '--glyphs_dir') {
      glyphs_dir = system.args[i + 1];
      return;
    }
  });
}
if (!src_font || !glyphs_dir) {
  console.log('Check arguments');
  phantom.exit(1);
}


// read source font
try {
  var f = fs.open(src_font, "r");
  var font = f.read();
} catch (e) {
  console.log('Cannot open ' + src_font + ': ' + e);
  phantom.exit(1);
}

// Path glyph codes spelling
font = font.replace(/unicode="&#x([a-f0-9]+);"/g, 'unicode="0x$1"');

// fetch glyphs
var glyphs = page.evaluate(function (font, glyph_size) {
  var ascent = parseInt($(font).find('font-face').attr('ascent'), 10);
  // descent has negative value
  var descent = -parseInt($(font).find('font-face').attr('descent'), 10);
  var font_horiz_adv_x = -$(font).find('font').attr('descent');

  var result = [];
  $(font).find('glyph').each(function () {
    var rules, bb, tfm, scale;
    var name, unicode;

    var path = $(this).attr('d');
    var horiz_adv_x = $(this).attr('horiz-adv-x');
    // if gliph dosen't have own horiz-adv-x, then use font horiz-adv-x
    if (!horiz_adv_x) {
      horiz_adv_x = font_horiz_adv_x;
    }

    unicode = parseInt($(this).attr('unicode'), 16);
    if (!unicode) {
      return;
    }

    if (undefined !== $(this).attr('name')) {
      name = $(this).attr('name');
    }
    else {
      // if glyph name dosen't set then use unicode as file name
      name = unicode.toString(16);
    }
    // trim name
    if ('string' === typeof(name)) {
      name = name.replace(/^\s+|\s+$/g, "");
    }
    if (undefined === name || null === name ||
        '' === name) {
      return;
    }

    //bb = Raphael.pathBBox(d);
    scale = glyph_size / (ascent + descent);

    //tfm = 's' + scale + ',-' + scale;
    rules = [
      // horisontal align
      't' + ((glyph_size - horiz_adv_x) / 2) + ',0',
      // vertical align
      't0,' + descent,
      // scale
      's' + scale + ',-' + scale
    ];
    tfm = rules.join('');

    result.push({
      name: name,
      path: Raphael.transformPath(path, tfm)
    });
  });

  return result;
}, font, GLYPH_SIZE);

// save glyph files
glyphs.forEach(function (glyph) {
  f = fs.open(glyphs_dir + '/' + glyph.name + '.svg', "w");
  f.writeLine(glyph_template.replace(':path_placehoder:', glyph.path));
  f.close();
});

phantom.exit();
