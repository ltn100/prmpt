#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:

# Import external modules
import inspect
import imp
import glob
import os

# Import prompty modules
import functions
import colours
import prompty
import git

class FunctionContainer(object):

    def _call(self, *args):
        if len(args) < 1:
            raise TypeError("call requires a name")
        name = args[0]
        args = [self.status] + list(args[1:])
        return self.functions[name](*args)


    def addFunctions(self, module):
        for name, func in inspect.getmembers(module, inspect.isfunction):
            if name[0] != "_":
                self.functions[name] = func

    def addFunctionsFromDir(self, directory):
        for filename in glob.glob(os.path.join(directory,"*.py")):
            module = imp.load_source('user', filename)
            for name, func in inspect.getmembers(module, inspect.isfunction):
                if name[0] != "_":
                    self.functions[name] = func

    def __init__(self, status=None, userDirs=None):
        if status is None:
            status = prompty.Status()
        self.status = status
        self.functions = {}
        self.addFunctions(functions)
        self.addFunctions(colours)
        self.addFunctions(git)
        if userDirs:
            for directory in userDirs:
                self.addFunctionsFromDir(directory)
        