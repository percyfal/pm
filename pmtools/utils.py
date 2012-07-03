"""
utils
"""

import sys
import subprocess

from bcbio.log import logger2
import pmtools.environment

def dry(message, func, *args, **kw):
    logger2.info(message)
    if pmtools.environment.dry_run:
        return
    return func(*args, **kw)

def sh(cl, message=None, out_handle=sys.stdout):
    """Run an external command"""
    if message is None:
        message = " ".join(cl)
    logger2.info(message)
    if dry_run:
        return
    return subprocess.check_call(" ".join(cl), stdout=out_handle)

def cmd(fn, *args,  **kwargs):
    # if message is None:
    #     message = " ".join([str(fn.__name__), " ".join(*args)])
    # logger2.info(message)
    # if dry_run:
    #     return
    if pmtools.environment.dry_run:
        return
    fn(*args, **kwargs)

