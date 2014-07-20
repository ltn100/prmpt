#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:

# Import external modules
import os
import sys
import shlex
import inspect

import functions



class Lexer(shlex.shlex):
    def __init__(self, instream):
        shlex.shlex.__init__(self, instream=instream.replace('\n','\n\n'))
        self.wordchars = self.wordchars + r":;#~@-_=+*/?'!$^&()|<>.," + '"'
        self.commenters = '%'

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
                    func = {'type': 'function', 'name': name}
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
                    out.append({ 'type': 'literal', 'value': token})
                    token = lex.next()
            except StopIteration:
                break
        return out
    
    def parse(self, instream):
        self.lex = Lexer(instream)
        return self._atom(self.lex, self.lex.next())


class Compiler(object):
    def __init__(self, status=None):
        if status is None:
            status = Status()
            
        self.status = status
        self.funcs = FunctionContainer(status)

    def compile(self, parsedStruct):
        out = ""
        for element in parsedStruct:
            if element['type'] == 'literal':
                # Literals go to the output verbatim
                out += element['value']
            elif element['type'] == 'function':
                # First arg is the function name
                args = [element['name']]
                # Then the required arguments
                if 'args' in element:
                    for arg in element['args']:
                        args.append(self.compile(arg))
                # Finally any optional arguments
                if 'optargs' in element:
                    for optarg in element['optargs']:
                        args.append(self.compile(optarg))
                # Call the function!
                out += unicode(self.funcs._call(*args))
                
        return out


class FunctionContainer(object):

    def _call(self, *args):
        if len(args) < 1:
            raise TypeError("call requires a name")
        name = args[0]
        args = [self.status] + list(args[1:])
        return self.functions[name](*args)


    def _addFunctions(self, module):
        for name, func in inspect.getmembers(module, inspect.isfunction):
            if name[0] != "_":
                self.functions[name] = func

    def __init__(self, status=None):
        if status is None:
            status = Status()
        self.status = status
        self.functions = {}
        self._addFunctions(functions)



class Prompt(object):

    def __init__(self, status):
        self.status = status
        self.parser = Parser()
        self.compiler = Compiler(status)


    def getPrompt(self):
        return self.compiler.compile(self.parser.parse(
            r"""
            \green{
                \user
            }
            @
            \white{
                \hostname
            }
            \space
            \blue[bold]{
                \workingdir
            }
            \newline
            \smiley
            \space
            """
        ))


class Status(object):
    def __init__(self, exitCode=0):
        self.exitCode = int(exitCode)
        self.euid = os.geteuid()


