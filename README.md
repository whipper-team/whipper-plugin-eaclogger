## Status
[![Build Status](https://travis-ci.org/JoeLametta/morituri-eaclogger.svg?branch=master)](https://travis-ci.org/JoeLametta/morituri-eaclogger)

## Logger information

This logger provides text reports structured in a way that carefully mimics EAC's generated ones. It is compatible with both whipper and morituri altough, regarding whipper, I suggest using the default logger unless you've particular requirements.

Eaclogger should be feature complete so future development will consist only of bugfixes.

## Instructions for morituri (and whipper before version [0.2.4](https://github.com/JoeLametta/whipper/releases/tag/v0.2.4))

To use this plugin:

* build it:

        git clone https://github.com/JoeLametta/morituri-eaclogger.git
        cd morituri-eaclogger
        python2 setup.py bdist_egg

* copy it to your plugin directory:

        mkdir -p $HOME/.morituri/plugins
        cp dist/morituri_*egg $HOME/.morituri/plugins

* verify that it gets recognized:

        rip cd rip --help

   You should see `eac` as a possible logger.

* use it:

        rip cd rip --logger=eac

## Instructions for whipper (since version [0.2.4](https://github.com/JoeLametta/whipper/releases/tag/v0.2.4))

To use this plugin:

* build it:

        git clone https://github.com/JoeLametta/morituri-eaclogger.git
        cd morituri-eaclogger
        python2 setup.py bdist_egg

* copy it to your plugin directory:

        export XDG_DATA_HOME=${XDG_DATA_HOME:-"${HOME}/.local/share"}
        mkdir -p $XDG_DATA_HOME/whipper/plugins
        cp dist/morituri_*egg $XDG_DATA_HOME/whipper/plugins

* verify that it gets recognized:

        rip cd rip --help

   You should see `eac` as a possible logger.

* use it:

        rip cd rip -L eac

## Developers

To use the plugin while developing uninstalled:

    python2 setup.py develop --install-dir=path/to/checkout/of/morituri
