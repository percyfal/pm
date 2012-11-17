"""Pm2 admin controller module"""
import os
import yaml
from cement.core import controller
from pm.core.controller import PmAbstractBaseController

class AdminController(PmAbstractBaseController):
    """
    pm2 administration
    """
    class Meta:
        label = 'admin'
        description = 'Project administration'
        arguments = [
            (['project_id'], dict(help="", nargs="?", action="store")),
            ]

    @controller.expose(hide=True)
    def default(self):
        print self._help_text


    @controller.expose(help="Add project to database")
    def add(self):
        if not self._check_pargs(["project_id"]):
            return
        if not os.path.exists(self.app._meta.project_config):
            config = {}
        else:
            with open(self.app._meta.project_config) as fh:
                config = yaml.load(fh)
                if config is None:
                    config = {}
        project_id = os.path.basename(self.pargs.project_id.rstrip(os.sep))
        print project_id
        print self.pargs.project_id
        if not project_id in config:
            config[project_id] = {'path':os.path.abspath(self.app.pargs.project_id)}
        print config
        with open(self.app._meta.project_config, "w") as fh:
            fh.write(yaml.safe_dump(config))
