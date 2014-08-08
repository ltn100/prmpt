#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:

# Import external modules
import os
import re
import getpass
import socket
import datetime

import colours


#            TODO:
#               \a     an ASCII bell character (07)
#               \j     the number of jobs currently managed by the shell
#               \l     the basename of the shell's terminal device name
#               \s     the name of the shell, the basename of $0  (the  portion  following
#                      the final slash)
#               \t     the current time in 24-hour HH:MM:SS format
#               \T     the current time in 12-hour HH:MM:SS format
#               \@     the current time in 12-hour am/pm format
#               \A     the current time in 24-hour HH:MM format
#               \v     the version of bash (e.g., 2.00)
#               \V     the release of bash, version + patch level (e.g., 2.00.0)
#               \!     the history number of this command
#               \#     the command number of this command



# ----- Special Characters --------
# \e
def unichar(status, code):
    return unichr(int(code,0))

# \\
def backslash(status):
    return u"\\"

def percent(status):
    return u"%"

def opencurly(status):
    return u"{"

def closecurly(status):
    return u"}"

def opensquare(status):
    return u"["

def closesquare(status):
    return u"]"

def space(status):
    return u" "

# \n
def newline(status):
    return u"\n"

# \r
def carriagereturn(status):
    return u"\r"

# \e
def escape(status):
    return u"\033"


# ----- Bash Prompt Functions --------
# \D
def datefmt(status,format=None):
    now = datetime.datetime.now()
    if format:
        format = format.replace('#', '%')
        return now.strftime(format)
    else:
        return now.strftime("%X")

# \d
def date(status):
    return datefmt(status, "%a %b %d")

# \u
def user(status):
    return getpass.getuser()

# \h
def hostname(status):
    return socket.gethostname().split(".")[0]

# \H
def hostnamefull(status):
    return socket.gethostname()

# \w
def workingdir(status):
    cwd = os.getenv('PWD')
    home = os.path.expanduser(r"~")
    return re.sub(r'^%s' % home, r"~", cwd)

# \W
def workingdirbase(status):
    return os.path.basename(os.getenv('PWD'))

# \$
def dollar(status, euid=None):
    if euid is None:
        euid = status.euid
    if int(euid) == 0:
        return ur"#"
    else:
        return ur"$"

def isrealpath(status, path=None):
    if path is None:
        path = os.getenv('PWD')
    if path == os.path.realpath(path):
        return True
    else:
        return False


# ----- Expression Functions --------

def exitsuccess(status):
    if status.exitCode == 0:
        return True
    else:
        return False

def equals(status, a,b):
    return a == b

def greater(status, a,b):
    if a > b:
        return a
    else:
        return b


# ----- Control Functions --------

def ifexpr(status, cond,thenval,elseval=None):
    if _tobool(cond):
        return thenval
    else:
        if elseval:
            return elseval
        else:
            return u""


# ----- String Functions --------

def lower(status, literal):
    return unicode(literal).lower()

def join(status, *args):
    if len(args) < 1:
        raise TypeError("join needs at least one argument")
    delim = args[0]
    args = args[1:]
    return unicode(delim).join(args)

def justify(status, left, centre, right, lpad=" ", rpad=" "):
    sleft = len(left)
    scentre = len(centre)
    sright = len(right)
    padsize = status.window.column - (sleft+scentre+sright)
    if padsize <= 1:
        # No more space!
        return left + centre + right

    # Aim to get the centre in the centre
    lpadsize = (status.window.column/2)-(sleft+(scentre/2))
    if lpadsize <= 0:
        lpadsize = 1
    rpadsize = padsize - lpadsize

    return left + lpad*lpadsize + centre + rpad*rpadsize + right

def right(status, literal):
    return justify(status, "", "", literal)



# ----- Misc Functions --------

def tick(status):
    return unichr(0x2714)

def cross(status):
    return unichr(0x2718)

def highvoltage(status):
    return unichr(0x26A1)

def plbranch(status):
    return unichr(0xe0a0)

def plline(status):
    return unichr(0xe0a1)

def pllock(status):
    return unichr(0xe0a2)

def plrightarrowfill(status):
    return unichr(0xe0b0)

def plrightarrow(status):
    return unichr(0xe0b1)

def plleftarrowfill(status):
    return unichr(0xe0b2)

def plleftarrow(status):
    return unichr(0xe0b3)

def powerline(status,content,background="blue",foreground="white"):
    out =  colours.startColour(status, fgcolour=foreground)
    out += colours.startColour(status, bgcolour=background)
    out += " "
    out += content
    out += " "
    out += colours.startColour(status, bgcolour=foreground)
    out += colours.startColour(status, fgcolour=background)
    out += plrightarrowfill(status)
    out += colours.stopColour(status)
    return out

def smiley(status):
    if status.exitCode == 0:
        out = colours.startColour(status, "green", prefix="bold")
        out += dollar(status)
        out += u":)"
    else:
        out = colours.startColour(status, "red", prefix="bold")
        out += dollar(status)
        out += u":("
    out += colours.stopColour(status)
    return out



#============================================
# Internal Functions
#============================================

def _tobool(expr):
    if str(expr).lower() in ['true', '1', 't', 'y', 'yes']:
        return True
    else:
        return False
