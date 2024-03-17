#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:

import setuptools
from setuptools.command.build_py import build_py
from sphinx.setup_command import BuildDoc
import py_compile
import glob
import os
import codecs
import re

here = os.path.abspath(os.path.dirname(__file__))


def read(*parts):
    with codecs.open(os.path.join(here, *parts), 'r') as fp:
        return fp.read()


def find_version(*file_paths):
    version_file = read(*file_paths)
    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")


class PostBuild(build_py):
    def run(self):
        build_py.run(self)
        print("compiling prmptc")
        py_compile.compile('bin/prmpt')


cmdclass = {
    # Post build step
    "build_py": PostBuild,

    # Build docs
    'build_sphinx': BuildDoc,
}

name = "prmpt"
version = find_version("prmpt", "__init__.py")

setuptools.setup(
    name=name,
    version=version,
    description="A command line prompt markup language",
    author="Lee Netherton",
    author_email="lee.netherton@gmail.com",
    url="https://github.com/ltn100/prmpt",
    license="MIT licence, see LICENCE",

    packages=["prmpt"],

    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development",
        "Topic :: Software Development :: User Interfaces",
        "Topic :: System :: Shells",
        "Topic :: System :: System Shells",
        "Topic :: Terminals",
        "Topic :: Terminals :: Terminal Emulators/X Terminals",
        "Topic :: Utilities",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: Linux",
        "Operating System :: Unix",
        "Operating System :: MacOS"
    ],

    scripts=["bin/prmpt"],

    data_files=[
        (
            "share/prmpt/skel",
            [f for f in glob.glob("skel/*") if os.path.isfile(f)]
        ),
        (
            "share/prmpt/skel/functions",
            [f for f in glob.glob("skel/functions/*") if os.path.isfile(f)]
        ),
    ],

    cmdclass=cmdclass,

    command_options={
        'build_sphinx': {
            'project': ('setup.py', name),
            'version': ('setup.py', version),
            'source_dir': ('setup.py', 'docs')
        }
    },

    setup_requires=[
        "wheel",
        "sphinx",
        "sphinx_rtd_theme"
    ],

    install_requires=[
        "future",
        "configparser"
    ],
)
