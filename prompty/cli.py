#!/usr/bin/env python
# vim:set softtabstop=4 shiftwidth=4 tabstop=4 expandtab:
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from builtins import chr
from future.utils import iteritems

# Import external modules
import datetime
import sys
import os
import getopt
import codecs
import click
from collections import OrderedDict

import prompty

# Should be overridden by bin/prompty
START = 0


class RunConfig(object):
    options = [
        # All options should have default=None
        # Set the real defaults in __init__() below
        click.option("--exit-status", "-e", default=None, type=int, help="The exit status of the last command. Also "
                                                                         "implies -W -n -r."),
        click.option("--wrap", "-W", default=None, is_flag=True, help="Wrap non-printing characters with \\001 and "
                                                                      "\\002 to maintain correct line length."),
        click.option("--no-nl", "-n", default=None, is_flag=True, help="Do not output the trailing newline."),
        click.option("--raw", "-r", default=None, is_flag=True, help="Print raw output (no titles or boxes)."),
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
        self.raw = False

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
@click.argument("scripts", nargs=-1)
@click.option("--all", "-a", is_flag=True, help="Run all installed prompty scripts.")
@RunConfig.add_options
@RunConfig.pass_config
def run(config, all, scripts, **kwargs):
    """
    Execute a prompty script (default).

    `run` is the default command, if no other is given.

    If multiple SCRIPTS are provided, each one will be executed.
    SCRIPTS can either be absolute path names or short names of
    those installed in the ~/.local/share/prompty/ directory.
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
        config.raw = True

    status = prompty.status.Status(config.exit_status, config.working_dir)
    status.wrap = config.wrap

    if all:
        # Print installed all scripts
        prompt = prompty.prompt.Prompt(status)
        scripts = [os.path.splitext(os.path.basename(s))[0] for s in prompt.config.get_prompt_files()]

    prompts = OrderedDict()
    for script in scripts:
        prompt = prompty.prompt.Prompt(status)
        script_filepath = prompt.config.get_prompt_file_path(script)
        if not script_filepath:
            raise click.BadParameter("Prompty file '{}' not found".format(script))
        prompt.config.load_prompt_file(script_filepath)
        prompts[script] = prompt

    if not prompts:
        # Add default
        prompt = prompty.prompt.Prompt(status)
        prompts["{} (current)".format(os.path.basename(prompt.config.prompt_file))] = prompt

    for file, prompt in iteritems(prompts):
        if config.raw:
            click.echo(prompt.get_prompt(), nl=(not config.no_nl), color=True)
        else:
            prompt.status.window.column -= 2
            print_box(file, prompt.get_prompt())
            prompt.status.window.column += 2

    if config.debug and START:
        elapsed = datetime.datetime.now() - START
        sys.stdout.write("Run time: %dms\n" % (elapsed.total_seconds()*1000))

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
@click.option("--raw", "-r", is_flag=True, help="Print raw filenames")
def ls(raw):
    """
    Show the list of prompty scripts.
    """
    status = prompty.status.Status()
    status.wrap = False
    prompt = prompty.prompt.Prompt(status)
    current_prompt_file = prompt.config.prompt_file

    if not raw:
        click.echo("Prompty files:")

    for filepath in prompt.config.get_prompt_files():
        base = os.path.basename(filepath)
        if raw:
            leader = ""
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


def print_box(title, contents):
    cols = prompty.status.Status().window.column

    # Add fake cursor to end  of prompt
    contents += chr(9608)

    if not cols:
        # Print simple
        click.echo(title)
        click.echo(chr(0x2550)*len(title))
        click.echo(contents, color=True)
        click.echo()
        return

    # Print with boxes

    # Top bar
    click.echo(chr(0x2554), nl=False)
    click.echo(chr(0x2550)*(len(title)+2), nl=False)
    click.echo(chr(0x2566), nl=False)
    click.echo(chr(0x2550)*(cols-(len(title)+5)), nl=False)
    click.echo(chr(0x2557), nl=False)
    click.echo()

    # Title line
    click.echo(chr(0x2551), nl=False)
    click.echo(" "+title+" ", nl=False)
    click.echo(chr(0x2551), nl=False)
    click.echo(" "*(cols-(len(title)+5)), nl=False)
    click.echo(chr(0x2551), nl=False)
    click.echo()

    # Below title
    click.echo(chr(0x2560), nl=False)
    click.echo(chr(0x2550)*(len(title)+2), nl=False)
    click.echo(chr(0x255d), nl=False)
    click.echo(" "*(cols-(len(title)+5)), nl=False)
    click.echo(chr(0x2551), nl=False)
    click.echo()

    # Contents line
    contents = add_border(contents, chr(0x2551), cols)
    click.echo(contents, color=True, nl=False)
    click.echo()

    # Below contents
    click.echo(chr(0x255a), nl=False)
    click.echo(chr(0x2550)*(cols-2), nl=False)
    click.echo(chr(0x255d), nl=False)
    click.echo()


def add_border(contents, border_chars, cols):
    new_lines = []
    for line in contents.splitlines():
        rpad = " "*(cols-(len(escape_ansi(line))+2))
        new_lines.append(border_chars + line + rpad + border_chars)
    return "\n".join(new_lines)


def escape_ansi(line):
    import re
    ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')
    return ansi_escape.sub('', line)
