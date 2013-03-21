PREFIX          ?= /usr/local


TTF2EOT_BIN     := ./support/ttf2eot/ttf2eot
TTFAUTOHINT_BIN := ./support/ttfautohint/frontend/ttfautohint

PLATFORM        := $(shell uname)

support:
	$(MAKE) $(TTF2EOT_BIN)
	$(MAKE) $(TTFAUTOHINT_BIN)

# ttfautohint
# ttf2eot

support-install: support
	cp $(TTFAUTOHINT_BIN) $(PREFIX)/bin
	cp $(TTF2EOT_BIN) $(PREFIX)/bin

support-osx: 
	@if [[ $(PLATFORM) = "Darwin" ]]; then \
		brew install ttf2eot ; \
		brew install ttfautohint ; \
	else \
		echo "this target is only for OS X" >&2 ; \
		exit 128 ; \
	fi

$(TTF2EOT_BIN):
	cd ./support/ttf2eot \
		&& $(MAKE) ttf2eot


$(TTFAUTOHINT_BIN):
	git submodule init support/ttfautohint
	git submodule update support/ttfautohint
	cd ./support/ttfautohint && \
		git submodule init && \
		git submodule update && \
		./bootstrap ; \
		./configure --with-qt=no --with-doc=no && make


dev-deps:
	@if [[ $(PLATFORM) = "Darwin" ]]; then \
		brew install python ; \
		brew install fontforge ; \
		sudo ln -s /opt/X11/lib/libfreetype.6.dylib /usr/local/lib/libfreetype.6.dylib ; \
		brew tap sampsyo/py ; \
		brew install PyYAML ; \
		brew install automake autoconf libtool ; \
		pip -q install pystache argparse ; \
	else \
		if test 0 -ne `id -u` ; then \
			echo "root privileges are required" >&2 ; \
			exit 128 ; \
		fi ; \
		apt-get -qq install \
			fontforge python python-fontforge libfreetype6-dev \
			python-yaml python-pip \
			build-essential autoconf automake libtool ; \
		pip -q install pystache argparse ; \
	fi
.PHONY: support
