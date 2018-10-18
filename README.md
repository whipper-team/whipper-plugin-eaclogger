## Status

[![Build Status](https://travis-ci.com/whipper-team/whipper-plugin-eaclogger.svg?branch=master)](https://travis-ci.com/whipper-team/whipper-plugin-eaclogger)

## Logger information

This logger plugin for whipper provides text reports structured in a way that
carefully mimics EAC's generated ones (except for the checksum). Unless you've
got particular requirements, I suggest using whipper's default logger.

The logger should be feature complete so future development will consist
mainly of bugfixes.

If you're looking for the analogous morituri plugin, it can be found
[here](https://github.com/whipper-team/morituri-plugin-eaclogger).

## Instructions

To use this plugin:

* build it:

    ```bash
    git clone https://github.com/whipper-team/whipper-plugin-eaclogger.git
    cd whipper-plugin-eaclogger
    python2 setup.py bdist_egg
    ```

* copy it to your plugin directory:

    ```bash
    export XDG_DATA_HOME=${XDG_DATA_HOME:-"${HOME}/.local/share"}
    mkdir -p $XDG_DATA_HOME/whipper/plugins
    cp dist/morituri_*egg $XDG_DATA_HOME/whipper/plugins
    ```

* verify that it gets recognized:

    ```bash
    whipper cd rip --help
    ```

  You should see `eac` as a possible logger.

* use it:

    ```bash
    whipper cd rip -L eac
    ```

## Developers

To use the plugin while developing uninstalled:

```bash
python2 setup.py develop --install-dir=path/to/checkout/of/whipper
```
