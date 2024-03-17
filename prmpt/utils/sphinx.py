#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from builtins import str

import sphinx.util.inspect
from sphinx.ext.autodoc import MethodDocumenter, ModuleDocumenter, ClassDocumenter, Signature
from six import StringIO, itervalues

from .. import functionBase


class PrmptSignature(sphinx.util.inspect.Signature):
    def format_args(self):
        """
        Format the arguments like ``[oparg][optarg=default]{reqarg}``.
        """
        required_args = []
        optional_args = []
        for i, param in enumerate(itervalues(self.parameters)):
            # skip first argument if subject is bound method
            if self.skip_first_argument and i == 0:
                continue

            arg = StringIO()

            if param.default is not param.empty:
                # Optional arg []
                if param.name.startswith("_"):
                    # Skip documenting optional parameters that start with _
                    continue

                arg.write("[")
                arg.write(param.name)
                if param.default is not None:
                    arg.write("='")
                    arg.write(str(param.default))
                    arg.write("'")
                arg.write("]")
                optional_args.append(arg.getvalue())
            else:
                # Required arg {}
                arg.write("{")
                arg.write(param.name)
                arg.write("}")
                required_args.append(arg.getvalue())

        return ''.join(optional_args) + ''.join(required_args)


class PrmptMethodDocumenter(MethodDocumenter):
    objtype = 'prmptmethod'
    priority = 20  # higher priority than MethodDocumenter

    def format_args(self, **kwargs):
        """
        Format the arguments like ``[oparg][optarg=default]{reqarg}``.
        """
        # Monkey patch the Signature class
        OldSignature = sphinx.ext.autodoc.Signature
        sphinx.ext.autodoc.Signature = PrmptSignature

        # Call base class member
        args = super(PrmptMethodDocumenter, self).format_args(**kwargs)

        # Revert patch
        sphinx.ext.autodoc.Signature = OldSignature
        return args

    def format_name(self, **kwargs):
        """
        Format the function name like ``\\function``.
        """
        name = super(PrmptMethodDocumenter, self).format_name(**kwargs)
        # Remove class name
        name = name.split('.')[-1]
        return "\\\\" + name


def setup(app):
    app.add_autodocumenter(PrmptMethodDocumenter)
