'use strict';

var fs = require('fs'),
    sax = require('sax');

module.exports = function(params, callback) {

    fs.readFile(params.src_font, function(err, data) {

        if (err) {
            throw err;
        }

        data = data.toString();

        var result = [],
            path,
            width,
            height,
            scale,
            fontHorizAdvX,
            ascent,
            descent,
            unicode,
            name,
            transform,
            glyphSize = 1000,
            parser = sax.parser(true/* strict */, {
                trim: true,
                normalize: true,
                lowercase: true,
                xmlns: true,
                position: false
            });

        parser.onopentag = function(node) {

            if (Object.keys(node.attributes).length) {

                // get horiz-adv-x from <font>
                if (node.name === 'font' && node.attributes['horiz-adv-x']) {
                    fontHorizAdvX = node.attributes['horiz-adv-x'].value;
                }

                // get ascent from <font-face>
                if (node.name === 'font-face' && node.attributes['ascent']) {
                    ascent = +node.attributes['ascent'].value;
                }

                // get descent from <font-face>
                if (node.name === 'font-face' && node.attributes['descent']) {
                    descent = -node.attributes['descent'].value;
                }

                // each <glyph>
                if (node.name === 'glyph' && node.attributes['d']) {

                    // path
                    path = node.attributes['d'].value;

                    // width
                    width = node.attributes['horiz-adv-x'] ?
                                node.attributes['horiz-adv-x'].value :
                                fontHorizAdvX;

                    // height
                    height = ascent + descent;

                    // scale
                    scale = glyphSize / height;

                    // unicode
                    if (!node.attributes['unicode']) return;

                    // patch glyph codes spelling
                    unicode = node.attributes['unicode'].value.replace(/unicode="&#x([a-f0-9]+);"/g, 'unicode="0x$1"');

                    // if 1 char -> direct definition
                    unicode = unicode.length === 1 ?
                                unicode.charCodeAt(0) :
                                parseInt(unicode, 16);

                    // name
                    name = node.attributes['glyph-name'] ?
                                node.attributes['glyph-name'].value :
                                unicode.toString(16);

                    // vertical mirror
                    transform = 'translate(0 ' + (glyphSize / 2) + ') scale(1 -1) translate(0 ' + (-glyphSize / 2) + ')';
                    // scale
                    transform += ' scale(' + scale + ')';
                    // descent shift
                    transform += ' translate(0 ' + descent + ')';

                    width = width * scale;
                    height = height * scale;

                    result.push({
                        path: path,
                        transform: transform,
                        unicode: unicode,
                        name: name,
                        width: width,
                        height: height
                    });

                }

            }

        }

        parser.onend = function() {

            callback(result);

        }

        parser.write(data).close();

    });

}
