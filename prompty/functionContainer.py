#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:

# Import external modules
#import inspect    # Removed for being slow to import
import types
import imp
import glob
import os

# Import prompty modules
import functions
import colours
import status as statusmod
import vcs


def getmembers(obj, predicate=None):
    """ ** Extracted from inspect module for optimisation purposes **
    Return all members of an object as (name, value) pairs sorted by name.
    Optionally, only return members that satisfy a given predicate."""
    results = []
    for key in dir(obj):
        try:
            value = getattr(obj, key)
        except AttributeError:
            continue
        if not predicate or predicate(value):
            results.append((key, value))
    
    results.sort()
    return results

def isfunction(obj):
    """ ** Extracted from inspect module for optimisation purposes **
    
    Return true if the object is a user-defined function.
    
    Function objects provide these attributes:
    __doc__         documentation string
    __name__        name with which this function was defined
    func_code       code object containing compiled function bytecode
    func_defaults   tuple of any default values for arguments
    func_doc        (same as __doc__)
    func_globals    global namespace in which this function was defined
    func_name       (same as __name__)"""
    return isinstance(obj, types.FunctionType)


class FunctionContainer(object):

    def _call(self, *args):
        if len(args) < 1:
            raise TypeError("call requires a name")
        name = args[0][0]
        if len(args[0]) > 1:
            pos = args[0][1]
        else:
            pos = 0
        self.status.pos = pos
        args = [self.status] + list(args[1:])
        return self.functions[name](*args)


    def addFunctions(self, module):
        for name, func in getmembers(module, isfunction):
            if name[0] != "_":
                self.functions[name] = func

    def addFunctionsFromDir(self, directory):
        for filename in glob.glob(os.path.join(directory,"*.py")):
            module = imp.load_source('user', filename)
            for name, func in getmembers(module, isfunction):
                if name[0] != "_":
                    self.functions[name] = func

    def __init__(self, status=None, userDirs=None):
        if status is None:
            status = statusmod.Status()
        self.status = status
        self.functions = {}
        self.addFunctions(functions)
        self.addFunctions(colours)
        self.addFunctions(vcs)
        if userDirs:
            for directory in userDirs:
                self.addFunctionsFromDir(directory)
