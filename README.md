prompty
=======

[![Build Status](https://travis-ci.org/ltn100/prompty.svg?branch=master)](https://travis-ci.org/ltn100/prompty)
[![Code Health](https://landscape.io/github/ltn100/prompty/master/landscape.png)](https://landscape.io/github/ltn100/prompty/master)
[![MIT license](http://img.shields.io/badge/license-MIT-blue.svg)](http://opensource.org/licenses/MIT)
[![Badges](http://img.shields.io/badge/badges-shields.io-lightgrey.svg)](http://shields.io)

### Preparing for an [0.1 release](https://github.com/ltn100/prompty/issues?q=milestone%3Av0.1)!


What is prompty?
----------------

Prompty is a **command prompt markup language**.

What does that mean? Well, your [command prompt](https://en.wikipedia.org/wiki/Command-line_interface#Command_prompt) is the bit of text you see when you load up a Linux command terminal. It may look a bit like this:

    user@hostname $ █

The prompt you see will vary depending on the machine you are connected to, and who you are logged in as. By default, most machines will have a fairly simple prompt, designed to be unobtrusive to any user. This is all well and good, but what if you want to get more specific information from your prompt? what if your prompt could be customised and adapted to the way YOU use the machine? software developers may want different information from sys-admins. What if you could add colour? git branch names? CPU load? Traditionally, you would customise your prompt by setting a PS1 environment variable. For example, to create the prompt above, the PS1 variable would be set to something like this:

```bash
export PS1="\u@\h \$ "
```

At this point it is fairly easy to make minor changes, but the complexity escalates very quickly if you want to do anything like add colour or branch statements. Here is an example of a prompt that uses colour and gives the current git branch name:

```bash
export PS1="\[\033[36m\]\u\[\033[m\]@\[\033[32m\]\h \[\033[33;1m\]\w\[\033[m\] (\$(git branch 2>/dev/null | grep '^*' | colrm 1 2)) \$ "
```

I think you'll agree that this is fairly impenetrable if it's the first time you'd seen it, and would take you a fair few minutes before you could start tweaking it to suit your needs. Perhaps what is needed is a *language* to describe, in easy-to-read terms, how the prompt is constructed?

Prompty is such a markup language. A [markup language](http://en.wikipedia.org/wiki/Markup_language) is something that can be used to describe the way text or information is displayed to the user. The prompty language takes its inspiration from the [LaTeX](http://en.wikipedia.org/wiki/LaTeX) document markup language, and aims to be as 'human-readable' as possible.

The above prompt in "prompty script" form would look like this:

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

% now for the git branch
(\gitbranch)
\space

% and finally we have the special $ sign
% (which actually turns into a # when you're root)
\dollar\space
```
