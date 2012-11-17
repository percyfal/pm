"""Pm controller module"""
import os
import sys
import re

from cement.core import interface, handler, controller, backend


# See paver.tasks.needs
# Will this even work? No way to get function name 
def requires(*args):
    """Specifies arguments which this task needs to run"""
    print args
    def entangle(func):
        req = args
        print dir(func)
        print func.label
        print func.func_dict
        print func.__class__
    return entangle

class PmBaseController(controller.CementBaseController):
    """
    This is the pm base controller.

    All other controllers are stacked on or extends this controller. 
    """
    class Meta:
        label = 'base'
        description = 'pm2 base controller'
        arguments = [
            (['-n', '--dry_run'], dict(help="dry run - don't actually do anything", action="store_true", default=False)),
            (['--force'], dict(help="force execution and bypass yes/no questions", action="store_true", default=False)),
            ]

    def _setup(self, app):
        super(PmBaseController, self)._setup(app)

    @controller.expose(hide=True)
    def default(self):
        print self._help_text

    #@requires("function")
    @controller.expose()
    def config(self):
        print "Config"
        

class PmAbstractBaseController(controller.CementBaseController):
    """ This is the pm abstract base controller. The controller allows
    shared options between different commands.

    All controllers should inherit from this class.
    """
    class Meta:
        label = 'abstract-base'

    # FIX ME: would want this to be a decorator
    def _check_pargs(self, pargs, msg=None):
        """Check that required list of pargs are present"""
        for p in pargs:
            if not self.pargs.__getattribute__(p):
                self.app.log.warn("Required argument '{}' lacking".format(p))
                return False
        return True

class PmAbstractExtendedBaseController(PmAbstractBaseController):
    """
    This is the pm extended abstract base controller.
    """
    class Meta:
        label = 'abstract-extended-base'
