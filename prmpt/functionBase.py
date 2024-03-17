#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import types


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


def ismethod(obj):
    """ ** Extracted from inspect module for optimisation purposes **

    Return true if the object is an instance method.

    Instance method objects provide these attributes:
        __doc__         documentation string
        __name__        name with which this method was defined
        im_class        class object in which this method belongs
        im_func         function object containing implementation of method
        im_self         instance to which this method is bound, or None"""
    return isinstance(obj, types.MethodType)


def isclass(obj):
    """ ** Extracted from inspect module for optimisation purposes **

    Return true if the object is a class.

    Class objects provide these attributes:
        __doc__         documentation string
        __module__      name of module in which this class was defined"""
    return isinstance(obj, type)


class PrmptFunctions(object):
    def __init__(self, container=None):
        self.functions = container
        if self.functions:
            self.status = self.functions.status
        else:
            self.status = None

    @staticmethod
    def _isPrmptFunctionsSubClass(obj):
        return isclass(obj) and issubclass(obj, PrmptFunctions)

    def register(self):
        for name, func in getmembers(self, ismethod):
            if name[0] != "_":
                self.functions.addFunction(name, func)

    def call(self, func, *args, **kwargs):
        return self.functions._call(func, *args, **kwargs)
