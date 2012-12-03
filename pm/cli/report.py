"""Pm2 report controller module"""
import os
import yaml
import datetime
import pandas as pd
from os.path import join as pjoin
from cement.core import controller, backend, hook
from pm.cli.controller import PmAbstractBaseController
from pm.lib.utils import update, config_to_dict
from pm.experiment import setup_project

LOG = backend.minimal_logger(__name__)

now = datetime.datetime.now()

class ReportController(PmAbstractBaseController):
    """
    pm2 utilities
    """
    class Meta:
        label = 'report'
        description = 'Report generation functions'
        arguments = [
            (['project_id'], dict(help="Project id or path", nargs="?", action="store")),
            (['--id'], dict(help="Project id as it will show in configuration", nargs="?", action="store")),
            (['--alias'], dict(help="Project alias", nargs="?", action="store")),
            (['--data'], dict(help="Data directory", nargs="?", action="store", default="data")),
            ]

    @controller.expose(hide=True)
    def default(self):
        print self._help_text

    @controller.expose(help="Create sphinx documentation for project")
    def sphinx(self):
        if not self._check_project():
            return
        p = self.app.config.get_section_dict("projects", subsection=self.pargs.project_id)
        project_conf = {'project':self.pargs.project_id, 'project_lc':self.pargs.project_id, 
                        'author':self.app.config.get("user", "author"), 'year': now.year,
                        'date':now.strftime("%Y-%m-%d"), 'description': p.get("description", None)}
        self.app._meta.sphinx_report_function(None, None, project_conf, None)
        

