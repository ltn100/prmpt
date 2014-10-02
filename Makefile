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
SETUP	:= setup.py

.PHONY: all
all: build

# Simple pass-through targets
.PHONY: build sdist bdist rpm
build sdist bdist rpm:
	$(PYTHON) $(SETUP) $@

# Pass-through targets dependant on 'build' target
.PHONY: install test
install test: build
	$(PYTHON) $(SETUP) $@

# Bespoke targets...
.PHONY: clean
clean:
	$(PYTHON) $(SETUP) $@
	rm -rf build dist

# Aliases...
.PHONY: check
check: test
