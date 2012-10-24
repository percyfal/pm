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
        description = 'pm base controller'
        arguments = [
            (['-n', '--dry_run'], dict(help="dry run - don't actually do anything", action="store_true", default=False)),
            (['--force'], dict(help="force execution and bypass yes/no questions", action="store_true", default=False)),
            ]

    def _setup(self, app):
        super(PmBaseController, self)._setup(app)

    @controller.expose(hide=True)
    def default(self):
        print self._help_text

class PmAbstractBaseController(controller.CementBaseController):
    """
    This is the pm abstract base controller.

    All controllers should inherit from this class.
    """
    class Meta:
        label = 'abstract-base'


class PmAbstractExtendedBaseController(PmAbstractBaseController):
    """
    This is the pm extended abstract base controller.
    """
    class Meta:
        label = 'abstract-extended-base'
