#!/usr/bin/env python
"""
Initialize project directory.

Usage:
    pm init [options] project_id

Options: -n, --dry_run          Dry run.
         -c, --config           Config file [~/config/post_process.yaml]
"""

import os
import sys

from optparse import OptionParser
from pmtools.templates import get_make_templates
from pmtools.utils import *

LOG_NAME="pm"
from bcbio.log import logger, setup_logging
from bcbio.pipeline.config_loader import load_config


def main(project):
    config = load_config(options.config)
    setup_logging(config)

    ## Initialize directory
    print "Dry run: %s" % options.dry_run
    #sh(["mkdir", "tmp"], None, options.dry_run)
    cmd(os.mkdir, ["tmp", "oeiuoi"], None,  dry_run=options.dry_run)
    make = get_make_templates()
    print make['Makefile'].render()

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-n", "--dry_run", dest="dry_run", action="store_true", default=False)
    parser.add_option("-c", "--config", dest="config", action="store", default=os.path.join(os.getenv("HOME"), "config", "post_process.yaml"))
    (options, args) = parser.parse_args()
    main(*args)
