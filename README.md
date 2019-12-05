## Status

[![License](https://img.shields.io/github/license/whipper-team/whipper-plugin-eaclogger.svg)](https://github.com/whipper-team/whipper-plugin-eaclogger/blob/master/LICENSE)
[![Build Status](https://travis-ci.com/whipper-team/whipper-plugin-eaclogger.svg?branch=master)](https://travis-ci.com/whipper-team/whipper-plugin-eaclogger)
[![GitHub (pre-)release](https://img.shields.io/github/release/whipper-team/whipper-plugin-eaclogger/all.svg)](https://github.com/whipper-team/whipper-plugin-eaclogger/releases/latest)

## Logger information

This logger plugin for whipper provides text reports structured in a way that
carefully mimics EAC's generated ones (except for the checksum). Unless you've
got particular requirements, I suggest using whipper's default logger.

The logger should be feature complete so future development will consist
mainly of bugfixes.

If you're looking for the analogous (legacy) morituri plugin, it can be found
[here](https://github.com/whipper-team/morituri-plugin-eaclogger).

## License

Licensed under the [ISC license](https://github.com/whipper-team/whipper-plugin-eaclogger/blob/master/LICENSE).

## Instructions

To use this plugin:

* build it:

    ```bash
    git clone https://github.com/whipper-team/whipper-plugin-eaclogger.git
    cd whipper-plugin-eaclogger
    python3 setup.py bdist_egg
    ```

* copy it to your local plugin directory:

    ```bash
    export XDG_DATA_HOME=${XDG_DATA_HOME:-"${HOME}/.local/share"}
    mkdir -p "$XDG_DATA_HOME/whipper/plugins"
    cp dist/whipper_plugin_eaclogger*.egg "$XDG_DATA_HOME/whipper/plugins"
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
python3 setup.py develop --install-dir=path/to/checkout/of/whipper
```
