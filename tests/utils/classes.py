import os
from cement.core import backend, handler, output
from cement.utils import test, shell

LOG = backend.minimal_logger(__name__)

BASEDIR = os.path.join(os.path.dirname(__file__), os.pardir)

from pm.cli import PmMainApp

## Set default configuration
filedir = os.path.abspath(os.curdir)
config_defaults = backend.defaults('config', 'project','log', 'bcbio')
config_defaults['project']['root']  = os.path.join(filedir, "data", "projects")
config_defaults['config']['ignore'] = ["slurm*", "tmp*"]
config_defaults['log']['level']  = "INFO"
config_defaults['log']['file']  = os.path.join(filedir, "log", "pm.log")

def safe_makedir(dname):
    """Make directory"""
    if not os.path.exists(dname):
        try:
            os.makedirs(dname)
        except OSError:
            if not os.path.isdir(dname):
                raise
    else:
        print "Directory %s already exists" % dname
    return dname


