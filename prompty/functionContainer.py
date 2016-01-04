#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:

# Import external modules
#import inspect    # Removed for being slow to import
#import types      # Not used
import imp
import glob
import os

# Import prompty modules
import functionBase

import status as statusmod




class FunctionContainer(object):

    def _call(self, *args, **kwargs):
        if len(args) < 1:
            raise TypeError("call requires a name")
        name = args[0]
        return self.functions[name](*args[1:], **kwargs)

    def addFunction(self, name, func):
        self.functions[name] = func

    def addFunctionsFromModule(self, module):
        for _, cls in functionBase.getmembers(
                module,
                functionBase.PromptyFunctions._isPromptyFunctionsSubClass
            ):
            # Instantiate class
            obj = cls(self)
            # Store object so that it is not garbage collected
            self.instances.append(obj)
            # Register prompty functions
            obj.register()


    def addFunctionsFromDir(self, directory):
        for filename in glob.glob(os.path.join(directory,"*.py")):
            module = imp.load_source('user', filename)
            self.addFunctionsFromModule(module)

    def __init__(self, status=None):
        if status is None:
            status = statusmod.Status()
        self.status = status
        self.functions = {}
        self.instances = []



