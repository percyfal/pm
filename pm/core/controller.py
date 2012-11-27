"""Pm controller module"""
import os
import sys
import re

from cement.core import interface, handler, controller, backend

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

    def _check_project(self):
        """Check that the required project exists in project config"""
        if not self._check_pargs(["project_id"]):
            return False
        if not self.app.config.has_section("projects", subsection=self.pargs.project_id):
            self.app.log.warn("No such project {}".format(self.pargs.project_id))
            return False
        return True


class PmAbstractExtendedBaseController(PmAbstractBaseController):
    """
    This is the pm extended abstract base controller.
    """
    class Meta:
        label = 'abstract-extended-base'
