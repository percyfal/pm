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
import pmtools.environment
from pmtools.io import yes_or_no

LOG_NAME="pm"
from bcbio.log import logger, setup_logging
from bcbio.pipeline.config_loader import load_config
from bcbio.utils import safe_makedir


def main(project):
    config = load_config(options.config)
    setup_logging(config)

    ## Initialize project directory
    project_dir = os.path.join(config('config', 'projectroot'), project)
    project_git_dir = os.path.join(project_dir, project + "_git")
    project_grf_dir = os.path.join(project_dir, "grf")
    project_biodata_dir = os.path.join(project_dir, "biodata")
    project_intermediate_dir = os.path.join(project_dir, "intermediate")
    project_data_dir = os.path.join(project_dir, "data")
    
    if yes_or_no("Make project directory "):
        cmd(safe_makedir, project_dir)

    make = get_make_templates()
    print make['Makefile'].render()

if __name__ == "__main__":
    parser = OptionParser()
    parser.add_option("-n", "--dry_run", dest="dry_run", action="store_true", default=False)
    parser.add_option("-c", "--config", dest="config", action="store", default=os.path.join(os.getenv("HOME"), "config", "post_process.yaml"))
    (options, args) = parser.parse_args()
    # Set global
    pmtools.environment.dry_run = options.dry_run
    main(*args)
