#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:

# Import external modules
import os
import re
import getpass
import socket
import datetime
import random
import types

import functionBase


#            TO DO:
#               \a     an ASCII bell character (07)
#               \j     the number of jobs currently managed by the shell
#               \l     the basename of the shell's terminal device name
#               \s     the name of the shell, the basename of $0  (the  portion
#                        following the final slash)
#               \t     the current time in 24-hour HH:MM:SS format
#               \T     the current time in 12-hour HH:MM:SS format
#               \@     the current time in 12-hour am/pm format
#               \A     the current time in 24-hour HH:MM format
#               \v     the version of bash (e.g., 2.00)
#               \V     the release of bash, version + patch level (e.g., 2.00.0)
#               \!     the history number of this command
#               \#     the command number of this command



import colours


class BaseFunctions(functionBase.PromptyFunctions):
    # ----- Special Characters --------
    # \e
    def unichar(self, code):
        return unichr(int(code,0))

    # \\
    def backslash(self):
        return "\\"

    def percent(self):
        return "%"

    def opencurly(self):
        return "{"

    def closecurly(self):
        return "}"

    def opensquare(self):
        return "["

    def closesquare(self):
        return "]"

    def space(self):
        return " "

    # \n
    def newline(self):
        return "\n"

    # \r
    def carriagereturn(self):
        return "\r"

    # \e
    def escape(self):
        return unicode("\033")


    # ----- Bash Prompt Functions --------
    # \D
    def datefmt(self,fmt=None):
        now = datetime.datetime.now()
        if fmt:
            fmt = fmt.replace('#', '%')
            return now.strftime(fmt)
        else:
            return now.strftime("%X")

    # \d
    def date(self):
        return self.datefmt("%a %b %d")

    # \u
    def user(self):
        return getpass.getuser()

    # \h
    def hostname(self):
        return socket.gethostname().split(".")[0]

    # \H
    def hostnamefull(self):
        return socket.gethostname()

    # \w
    def workingdir(self):
        cwd = self.status.getWorkingDir()
        home = os.path.expanduser(r"~")
        return re.sub(r'^%s' % home, r"~", cwd)

    # \W
    def workingdirbase(self):
        return os.path.basename(self.status.getWorkingDir())

    # \$
    def dollar(self, euid=None):
        if euid is None:
            euid = self.status.euid
        if int(euid) == 0:
            return unicode(r"#")
        else:
            return unicode(r"$")

    def isrealpath(self, path=None):
        if path is None:
            path = self.status.getWorkingDir()
        if path == os.path.realpath(path):
            return True
        else:
            return False


    # ----- Expression Functions --------

    def exitsuccess(self):
        if self.status.exitCode == 0:
            return True
        else:
            return False

    def equals(self, a,b):
        return a == b

    def greater(self, a,b):
        if a > b:
            return a
        else:
            return b


    # ----- Control Functions --------

    def ifexpr(self, cond,thenval,elseval=None):
        if _tobool(cond):
            return thenval
        else:
            if elseval:
                return elseval
            else:
                return unicode("")


    # ----- String Functions --------

    def lower(self, literal):
        return unicode(literal).lower()

    def join(self, *args):
        if len(args) < 1:
            raise TypeError("join needs at least one argument")
        delim = args[0]
        args = args[1:]
        return unicode(delim).join(args)

    def justify(self, left, centre, right, lpad=" ", rpad=" "):
        sleft = len(left)
        scentre = len(centre)
        sright = len(right)
        padsize = self.status.window.column - (sleft+scentre+sright)
        if padsize <= 1:
            # No more space!
            return left + centre + right

        # Aim to get the centre in the centre
        lpadsize = (self.status.window.column/2)-(sleft+(scentre/2))
        if lpadsize <= 0:
            lpadsize = 1
        rpadsize = padsize - lpadsize

        return left + lpad*lpadsize + centre + rpad*rpadsize + right

    def right(self, literal):
        return self.justify("", "", literal)



    # ----- Misc Functions --------

    def tick(self):
        return unichr(0x2714)

    def cross(self):
        return unichr(0x2718)

    def highvoltage(self):
        return unichr(0x26A1)

    def plbranch(self):
        return unichr(0xe0a0)

    def plline(self):
        return unichr(0xe0a1)

    def pllock(self):
        return unichr(0xe0a2)

    def plrightarrowfill(self):
        return unichr(0xe0b0)

    def plrightarrow(self):
        return unichr(0xe0b1)

    def plleftarrowfill(self):
        return unichr(0xe0b2)

    def plleftarrow(self):
        return unichr(0xe0b3)

    def powerline(self,content,background="blue",foreground="white"):
        c = colours.Colours(self.functions)
        out =  c.startColour(fgcolour=foreground)
        out += c.startColour(bgcolour=background)
        out += " "
        out += content
        out += " "
        out += c.startColour(bgcolour=foreground)
        out += c.startColour(fgcolour=background)
        out += self.plrightarrowfill()
        out += c.stopColour()
        return out

    def smiley(self):
        c = colours.Colours(self.functions)
        if self.status.exitCode == 0:
            out = c.startColour("green", style="bold")
            out += self.dollar()
            out += unicode(":)")
        else:
            out = c.startColour("red", style="bold")
            out += self.dollar()
            out += unicode(":(")
        out += c.stopColour()
        return out

    def randomcolour(self, literal, seed=None):
        if seed:
            random.seed(seed)
        c = colours.Colours(self.functions)
        colour = str(random.randrange(1,255))
        out = c.startColour(colour)
        out += literal
        out += c.stopColour()
        return out


    def hashedcolour(self, literal):
        return self.randomcolour(literal, seed=literal)

# ============================================
# Internal Functions
# ============================================

def _tobool(expr):
    if str(expr).lower() in ['true', '1', 't', 'y', 'yes']:
        return True
    else:
        return False
