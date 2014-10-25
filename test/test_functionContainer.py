#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:

import sys
import os

from test_prompty import UnitTestWrapper
from test_prompty import prompty


class TestFunctions(prompty.functionBase.PromptyFunctions):
    def testFunc(self):
        return "This Is A Test"
    
    def _hiddenFunc(self):
        return "This is secret"

class FunctionContainerTests(UnitTestWrapper):
    def test_noname(self):
        c = prompty.functionContainer.FunctionContainer()
        self.assertRaises(TypeError, c._call)
        
    def test_extendFunctionContainer(self):
        c = prompty.functionContainer.FunctionContainer()
        # Import this module
        c.addFunctionsFromModule(sys.modules[__name__])
        self.assertEqual(r"This Is A Test", c._call(["testFunc"]))
        self.assertRaises(KeyError, c._call, ["_hiddenFunc"])
        
    def test_extendFunctionContainerFromDir(self):
        c = prompty.functionContainer.FunctionContainer()
        # Import this directory
        c.addFunctionsFromDir(os.path.dirname(sys.modules[__name__].__file__))
        self.assertEqual(r"This Is A Test", c._call(["testFunc"]))