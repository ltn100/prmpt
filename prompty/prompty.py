#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:

# Import external modules
import os
import inspect

import parser
import compiler
import functions



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
        self.parser = parser.Parser()
        self.compiler = compiler.Compiler(status)


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


