import os
import sys
import re
import shutil
import logbook

LOG = logbook.Logger(__name__)

has_ngstestdata = False

# Constants
ARCHIVE = os.path.join(os.path.dirname(__file__), "data", "archive")
PRODUCTION = os.path.join(os.path.dirname(__file__), "data", "production")
PROJECTS = os.path.join(os.path.dirname(__file__), "data", "projects")

has_ngstestdata = False
try:
    import ngstestdata as ntd
    has_ngstestdata = True
    datadir = os.path.join(os.path.dirname(ntd.__file__), os.pardir, "data")
except ImportError:
    LOG.warn("Module ngstestdata not found. Not running bcbio")

def setUpModule():
    if not has_ngstestdata:
        return
    LOG.info("Running setUpModule")
    _check_requirements()
    _setup_illumina_data(datadir)
    

def _check_requirements():
    """Assert the existence of paths and programs"""
    envvars = ["PICARD_HOME", "GATK_HOME"]
    for ev in envvars:
        if not os.getenv(ev, None):
            LOG.warn("Required environment variable {} missing".format({}))
            sys.exit()

def _setup_illumina_data(datadir):
    prjdir = os.path.join(datadir, "projects")
    outdir = os.path.join(os.path.dirname(__file__), "data", "projects")
    for root, dirs, files in os.walk(prjdir):
        proot = os.path.relpath(root, prjdir)
        if len(proot.split(os.sep)) <= 2:
            continue
        if not files:
            continue
        out_d = os.path.join(outdir, proot)
        if not os.path.exists(out_d):
            os.makedirs(out_d)
        (fc_date, fc_name) = os.path.basename(root).split("_")
        fqfiles = sorted([x for x in files if re.search("fastq", x)])
        for f in files:
            src = os.path.join(root, f)
            tgt = os.path.join(out_d, f)
            if not os.path.exists(os.path.join(out_d, f)):
                LOG.info("copying file from {} to {}".format(src, tgt))
                shutil.copyfile(src, tgt)

