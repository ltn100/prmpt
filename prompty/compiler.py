#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:

import parser
import functionContainer
import colours
import status



class Output(object):
    def __init__(self):
        self.output = ""
        self.pos = status.Coords()

    def add(self, unicodeString):
        self.output += unicode(unicodeString)
        self._updatePos(unicodeString)

    def _updatePos(self, unicodeString):
        non_print = False
        for char in unicodeString:
            if char == colours.Colours.NOCOUNT_START:
                non_print = True
                continue
            if char == colours.Colours.NOCOUNT_END:
                non_print = False
                continue
            if not non_print:
                if char == "\n":
                    self.pos.incRow()
                    self.pos.column = 0
                elif char == "\r":
                    self.pos.column = 0
                else:
                    self.pos.incColumn()

class Compiler(object):
    def __init__(self, funcs=None):
        if funcs is None:
            funcs = functionContainer.FunctionContainer()
        self.funcs = funcs
        self.parser = parser.Parser()
        self.parsedStruct = []

    def compile(self, promptString):
        self.parsedStruct.extend(self.parser.parse(promptString))

    def execute(self):
        return self._execute(self.parsedStruct)

    def _execute(self, parsedStruct, pos=None):
        out = Output()
        if pos is None:
            pos = status.Coords()
        for element in parsedStruct:
            if element['type'] == 'literal':
                # Literals go to the output verbatim
                out.add(element['value'])
                self.funcs.status.pos.set(out.pos)
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
                    out.add(unicode(self.funcs._call(*args)))
                    self.funcs.status.pos.set(out.pos)
                except ValueError, e:
                    return "Prompty error on line %d: %s\n$ " % (element['lineno'], str(e))
                except KeyError, e:
                    return "Prompty error on line %d: No such function %s\n$ " % (element['lineno'], str(e))

        return out.output
