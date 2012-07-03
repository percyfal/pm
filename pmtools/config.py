"""
Configuration settings.
"""

import os

from ConfigParser import SafeConfigParser

# Global configuration variables
config_file=None
dry_run = False
project_root = os.getenv("HOME")
repos=None

def parse_ini(cfg_file=os.path.join(os.getenv("HOME"), ".pmrc")):
    parser = SafeConfigParser()
    parser.read(cfg_file)
    return parser

