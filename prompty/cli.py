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

import prompty

# Should be overridden by bin/prompty
START = 0


class RunConfig(object):
    options = [
        # All options should have default=None
        # Set the real defaults in __init__() below
        click.option("--exit-status", "-e", default=None, type=int, help="The exit status of the last command. Also "
                                                                         "implies -W and -n."),
        click.option("--wrap", "-W", default=None, is_flag=True, help="Wrap non-printing characters with \\001 and "
                                                                      "\\002 to maintain correct line length."),
        click.option("--no-nl", "-n", default=None, is_flag=True, help="Do not output the trailing newline."),
        click.option("--working-dir", "-w", default=None, help="The working directory (default is cwd)."),
        click.option("--debug", "-d", default=None, is_flag=True, help="Run in debug mode."),
        click.option("--version", "-v", default=None, is_flag=True, help="Print the version."),
    ]

    def __init__(self):
        self.exit_status = None
        self.working_dir = None
        self.version = False
        self.debug = False
        self.no_nl = False
        self.wrap = False

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


@click.group(
    invoke_without_command=True,
    context_settings={"help_option_names": ["-h", "--help"]}
)
@RunConfig.add_options
@RunConfig.pass_config
@click.pass_context
def cli(ctx, config, **kwargs):
    """
    Promty is a bash prompt markup language. Use one of the COMMANDS below:
    """
    config.update(kwargs)

    if ctx.invoked_subcommand is None:
        # Run default command (run)
        return ctx.invoke(run)


@cli.command()
@click.argument("script", required=False)
@RunConfig.add_options
@RunConfig.pass_config
def run(config, script, **kwargs):
    """
    Execute a prompty script (default COMMAND).
    """
    config.update(kwargs)

    if config.version:
        click.echo(prompty.__version__)
        return

    if config.exit_status is None:
        # Probably called from CLI
        config.exit_status = 0
    else:
        # Probably called from PS1
        config.wrap = True
        config.no_nl = True

    status = prompty.status.Status(config.exit_status, config.working_dir)
    status.wrap = config.wrap

    prompt = prompty.prompt.Prompt(status)

    if script is not None:
        script_filepath = prompt.config.get_prompt_file_path(script)
        if not script_filepath:
            raise click.BadParameter("Prompty file '{}' not found".format(script))
        prompt.config.load_prompt_file(script_filepath)

    if config.debug and START:
        elapsed = datetime.datetime.now() - START
        sys.stdout.write("%d\n" % (elapsed.total_seconds()*1000))

    click.echo(prompt.get_prompt(), nl=(not config.no_nl), color=True)

    sys.exit(config.exit_status)


@cli.command()
def gen_bashrc():
    """
    Print a .bashrc invocation line.
    """
    abs_path = os.path.abspath(sys.argv[0])
    click.echo("export PS1=\"\\$(%s -e \\$?)\"" % abs_path)


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
                c.startcolour(colour, style=style),
                style[c.NAME_KEY],
                colour[c.NAME_KEY],
                c.stopcolour())
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
            c.startcolour(
                fgcolour=colour[c.FG_KEY],
                bgcolour=colour[c.BG_KEY],
                style=colour[c.STYLE_KEY]
            ),
            colour[c.NAME_KEY],
            c.stopcolour())
        )


@cli.command()
@click.option("--full", "-f", is_flag=True, help="Render the output of each prompty script.")
def ls(full):
    """
    Show the list of prompty scripts.
    """
    status = prompty.status.Status()
    status.wrap = False
    prompt = prompty.prompt.Prompt(status)
    current_prompt_file = prompt.config.prompt_file

    click.echo("Prompty files:")

    for filepath in prompt.config.get_prompt_files():
        base, ext = os.path.splitext(os.path.basename(filepath))

        if full:
            if current_prompt_file == filepath:
                base = base + " (current)"
            click.echo(chr(0x2554), nl=False)
            click.echo(chr(0x2550)*(len(base)+2), nl=False)
            click.echo(chr(0x2557))

            click.echo(chr(0x2551), nl=False)
            click.echo(" "+base+" ", nl=False)
            click.echo(chr(0x2551))

            click.echo(chr(0x255a), nl=False)
            click.echo(chr(0x2550)*(len(base)+2), nl=False)
            click.echo(chr(0x255d))

            prompt.compiler.clear()
            prompt.config.prompt_file = filepath
            prompt.config.load_prompt_file()
            click.echo(prompt.get_prompt(), nl=False)
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
    status = prompty.status.Status()
    prompt = prompty.prompt.Prompt(status)

    file_with_ext = file+".prompty"
    files = [os.path.basename(f) for f in prompt.config.get_prompt_files()]
    if file_with_ext not in files:
        raise click.BadParameter("Prompty file '{}' not found".format(file_with_ext))

    status = prompty.status.Status()
    config = prompty.config.Config()
    config.load(status.user_dir.get_config_file())
    config.config_parser.set('prompt', 'prompt_file', file_with_ext)
    config.save()
