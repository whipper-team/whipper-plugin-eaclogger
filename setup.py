from setuptools import setup
from eaclogger import __version__ as plugin_version

setup(
    name="whipper-plugin-eaclogger",
    version=plugin_version,
    description="A plugin for whipper which provides EAC style log reports",
    author="JoeLametta, supermanvelo",
    maintainer="JoeLametta",
    license="ISC License",
    url="https://github.com/whipper-team/whipper-plugin-eaclogger",
    packages=["eaclogger", "eaclogger.logger"],
    entry_points={
        "whipper.logger": [
            "eac = eaclogger.logger.eac:EacLogger"
        ]
    }
)
