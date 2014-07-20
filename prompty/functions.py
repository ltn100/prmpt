#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:

# Import external modules
import sys
import os
import re
import getpass
import socket
import inspect

import colours
import prompty


#               \a     an ASCII bell character (07)
#               \d     the date in "Weekday Month Date" format (e.g., "Tue May 26")
#               \D{format}
#                      the format is passed to strftime(3) and the result is inserted into
#                      the  prompt  string;  an  empty format results in a locale-specific
#                      time representation.  The braces are required
#               \e     an ASCII escape character (033)
#              x\h     the hostname up to the first `.'
#              x\H     the hostname
#               \j     the number of jobs currently managed by the shell
#               \l     the basename of the shell's terminal device name
#              x\n     newline
#              x\r     carriage return
#               \s     the name of the shell, the basename of $0  (the  portion  following
#                      the final slash)
#               \t     the current time in 24-hour HH:MM:SS format
#               \T     the current time in 12-hour HH:MM:SS format
#               \@     the current time in 12-hour am/pm format
#               \A     the current time in 24-hour HH:MM format
#              x\u     the username of the current user
#               \v     the version of bash (e.g., 2.00)
#               \V     the release of bash, version + patch level (e.g., 2.00.0)
#              x\w     the  current working directory, with $HOME abbreviated with a tilde
#                      (uses the value of the PROMPT_DIRTRIM variable)
#              x\W     the basename of the current working directory, with $HOME  abbreviated with a tilde
#               \!     the history number of this command
#               \#     the command number of this command
#              x\$     if the effective UID is 0, a #, otherwise a $
#               \nnn   the character corresponding to the octal number nnn
#               \\     a backslash
#              x\[     begin a sequence of non-printing characters, which could be used to
#                      embed a terminal control sequence into the prompt
#              x\]     end a sequence of non-printing characters

colours._populateFunctions(sys.modules[__name__])

def unichar(status, code):
    return unichr(int(code))

def space(status):
    return u" "

def newline(status):
    return u"\n"

def carriagereturn(status):
    return u"\r"

def user(status):
    return getpass.getuser()

def hostname(status):
    return socket.gethostname().split(".")[0]

def hostnamefull(status):
    return socket.gethostname()

def workingdir(status):
    home = os.path.expanduser(r"~")
    cwd = os.getcwd()
    return re.sub(r'^%s' % home, r"~", cwd)

def workingdirbase(status):
    return os.path.basename(os.getcwd())

def dollar(status, euid=None):
    if euid is None:
        euid = status.euid
    if int(euid) == 0:
        return ur"#"
    else:
        return ur"$"


def _tobool(expr):
    if str(expr).lower() in ['true', '1', 't', 'y', 'yes']:
        return True
    else:
        return False

def equals(status, a,b):
    return a == b

def ifexpr(status, cond,thenval,elseval=None):
    if _tobool(cond):
        return thenval
    else:
        if elseval:
            return elseval
        else:
            return u""

def exitsuccess(status):
    if status.exitCode == 0:
        return True
    else:
        return False


def lower(status, literal):
    return unicode(literal).lower()

def greater(status, a,b):
    if a > b:
        return a
    else:
        return b

def join(status, *args):
    if len(args) < 1:
        raise TypeError("join needs at least one argument")
    delim = args[0]
    args = args[1:]
    return unicode(delim).join(args)

def smiley(status):
    if status.exitCode == 0:
        out = colours.startColour(status, "green", "bold")
        out += dollar(status)
        out += u":)"
    else:
        out = colours.startColour(status, "red", "bold")
        out += dollar(status)
        out += u":("
    out += colours.stopColour(status)
    return out


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
            status = prompty.Status()
        self.status = status
        self.functions = {}
        self._addFunctions(sys.modules[__name__])

