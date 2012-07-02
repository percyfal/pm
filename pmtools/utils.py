"""
utils
"""

import sys
import subprocess

from bcbio.log import logger2

def sh(cl, message=None, dry_run=False, out_handle=sys.stdout):
    """Run an external command"""
    if message is None:
        message = " ".join(cl)
    logger2.info(message)
    if dry_run:
        return
    return subprocess.check_call(" ".join(cl), stdout=out_handle)

def cmd(fn, args=[], message=None, dry_run=False, out_handle=sys.stdout, **kwargs):
    if message is None:
        message = " ".join([fn, " ".join(args)])
    logger2.info(message)
    if dry_run:
        return
    fn(args, kwargs)
