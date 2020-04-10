Prompty [![Build Status](https://travis-ci.org/ltn100/prompty.svg?branch=develop)](https://travis-ci.org/ltn100/prompty) [![Documentation Status](https://readthedocs.org/projects/prompty/badge/?version=latest)](https://prompty.readthedocs.io/en/latest/) [![Coverage Status](https://coveralls.io/repos/ltn100/prompty/badge.svg?service=github)](https://coveralls.io/github/ltn100/prompty) [![PyPI version](https://badge.fury.io/py/prompty.svg)](https://pypi.org/project/prompty/) [![MIT license](http://img.shields.io/badge/license-MIT-blue.svg)](http://opensource.org/licenses/MIT)
=======

Prompty is a [command prompt](https://en.wikipedia.org/wiki/Command-line_interface#Command_prompt) [markup language](https://en.wikipedia.org/wiki/Markup_language).

The language is loosely modelled on the [LaTeX](https://en.wikipedia.org/wiki/LaTeX) markup language, used for typesetting.

Here is an example of the sort of interactive command prompt that can be built using prompty:

![prompty demonstration](./img/demo.gif)


# Installation

The latest version can be installed from PyPI using `pip`:

```bash
sudo pip install prompty
```

It is a good idea to test that prompty is working correctly before continuing. Run the `prompty` command on its own and ensure that there are no errors:

```bash
prompty
```

If all has gone well, you should see some colourful output. (If not, see the tip section below for some ideas).

In order for for prompty to be integrated into your bash prompt, you need to insert a line at the end of your `.bashrc` file so that it is called from your `PS1` environment variable:

```bash
prompty bashrc >> ~/.bashrc
```

Now re-source your updated `.bashrc` file:

```bash
source ~/.bashrc
```
(alternatively you can restart your shell session)

You should now see the default prompty prompt.

> **Tip:** If you get an error like "`prompty: command not found`", it is probably because you installed it locally as a non-root user (without `sudo`). This is fine, but you will need to call the prompty executable from its local path. The previous commands can be replaced with:
>
> `# Test that prompty works`  
> `~/.local/bin/prompty`
>
> `# Update .bashrc file`  
> `~/.local/bin/prompty bashrc >> ~/.bashrc`
>
> `# Reload .bashrc`  
> `source ~/.bashrc`

# Configuration

The configuration for prompty is defined in your `~/.local/share/prompty/prompty.cfg` file:

```cfg
[prompt]
prompt_file = default.prompty
```

The `prompt_file` variable specifies which prompty file is currently in use. The prompty files are located in `~/.local/share/prompty/`. You can change the configuration to use one of the pre-defined ones, or write your own.


# Examples

## Simple example

You can define a simple `.prompty` file like this:

```TeX
\green{\user}\space
\yellow{\hostname}\space
\blue[bold]{\workingdir}\space
\magenta[inverted]{(\repobranch )}\newline
\green[bold]{\unichar{0x27a5}}\space
```

And your prompt will end up looking like this:

![example](./img/example1.gif)


## A more verbose example

Here is a verbose example with comments to explain the syntax used:

```TeX
% comments are allowed
% and white-space does not matter!

% first the username
\lightblue{\user}

% then an @ symbol
@

% followed by the machine name
\green{\hostname}

% if we want an actual space, we do this:
\space

% now the working directory in a nice yellow.
% lets also make it bold!
\yellow[bold]{\workingdir}
\space

% now for the VCS repository branch
(\repobranch )
\space

% and finally we have the special $ sign
% (which actually turns into a # when you're root)
\dollar\space
```

This prompty script will achieve the following prompt:

![example](./img/example2.gif)


## More

[`elite.prompty`](./skel/elite.prompty):

![elite](./img/elite.png)


[`red.prompty`](./skel/red.prompty):

![red](./img/red.png)

For a more elaborate example, see [`~/.local/share/prompty/default.prompty`](./skel/default.prompty) (this is the one used for the animation at the top of this page).


# Documentation

Documentation is available at [readthedocs](https://prompty.readthedocs.io/en/latest/).