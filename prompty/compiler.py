#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:

import parser
import colours
import status


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
                args = [(element['name'], pos+out.pos)]
                # Then the required arguments
                if 'args' in element:
                    for arg in element['args']:
                        args.append(self._execute(arg,pos+out.pos))
                # Finally any optional arguments
                if 'optargs' in element:
                    for optarg in element['optargs']:
                        args.append(self._execute(optarg,pos+out.pos))
                # Call the function!
                try:
                    out += self._move(unicode(self.funcs._call(*args)))
                except ValueError, e:
                    return "Prompty error on line %d: %s\n$ " % (element['lineno'], str(e))
                except KeyError, e:
                    return "Prompty error on line %d: No such function %s\n$ " % (element['lineno'], str(e))

        return out
