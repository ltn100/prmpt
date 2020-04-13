#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

# Import external modules
import shlex
import re


class Lexer(shlex.shlex):
    """ A lexer to split tokens in a prompty script.

    Usage: l = Lexer("\\my\\amazing{}function")
    renders an iterable object, l, which will generate:
    ['\\my' , '\\amazing', '{', '}', 'function']

    Inherits usage from shlex
    https://docs.python.org/2/library/shlex.html
    """
    SPECIAL_CHARS = "%\\{}[] \t\n\r"
    COMMENT_CHAR = "%"

    def __init__(self, instream):
        instream = self.fix_comments(instream)
        instream = self.fix_line_numbers(instream)

        shlex.shlex.__init__(self, instream=instream)
        ascii_char_set = set([chr(i) for i in range(128)])
        # Discard special chars
        for char in self.SPECIAL_CHARS:
            ascii_char_set.discard(char)
        self.wordchars = ''.join(ascii_char_set)
        self.commenters = self.COMMENT_CHAR

    @staticmethod
    def fix_comments(instream):
        """Fix for bug where newline at end of comment gets treated
        as part of the comment (causing 'A\n#comment\nB' to be rendered
        as 'AB' instead of the intended 'A,B').
             http://bugs.python.org/issue7089

        This works by ensuring there is always whitespace between the
        last 'real' character and the comment character.
        """
        return re.sub(Lexer.COMMENT_CHAR,
                      " " + Lexer.COMMENT_CHAR,
                      instream)

    @staticmethod
    def fix_line_numbers(instream):
        """Fix broken line number reporting by ensuring that every line
        has a trailing whitespace character
        """
        return re.sub(r"([\r]?)\n", r" \1\n", instream)
