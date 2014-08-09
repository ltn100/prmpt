#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:

import lexer

class Parser(object):
    @staticmethod
    def _guardedNext(lex):
        token = None
        try:
            token = lex.next()
        except StopIteration:
            pass
        return token

    def _atom(self, lex, token):
        out = []

        while True:
            try:
                if token == '\\':
                    # Function
                    name = lex.next()
                    func = {'type': 'function', 'name': name,
                            'lineno' : lex.lineNo()}
                    args = []
                    optargs = []
                    token = self._guardedNext(lex)
                    while token in ['{', '[']:
                        # Arguments
                        arg = self._atom(lex, lex.next())

                        if token == '{':
                            args.append(arg)
                        elif token == '[':
                            optargs.append(arg)
                        token = self._guardedNext(lex)
                    if args:
                        func['args'] = args
                    if optargs:
                        func['optargs'] = optargs
                    out.append(func)
                    if token is None:
                        raise StopIteration
                elif token in ['}',']']:
                    # End scope
                    break
                else:
                    # String literal
                    out.append({ 'type': 'literal', 'value': token,
                                'lineno' : lex.lineNo()})
                    token = lex.next()
            except StopIteration:
                break
        return out

    def parse(self, instream):
        lex = lexer.Lexer(instream)
        return self._atom(lex, lex.next())
