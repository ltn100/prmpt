#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import datetime

# Import external modules
import sys
import os
import getopt
import codecs
import click

import prompty

# Should be overridden by bin/prompty
START = 0


class RunConfig(object):
    options = [
        # All options should have default=None
        # Set the real defaults in __init__() below
        click.option("--exit-status", "-e", default=None, type=int, help="The exit status of the last command."),
        click.option("--working-dir", "-w", default=None, help="The working directory (default is cwd)."),
        click.option("--debug", "-d", default=None, is_flag=True, help="Run in debug mode."),
        click.option("--version", "-v", default=None, is_flag=True, help="Print the version."),
    ]

    def __init__(self):
        self.exit_status = 0
        self.working_dir = None
        self.version = False
        self.debug = False

    def update(self, kwargs):
        for key, value in kwargs.items():
            if value is not None:
                setattr(self, key, value)

    @staticmethod
    def add_options(func):
        for option in reversed(RunConfig.options):
            func = option(func)
        return func


RunConfig.pass_config = staticmethod(
    click.make_pass_decorator(RunConfig, ensure=True)
)


@click.group(invoke_without_command=True)
@RunConfig.add_options
@RunConfig.pass_config
@click.pass_context
def cli(ctx, config, **kwargs):
    config.update(kwargs)

    if ctx.invoked_subcommand is None:
        # Run default command (run)
        return ctx.invoke(run)


@cli.command()
@RunConfig.add_options
@RunConfig.pass_config
def run(config, **kwargs):
    """
    Execute a prompty script.
    """
    config.update(kwargs)

    if config.version:
        click.echo(prompty.__version__)
        return

    s = prompty.status.Status(config.exit_status, config.working_dir)

    p = prompty.prompt.Prompt(s)

    prompt = p.getPrompt()

    if config.debug and START:
        elapsed = datetime.datetime.now() - START
        sys.stdout.write("%d\n" % (elapsed.total_seconds()*1000))

    click.echo(prompt, nl=False)

    sys.exit(config.exit_status)


@cli.command()
def bashrc():
    """
    Print a .bashrc invocation line.
    """
    abs_path = os.path.abspath(sys.argv[0])
    click.echo("export PS1=\"\\$(%s \\$?)\"" % abs_path)


@cli.command()
def colours():
    """
    Print available prompty colours.
    """
    c = prompty.colours.Colours(prompty.functionContainer.FunctionContainer())
    for style in c.STYLES:
        for colour in c.COLOURS:
            print("%s%s : %s%s" % (c.startColour(colour, style=style, _wrap=False),
                                   style[c.NAME_KEY],
                                   colour[c.NAME_KEY],
                                   c.stopColour(_wrap=False)))


@cli.command()
def palette():
    """
    Print available prompty colour palette.
    """
    c = prompty.colours.Colours(prompty.functionContainer.FunctionContainer())
    for colour in c.PALETTE:
        print("%s%s%s" % (
            c.startColour(
                fgcolour=colour[c.FG_KEY],
                bgcolour=colour[c.BG_KEY],
                style=colour[c.STYLE_KEY],
                _wrap=False
            ),
            colour[c.NAME_KEY],
            c.stopColour(_wrap=False))
        )


@cli.command()
def list():
    """
    Show the list of prompty scripts.
    """
    print("list")
