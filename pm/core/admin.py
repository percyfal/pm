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
        path = self.pargs.project_id.rstrip(os.sep)
        project_id = os.path.basename(path)
        self.app.config.add_section("projects", subsection=project_id)
        self.app.config.save()
        self.app.config.set("projects", "path", subsection=project_id, value=path)
        print self.app.config.get_section_dict("projects")
        with open(self.app._meta.project_config, "w") as fh:
            fh.write(yaml.safe_dump(config))
