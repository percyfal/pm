"""Pm2 admin controller module"""
import os
import yaml
import pandas as pd
from cement.core import controller
from pm.core.controller import PmAbstractBaseController
from pm.experiment import setup_project
from pm.lib.utils import update, config_to_dict

class AdminController(PmAbstractBaseController):
    """
    pm2 administration
    """
    class Meta:
        label = 'admin'
        description = 'Project administration'
        arguments = [
            (['project_id'], dict(help="", nargs="?", action="store")),
            (['--alias'], dict(help="", nargs="?", action="store")),
            (['--data'], dict(help="Data directory", nargs="?", action="store", default="")),
            ]

    @controller.expose(hide=True)
    def default(self):
        print self._help_text

    @controller.expose(help="Delete project from database")
    def delete(self):
        if not self._check_pargs(["project_id"]):
            return
        self.app.config.del_section("projects", subsection=self.pargs.project_id)
        self.app.config.save({'projects':self.app.config.get_section_dict("projects")}, self.app._meta.project_config)

    @controller.expose(help="Add project to database")
    def add(self):
        if not self._check_pargs(["project_id"]):
            return
        path = os.path.abspath(self.pargs.project_id.rstrip(os.sep))
        project_id = os.path.basename(path)
        if self.app.config.has_section("projects", subsection=project_id):
            self.app.log.warn("project id {} already exists".format(project_id))
            return
        self.app.config.add_section("projects", subsection=project_id)
        self.app.config.set("projects", "path", subsection=project_id, value=path)
        self.app.config.set("projects", "alias", subsection=project_id, value=self.pargs.alias)
        self.app.config.save({'projects':self.app.config.get_section_dict("projects")}, self.app._meta.project_config)

    @controller.expose(help="Add alias to project")
    def add_alias(self):
        if not self._check_pargs(["project_id", "alias"]):
            return
        if not self.app.config.has_section("projects", subsection=self.pargs.project_id):
            self.app.log.warn("no such project {}".format(self.pargs.project_id))
            return
        self.app.config.set("projects", "alias", subsection=self.pargs.project_id, value=self.pargs.alias)
        self.app.config.save({'projects':self.app.config.get_section_dict("projects")}, self.app._meta.project_config)

    @controller.expose(help="List projects")
    def ls(self):
        #self.app._output_data['stdout'].write(project.transpose())
        projects = pd.DataFrame(self.app.config.get_section_dict("projects"))
        print projects.transpose()

    @controller.expose(help="Setup a project. Samples have to be organize as sample/samplerungroup/samplerunid")
    def setup(self):
        if not self._check_pargs(["project_id"]):
            return
        if not self.app.config.has_section("projects", subsection=self.pargs.project_id):
            self.app.log.warn("No such project {}".format(self.pargs.project_id))
            return
        try:
            samples = setup_project(os.path.join(self.app.config.get("projects", "path", subsection=self.pargs.project_id), self.pargs.data))
            print pd.Series(config_to_dict(samples))
        except IOError:
            self.app.log.warn("no samples found for {}".format(self.pargs.project_id))
        # Save sampes to configuration
        sampleconf = os.path.join(self.app.config.get("projects", "path", subsection=self.pargs.project_id), "config", "samples.yaml")
        if not os.path.exists(os.path.dirname(sampleconf)):
            os.mkdir(os.path.dirname(sampleconf))
            config = {}
        else:
            with open(sampleconf) as fh:
                config = yaml.load(fh)
            config = update(config, samples)


