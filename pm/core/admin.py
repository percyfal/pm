"""Pm2 admin controller module"""
import os
import yaml
import pandas as pd
from cement.core import controller, backend
from pm.core.controller import PmAbstractBaseController
from pm.experiment import setup_project
from pm.lib.utils import update, config_to_dict

LOG = backend.minimal_logger(__name__)

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
        if not os.path.exists(path):
            self.app.log.warn("No such path {}; skipping".format(path))
            return
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
        projects = pd.DataFrame(self.app.config.get_section_dict("projects"))
        self.app._output_data['stdout'].write("\nAvailable projects\n====================\n\n")
        self.app._output_data['stdout'].write(str(projects.transpose()))

    @controller.expose(help="Setup a project. Samples have to be organized as sample/samplerungroup/samplerunid")
    def setup(self):
        if not self._check_pargs(["project_id"]):
            return
        if not self.app.config.has_section("projects", subsection=self.pargs.project_id):
            self.app.log.warn("No such project {}".format(self.pargs.project_id))
            return
        try:
            samples = setup_project(os.path.join(self.app.config.get("projects", "path", subsection=self.pargs.project_id), self.pargs.data))
        except IOError:
            self.app.log.warn("no samples found for {}".format(self.pargs.project_id))
        # Save samples to configuration
        sampleconf = os.path.join(self.app.config.get("projects", "path", subsection=self.pargs.project_id), "config", "samples.yaml")
        if not os.path.exists(os.path.dirname(sampleconf)):
            os.mkdir(os.path.dirname(sampleconf))
            config = {}
        # If old config exists
        if os.path.exists(sampleconf):
            with open(sampleconf) as fh:
                config = yaml.load(fh)
            if config:
                config = update(samples, config)
            else:
                print "setting equal"
                print samples
                config = samples
        else:
            config = samples
        print "safe dump" + str(yaml.safe_dump(config_to_dict(config), default_flow_style=False, allow_unicode=True, width=1000))
        if config:
            LOG.info("Saving sample configuration to {}".format(sampleconf))
            with open(sampleconf, "w") as fh:
                fh.write(yaml.safe_dump(config_to_dict(config), default_flow_style=False, allow_unicode=True, width=1000))


