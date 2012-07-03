"""
Configuration settings.
"""

import os

from ConfigParser import SafeConfigParser

def parse_ini():
    parser = SafeConfigParser()
    parser.read(os.path.join(os.getenv("HOME"), ".pmrc"))
    return parser

# Global configuration variables
dry_run = False
project_root = os.getenv("HOME")
repos=None
