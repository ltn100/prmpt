#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from prmpt import lexer


class Parser(object):
    """ Parse an input stream by first passing it through the
    Lexer class. The lexer will yield a set of discrete tokens
    that can be iterated upon. Special tokens (like \\) need to
    be parsed allong with the tokens directly following them.

    The returned output is a list of dictionary items with a 'type'
    key set to one of:
        'function' : with the additional keys:
                'name' : the function name
                'args' : a list of other dictionaries to be nested
                'optargs' : a list of other dictionaries to be nested
        'literal' : a literal string, with the additional keys:
                'value' : the string itself

    Additionally, both types also receive the key:
                'lineno' : an integer type with the source line no.
    """
    def parse(self, instream):
        """ Run the input stream recursively through the atom
        and build a list of nested dictionary objects
        """
        lex = lexer.Lexer(instream)
        return self._atom(lex, lex.get_token())

    def _atom(self, lex, token):
        """ Recursive function to parse all tokens.
        """
        out = []

        while True:
            if not token:
                # End of tokens
                break
            if token == '\\':
                # Function
                name = lex.get_token()
                func = {'type': 'function',
                        'name': name,
                        'lineno': lex.lineno
                        }
                args = []
                optargs = []
                token = lex.get_token()
                while token in ['{', '[']:
                    # Arguments
                    arg = self._atom(lex, lex.get_token())

                    if token == '{':
                        args.append(arg)
                    elif token == '[':
                        optargs.append(arg)
                    token = lex.get_token()
                if args:
                    func['args'] = args
                if optargs:
                    func['optargs'] = optargs
                out.append(func)
                if not token:
                    break
            elif token in ['}', ']']:
                # End scope
                break
            else:
                # String literal
                out.append(
                    {'type': 'literal',
                     'value': token,
                     'lineno': lex.lineno
                     }
                )
                token = lex.get_token()

        return out
