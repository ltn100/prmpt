#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:

# Import external modules
import shlex

class Lexer(shlex.shlex):
    def __init__(self, instream):
        shlex.shlex.__init__(self, instream=instream.replace('\n','\n\n'))
        self.wordchars = self.wordchars + r":;#~@-_=+*/?'!$^&()|<>.," + '"'
        self.commenters = '%'