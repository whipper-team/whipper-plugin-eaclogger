from setuptools import setup

setup(
    name="morituri-eaclogger",
    version="0.2.4",
    description="""morituri EAC-style logger""",
    author="superveloman",
    maintainer="JoeLametta",
    packages=[
        'eaclogger',
        'eaclogger.logger'],
    entry_points="""
  [morituri.logger]
  eac = eaclogger.logger.eac:EacLogger
  """)
