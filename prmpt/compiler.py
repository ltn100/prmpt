#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from builtins import str

from prmpt import parser
from prmpt import colours
from prmpt import status


class Compiler(object):
    """ Compiles and executes the parsed dictionary list output
    from the Parser.

    Literals are output verbatim, or passed into functions for
    processing.
    """
    def __init__(self, functionContainer):
        # Compiler requires a valid FunctionContainer in order
        # to execute functions
        self.funcs = functionContainer

        self.parser = parser.Parser()
        self.parsedStruct = []

    def compile(self, promptString):
        """ Parse a given promptString. Add the resulting
        list of dictionary items to the internal buffer
        ready for executing.
        """
        self.parsedStruct.extend(self.parser.parse(promptString))

    def execute(self):
        """ Execute the internal buffer and return the output
        string.
        """
        return self._execute(self.parsedStruct)

    def _move(self, string):
        self.funcs.status.pos.incFromString(string)
        return string

    def _execute(self, parsedStruct):
        out = ""
        for element in parsedStruct:
            if element['type'] == 'literal':
                # Literals go to the output verbatim
                out += self._move(element['value'])
            elif element['type'] == 'function':
                # First arg is the function name and current char position
                args = [element['name']]
                # Then the required arguments
                if 'args' in element:
                    for arg in element['args']:
                        args.append(self._execute(arg))
                # Finally any optional arguments
                if 'optargs' in element:
                    for optarg in element['optargs']:
                        args.append(self._execute(optarg))
                # Call the function!
                try:
                    out += self._move(str(self.funcs._call(*args)))
                except ValueError as e:
                    return "Prmpt error on line %d: %s\n$ " % (element['lineno'], str(e))
                except KeyError as e:
                    return "Prmpt error on line %d: No such function %s\n$ " % (element['lineno'], str(e))

        return out
