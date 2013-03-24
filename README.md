Font Builder
============

Set of scripts to generate iconic fonts. Available operation:

- Building fonts from SVG images
- Bulk glyphs code change
- Transformations (resize/move glyphs)
- Making CSS/HTML from templates

This scripts are NOT indended to run standalone. See real usage example
in [fontello](https://github.com/fontello) repos:

- https://github.com/fontello/entypo
- https://github.com/fontello/awesome-uni.font
- https://github.com/fontello/iconic-uni.font
- https://github.com/fontello/websymbols-uni.font


Installation
------------

You MUST have node.js 0.8+ installed. In Ubuntu 12.04+, just clone repo and
run in command line:

    sudo make dev-deps
    make support
    sudo make support-install
    npm install

You can skip `support-install` step, if you don't need to install ttfautohint
& ttf2eot globally. 

### OS X

OS X users can use this, too. Make sure you have [Homebrew](http://mxcl.github.com/homebrew/) 
installed.

Then, run:
	
	make dev-deps
	make support-osx
	npm install

This installs Python, pip, and some other build dependencies. 
This _will_ globally install ttfautohint & ttf2eot.

Licence info
------------

Code (except `./support` folder) distributed under MIT licence.
`./support` folder contains 3d-party software, see README there.

(c) 2012 Vitaly Puzrin.

[Contributors](https://github.com/fontello/font-builder/contributors)

Special thanks to Werner Lemberg, author of [ttfautohint](http://www.freetype.org/ttfautohint/)
utility, used in this project.

