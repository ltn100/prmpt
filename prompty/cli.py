#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from builtins import chr

# Import external modules
import datetime
import sys
import os
import getopt
import codecs
import click
import glob

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
def gen_bashrc():
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
    c.status.wrap = False
    for style in c.STYLES:
        for colour in c.COLOURS:
            click.echo("%s%s : %s%s" % (
                c.startColour(colour, style=style),
                style[c.NAME_KEY],
                colour[c.NAME_KEY],
                c.stopColour())
            )


@cli.command()
def palette():
    """
    Print available prompty colour palette.
    """
    c = prompty.colours.Colours(prompty.functionContainer.FunctionContainer())
    c.status.wrap = False
    for colour in c.PALETTE:
        click.echo("%s%s%s" % (
            c.startColour(
                fgcolour=colour[c.FG_KEY],
                bgcolour=colour[c.BG_KEY],
                style=colour[c.STYLE_KEY]
            ),
            colour[c.NAME_KEY],
            c.stopColour())
        )


@cli.command()
@click.option("--full", "-f", is_flag=True, help="Render the output of each prompty script.")
def list(full):
    """
    Show the list of prompty scripts.
    """
    status = prompty.status.Status()
    status.wrap = False
    prompt = prompty.prompt.Prompt(status)
    current_prompt_file = prompt.config.promptFile

    click.echo("Prompty files:")

    for filepath in _get_prompty_files(prompt.config):
        base, ext = os.path.splitext(os.path.basename(filepath))

        if full:
            if current_prompt_file == filepath:
                base = base + " (current)"
            click.echo(chr(0x2554), nl=False); click.echo(chr(0x2550)*(len(base)+2), nl=False); click.echo(chr(0x2557))
            click.echo(chr(0x2551), nl=False); click.echo(" "+base+" ", nl=False);              click.echo(chr(0x2551))
            click.echo(chr(0x255a), nl=False); click.echo(chr(0x2550)*(len(base)+2), nl=False); click.echo(chr(0x255d))

            prompt.compiler.clear()
            prompt.config.promptFile = filepath
            prompt.config.loadPromptFile()
            click.echo(prompt.getPrompt(), nl=False)
            click.echo(chr(9608))
            click.echo(chr(0x2500)*status.window.column)
        else:
            leader = "[*] " if current_prompt_file == filepath else "[ ] "
            click.echo(leader + base)


@cli.command()
@click.argument("file")
def use(file):
    """
    Change the current prompty file
    """
    file_with_ext = file+".prompty"
    files = [os.path.basename(f) for f in _get_prompty_files()]
    if file_with_ext not in files:
        raise click.BadParameter("Prompty file '{}' not found".format(file_with_ext))

    status = prompty.status.Status()
    config = prompty.config.Config()
    config.load(status.userDir.getConfigFile())
    config.configParser.set('prompt', 'prompt_file', file_with_ext)
    config.save()


def _get_prompty_files(config=None):
    status = prompty.status.Status()
    if config is None:
        config = prompty.config.Config()
    config.load(status.userDir.getConfigFile())
    return sorted(glob.glob(os.path.join(status.userDir.getDir(), "*.prompty")))
