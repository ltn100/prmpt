#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:

# Import external modules
import shlex

class Lexer(shlex.shlex):
    def __init__(self, instream):
        shlex.shlex.__init__(self, instream=instream.replace('\n','\n\n'))
        asciiCharSet = set([chr(i) for i in range(128)])
        # Discard special chars
        for char in "%\\{}[] \t\n\r":
            asciiCharSet.discard(char)
        self.wordchars = ''.join(asciiCharSet)
        self.commenters = '%'
        
    def lineNo(self):
        return (self.lineno+1)/2