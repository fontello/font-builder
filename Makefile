TTF2EOT_BIN     = ./support/ttf2eot/ttf2eot
TTFAUTOHINT_BIN = ./support/ttfautohint/frontend/ttfautohint


support:
	$(MAKE) $(TTF2EOT_BIN)
	$(MAKE) $(TTFAUTOHINT_BIN)


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
		./configure --without-qt && \
		make


dev-deps:
	@if test 0 -ne `id -u` ; then \
		echo "root priveledges are required" >&2 ; \
		exit 128 ; \
		fi
	apt-get -qq install \
		fontforge python python-fontforge libfreetype6-dev \
		python-yaml python-pip \
		build-essential \
		autoconf automake libtool
	pip -q install pystache argparse


.SILENT: dev-deps
.PHONY: support
