#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:

import prompty
import functions

class Compiler(object):
    def __init__(self, status=None):
        if status is None:
            status = prompty.Status()
            
        self.status = status
        self.funcs = functions.FunctionContainer(status)

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