#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from builtins import str
from builtins import chr

# Import external modules
import os
import re
import getpass
import socket
import datetime
import random

from . import functionBase


class SpecialCharacters(functionBase.PrmptFunctions):
    """
    Functions to print special characters.
    """
    def unichar(self, code):
        """
        Generate a unicode character.

        :param code: A unicode integer value. Can be prepended with ``0x`` or
                        ``0o`` for hexadecimal or octal values.
        """
        return chr(int(code, 0))

    def backslash(self):
        """
        A backslash character (``\\``).
        """
        return "\\"

    def percent(self):
        """
        A percent character (``%``).
        """
        return "%"

    def opencurly(self):
        """
        An open curly brace character (``{``).
        """
        return "{"

    def closecurly(self):
        """
        An close curly brace character (``}``).
        """
        return "}"

    def opensquare(self):
        """
        An open square bracket character (``[``).
        """
        return "["

    def closesquare(self):
        """
        A close square bracket character (``]``).
        """
        return "]"

    def space(self):
        """
        A single "space" character.
        """
        return " "

    def newline(self):
        """
        A new line character (``\\n``).
        """
        return "\n"

    def carriagereturn(self):
        """
        A carriage return character (``\\r``).
        """
        return "\r"

    def escape(self):
        """
        A bash escape code character (``\\033``).
        """
        return str("\033")

    def tick(self):
        """
        A tick symbol (\u2714).
        """
        return chr(0x2714)

    def cross(self):
        """
        A cross symbol (\u2718).
        """
        return chr(0x2718)

    def highvoltage(self):
        """
        A high voltage symbol (\u26A1).
        """
        return chr(0x26A1)


class PowerlineFunctions(functionBase.PrmptFunctions):
    """
    Functions for use with
    `Powerline <https://github.com/powerline/powerline>`_ fonts.

    You must have the `powerline fonts <https://github.com/powerline/fonts>`_
    package installed in order for these to render properly.
    """
    def powerline(self, content, bg="blue", bg_next="default", fg="white", dir="right"):
        """
        Render ``content`` inside powerline arrows. It is possible to string
        together multiple powerlines together by ensuring that the next
        background colour is set match the next block's background. For
        example:

        .. highlight:: python
        .. code-block:: latex

            \\powerline[27][33]{this}  % colour 33 is carried over
            \\powerline[33][75]{is}    % colour 75 is carried over
            \\powerline[75]{cool}      % next colour is default bg colour

        :param content: The contents of the powerline
        :param bg: Background colour, defaults to "blue"
        :param bg_next: Background colour of next block, defaults to "default"
        :param fg: Foreground colour, defaults to "white"
        :param dir: The arrow direction, defaults to "right"
        """
        out = ""
        if dir == "left":
            out += self.call("startColour", bgcolour=bg_next)
            out += self.call("startColour", fgcolour=bg)
            out += self.plleftarrowfill()
        out += self.call("startColour", fgcolour=fg)
        out += self.call("startColour", bgcolour=bg)
        out += " "
        out += content
        out += " "
        if dir == "right":
            out += self.call("startColour", bgcolour=bg_next)
            out += self.call("startColour", fgcolour=bg)
            out += self.plrightarrowfill()
        out += self.call("stopColour")
        return out

    def plbranch(self):
        """
        A powerline branch symbol.
        """
        return chr(0xe0a0)

    def plline(self):
        """
        A powerline "line number" symbol.
        """
        return chr(0xe0a1)

    def pllock(self):
        """
        A powerline padlock symbol.
        """
        return chr(0xe0a2)

    def plrightarrowfill(self):
        """
        A powerline filled right arrow.
        """
        return chr(0xe0b0)

    def plrightarrow(self):
        """
        A powerline unfilled right arrow.
        """
        return chr(0xe0b1)

    def plleftarrowfill(self):
        """
        A powerline filled left arrow.
        """
        return chr(0xe0b2)

    def plleftarrow(self):
        """
        A powerline unfilled left arrow.
        """
        return chr(0xe0b3)


class BashPromptEscapes(functionBase.PrmptFunctions):
    """
    Functions to mimic bash prompt escape sequences, similar to those defined
    here:
    https://www.tldp.org/HOWTO/Bash-Prompt-HOWTO/bash-prompt-escape-sequences.html
    """
    # TODO:
    # - \a - an ASCII bell character (07)
    # - \j - the number of jobs currently managed by the shell
    # - \l - the basename of the shell's terminal device name
    # - \s - the name of the shell, the basename of $0  (the  portion
    #        following the final slash)
    # - \t - the current time in 24-hour HH:MM:SS format
    # - \T - the current time in 12-hour HH:MM:SS format
    # - \@ - the current time in 12-hour am/pm format
    # - \A - the current time in 24-hour HH:MM format
    # - \v - the version of bash (e.g., 2.00)
    # - \V - the release of bash, version + patch level (e.g., 2.00.0)
    # - \! - the history number of this command
    # - \# - the command number of this command

    def date(self):
        """
        The date  in  "Weekday Month Date"  format (e.g., ``Tue May 26``).

        Equivalent to the bash prompt escape sequence ``\\d``
        """
        return self.datefmt("%a %b %d")

    def datefmt(self, fmt='#X'):
        """
        Generate the current date and time, and format it according to the
        given ``fmt`` string. Formats are given in the `strptime()
        <https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior>`_
        function documentation. However, because ``%`` is a special character
        in prmpt, the control character is changed to ``#``. For example:
        ``#a #b #d`` will render to "Weekday Month Date".

        If no ``fmt`` string is given, then the local time in 24hr format is
        returned.

        :param fmt: format string, defaults to ``#X`` - Locale's appropriate time
                    representation, e.g.: ``21:30:00``.
        """
        now = datetime.datetime.now()
        fmt = fmt.replace('#', '%')
        return now.strftime(fmt)

    def user(self):
        """
        The username of the current user.

        Equivalent to the bash prompt escape sequence ``\\u``.
        """
        return getpass.getuser()

    def hostname(self):
        """
        The hostname up to the first ``.``.

        Equivalent to the bash prompt escape sequence ``\\h``.
        """
        return socket.gethostname().split(".")[0]

    def hostnamefull(self):
        """
        The hostname.

        Equivalent to the bash prompt escape sequence ``\\H``.
        """
        return socket.gethostname()

    def workingdir(self):
        """
        The current working directory.

        Equivalent to the bash prompt escape sequence ``\\w``.
        """
        cwd = self.status.getWorkingDir()
        home = os.path.expanduser(r"~")
        return re.sub(r'^%s' % home, r"~", cwd)

    def workingdirbase(self):
        """
        The basename of the current working directory.

        Equivalent to the bash prompt escape sequence ``\\W``.
        """
        return os.path.basename(self.status.getWorkingDir())

    def dollar(self, euid=None):
        """
        If the effective UID is 0, a ``#``, otherwise a ``$``.

        Equivalent to the bash prompt escape sequence ``\\$``.

        :param euid: A user Id, defaults to the current user.
        """
        if euid is None:
            euid = self.status.euid
        if int(euid) == 0:
            return str(r"#")
        else:
            return str(r"$")


class MiscFunctions(functionBase.PrmptFunctions):
    def isrealpath(self, path=None):
        """
        If the current directory is a real path (i.e. not via a symbolic link)
        then return ``True``, else return ``False``.

        :param path: A path, defaults to the current working path.
        :rtype: bool
        """
        if path is None:
            path = self.status.getWorkingDir()
        if path == os.path.realpath(path):
            return True
        else:
            return False

    # ----- Expression Functions --------
    def exitsuccess(self):
        """
        If the last command executed with a 0 status code, return ``True``. Otherwise
        return ``False``.

        :rtype: bool
        """
        if self.status.exitCode == 0:
            return True
        else:
            return False

    def equals(self, a, b):
        """
        Return ``True`` if the two parameters ``a`` and ``b`` are equal (by value).

        :rtype: bool
        """
        return a == b

    def max(self, a, b):
        """
        Return the maximum of ``a`` and ``b``.

        :type a: number
        :type b: number
        :rtype: number
        """
        if float(a) > float(b):
            return a
        else:
            return b

    def min(self, a, b):
        """
        Return the minimum of ``a`` and ``b``.

        :type a: number
        :type b: number
        :rtype: number
        """
        if float(a) < float(b):
            return a
        else:
            return b

    def gt(self, a, b):
        """
        Return ``True`` if ``a`` > ``b``.

        :type a: number
        :type b: number
        :rtype: bool
        """
        return float(a) > float(b)

    def lt(self, a, b):
        """
        Return ``True`` if ``a`` < ``b``.

        :type a: number
        :type b: number
        :rtype: bool
        """
        return float(a) < float(b)

    def gte(self, a, b):
        """
        Return ``True`` if ``a`` >= ``b``.

        :type a: number
        :type b: number
        :rtype: bool
        """
        return float(a) >= float(b)

    def lte(self, a, b):
        """
        Return ``True`` if ``a`` <= ``b``.

        :type a: number
        :type b: number
        :rtype: bool
        """
        return float(a) <= float(b)

    # ----- Control Functions --------

    def ifexpr(self, cond, thenval='', elseval=''):
        """
        If ``cond`` is equivalent to ``True``, then return ``thenval``, else
        return ``elseval``.

        :param cond: Condition
        :type cond: bool
        :param thenval: Value returned if condition is equivalent to ``True``, defaults to an empty string.
        :param elseval: Value returned if condition is equivalent to ``False``, defaults to an empty string.
        """
        if _tobool(cond):
            return thenval
        else:
            if elseval:
                return elseval
            else:
                return str("")

    # ----- String Functions --------
    def lower(self, literal):
        """
        Return a lowercase representation of ``literal``.
        """
        return str(literal).lower()

    def upper(self, literal):
        """
        Return an uppercase representation of ``literal``.
        """
        return str(literal).upper()

    def join(self, *args):
        """
        Join multiple strings together. The first argument is the delimiter, all subsequent
        arguments are strings to join.

        Example:

        .. highlight:: python
        .. code-block:: latex

            \\join{_}{joined}{with}{underscores}

        Output:

        .. highlight:: python
        .. code-block:: none

            joined_with_underscores
        """
        if len(args) < 1:
            raise TypeError("join needs at least one argument")
        delim = args[0]
        args = args[1:]
        return str(delim).join(args)

    def justify(self, left, centre, right, lpad=u" ", rpad=u" "):
        """
        Justify text in 3 columns to fill the terminal. Text in ``left`` will be
        left justified, text in ``centre`` will be centre justified, and text in
        ``right`` will be right justified. The padding characters between ``left``
        and ``centre``, and ``centre`` and ``right`` can be controlled with ``lpad``
        and ``rpad``, respectively.

        Example:

        .. highlight:: python
        .. code-block:: latex

            \\justify[_]{this is left}{in the centre}{on the right}

        Output:

        .. highlight:: python
        .. code-block:: none

            this is left________________________in the centre                        on the right
        """
        sleft = len(left)
        scentre = len(centre)
        sright = len(right)
        padsize = self.status.window.column - (sleft+scentre+sright)
        if padsize <= 1:
            # No more space!
            return left + centre + right

        # Aim to get the centre in the centre
        lpadsize = (self.status.window.column//2)-(sleft+(scentre//2))
        if lpadsize <= 0:
            lpadsize = 1
        rpadsize = padsize - lpadsize

        return left + lpad*lpadsize + centre + rpad*rpadsize + right

    def right(self, literal):
        """
        Justify string ``literal`` right.
        """
        return self.justify("", "", literal)

    def smiley(self):
        """
        Generate a smiley that has the following properties:

        - ``$:)`` - (colour green) Last command succeeded, user is not root
        - ``$:(`` - (colour red) Last command failed, user is not root
        - ``#:)`` - (colour green) Last command succeeded, user is root
        - ``#:(`` - (colour red) Last command failed, user is root
        """
        if self.status.exitCode == 0:
            out = self.call("startColour", "green", style="bold")
            out += self.call("dollar")
            out += str(":)")
        else:
            out = self.call("startColour", "red", style="bold")
            out += self.call("dollar")
            out += str(":(")
        out += self.call("stopColour")
        return out

    def randomcolour(self, literal, seed=None):
        """
        Decorate ``literal`` with a random colour.

        :param seed: The random hash seed, to enable consistency between calls.
        """
        if seed:
            random.seed(seed)
        colour = str(random.randrange(1, 255))
        out = self.call("startColour", colour)
        out += literal
        out += self.call("stopColour")
        return out

    def hashedcolour(self, literal):
        """
        Decorate ``literal`` with a colour based on its hash.
        This can be useful for generating a unique colour for different
        user or host names.
        """
        return self.randomcolour(literal, seed=literal)


# ============================================
# Internal Functions
# ============================================
def _tobool(expr):
    # First try integer cast
    try:
        return bool(int(expr))
    except ValueError:
        pass

    if str(expr).lower() in ['true', 't', 'y', 'yes']:
        return True
    else:
        return False
