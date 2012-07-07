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

import argparse

from pmtools.templates import get_make_templates
from pmtools.utils import *
import pmtools.config
from pmtools.io import yes_or_no

LOG_NAME="pm"
from bcbio.log import logger, setup_logging
from bcbio.pipeline.config_loader import load_config
from bcbio.utils import safe_makedir


def main(pm_config_file, project):
    config = load_config(options.config)
    setup_logging(config)

    ## Initialize project directory
    project_dir = os.path.join(pmtools.config.project_root, project)
    project_git_dir = os.path.join(project_dir, project + "_git")
    project_grf_dir = os.path.join(project_dir, "grf")
    project_biodata_dir = os.path.join(project_dir, "biodata")
    project_intermediate_dir = os.path.join(project_dir, "intermediate")
    project_data_dir = os.path.join(project_dir, "data")
    
    if yes_or_no("Make project directory %s" % project_dir):
        cmd(safe_makedir, project_dir)

    make = get_make_templates()
    print make['Makefile'].render()

def _init_config(pm_config_file):
    if not os.path.exists(pm_config_file):
        print >> sys.stderr, "[main] No such file %s" % pmtools.environment.config_file
        return False
    
    cfg = pmtools.config.parse_ini()
    print cfg
    if not cfg.get("config", "projectroot") or not cfg.get("config", "repos"):
        print >> sys.stderr, "[main] No projectroot and/or repos entry in config"
        print >> sys.stderr, "[main] Please make sure you have defined an existing path 'projectroot' where project analysis directories reside"
        print >> sys.stderr, "[main] and 'repos' where project git repositories reside."
        return False
    return True

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="", prog="init")
    parser = OptionParser()
    parser.add_option("-n", "--dry_run", dest="dry_run", action="store_true", default=False)
    parser.add_option("-c", "--config", dest="config", action="store", default=os.path.join(os.getenv("HOME"), "config", "post_process.yaml"))
    (options, args) = parser.parse_args()
    # Set global
    pmtools.config.dry_run = options.dry_run

    if len(args) != 2:
        print __doc__
        sys.exit()
        
    pm_config_file=args[0]
    project = args[1]

    _init_config(pm_config_file)

    main(pm_config_file, project)
