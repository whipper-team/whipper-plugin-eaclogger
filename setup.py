from setuptools import setup

setup(
    name="whipper-plugin-eaclogger",
    version="0.3.0",
    description="""A logger plugin for whipper which provides EAC style log reports""",
    author="JoeLametta, superveloman",
    maintainer="JoeLametta",
    url="https://github.com/whipper-team/whipper-plugin-eaclogger",
    packages=[
        "eaclogger",
        "eaclogger.logger"],
    entry_points="""
  [whipper.logger]
  eac = eaclogger.logger.eac:EacLogger
  """)
