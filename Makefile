#####################################################
# python-make                                       #
# ===========                                       #
#                                                   #
# This is a simple Makefile wrapper to map 'make'   #
# ulility commands to python 'setup.py' commands.   #
# So you can, for example, use commands like this   #
# from the command line:                            #
#                                                   #
#    make                                           #
#    make test                                      #
#    make install                                   #
#    make clean                                     #
#                                                   #
# For more information, and for the latest version, #
# see: https://github.com/ltn100/python-make        #
#####################################################
PYTHON	?= python
TWINE	?= twine
SETUP	:= setup.py

.PHONY: all
all: build

.PHONY: build
build:
	$(PYTHON) $(SETUP) sdist bdist_wheel

.PHONY: upload
upload: clean build
	$(TWINE) $@ dist/*

# Pass-through targets dependant on 'build' target
.PHONY: install test
install test: build
	$(PYTHON) $(SETUP) $@

.PHONY: docs
docs:
	$(PYTHON) $(SETUP) build_sphinx && \
	xdg-open build/sphinx/html/index.html

# Bespoke targets...
.PHONY: clean
clean:
	$(PYTHON) $(SETUP) $@
	rm -rf build dist

# Aliases...
.PHONY: check
check: test
