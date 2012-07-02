#!/usr/bin/env python
"""Project management tools.

Usage:
    pm.py <command> [options]

Command: init                  Initialize a project
         clean                 Remove obsolete files
         deliver               Deliver data
         compress              Compress data
         sbatch_helper         Create sbatch scripts
         statusdb              Connect to statusdb

"""

import os
import sys
import subprocess

from pmtools.config import parse_ini

COMMANDS = ["init", "clean", "deliver", "compress", "sbatch_helper", "statusdb"]

def main(cmd, opts):
    
    if not cmd in COMMANDS:
        print >> sys.stderr, "[main] Unrecognized command '%s'" % cmd
        sys.exit()

    if not _validate_config():
        sys.exit()
        
    cl = ["%s.py" % cmd] + opts
    subprocess.check_call(cl, stdout=sys.stdout, stderr=sys.stderr)

def _validate_config():
    if not os.path.exists(os.path.join(os.getenv("HOME"), ".pmrc")):
        print >> sys.stderr, "[main] No config file ~/.pmrc"
        return False
    
    cfg = parse_ini()
    if not cfg.get("config", "projectroot") or not cfg.get("config", "repos"):
        print >> sys.stderr, "[main] No projectroot and/or repos entry in config"
        print >> sys.stderr, "[main] Please make sure you have defined an existing path 'projectroot' where project analysis directories reside"
        print >> sys.stderr, "[main] and 'repos' where project git repositories reside."
        return False
    return True
        

if __name__ == "__main__":
    if len(sys.argv) < 1:
        print __doc__
        sys.exit()

    args = sys.argv[1:]
    cmd = args[0]
    opts = args[1:]

    main(cmd, opts)
