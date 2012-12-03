"""Pm2 admin controller module"""
import os
import yaml
import pandas as pd
from os.path import join as pjoin
from cement.core import controller, backend, hook
from pm.cli.controller import PmAbstractBaseController
from pm.lib.utils import update, config_to_dict
from pm.experiment import setup_project, Sample, load_samples

LOG = backend.minimal_logger(__name__)

def collect_results(prjdir, sample):
    LOG.info("Collecting results for {}".format(sample))
    return

def _get_samples(app, project_id):
    """Get samples for a project"""
    path = os.path.abspath(pjoin(app.config.get("projects", "path", project_id), app._meta.sample_config))
    if not os.path.exists(path):
        LOG.warn("No sample configuration found for project {}; skipping".format(project_id))
        return
    samples = load_samples(path)
    # with open(path) as fh:
    #     samples = {k:Sample(**v) for k, v in yaml.load(fh).iteritems()}
    return samples

class AdminController(PmAbstractBaseController):
    """
    pm2 administration
    """
    class Meta:
        label = 'admin'
        description = 'Project administration'
        arguments = [
            (['project_id'], dict(help="Project id or path", nargs="?", action="store")),
            (['--id'], dict(help="Project id as it will show in configuration", nargs="?", action="store")),
            (['--alias'], dict(help="Project alias", nargs="?", action="store")),
            (['--data'], dict(help="Data directory", nargs="?", action="store", default="data")),
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
        if not self._check_project() or not self._check_pargs(["project_id", "alias"]):
            return
        self.app.config.set("projects", "alias", subsection=self.pargs.project_id, value=self.pargs.alias)
        self.app.config.save({'projects':self.app.config.get_section_dict("projects")}, self.app._meta.project_config)

    @controller.expose(help="List projects")
    def ls(self):
        if self.pargs.project_id:
            samples = _get_samples(self.app, self.pargs.project_id)
            samples = pd.DataFrame(samples)
            self.app._output_data['stdout'].write("\nSamples for project {}\n======================================\n\n".format(self.pargs.project_id))
            self.app._output_data['stdout'].write(str(samples.transpose().stack()))
        else:
            projects = pd.DataFrame(self.app.config.get_section_dict("projects"))
            self.app._output_data['stdout'].write("\nAvailable projects\n====================\n\n")
            self.app._output_data['stdout'].write(str(projects.transpose()))

    @controller.expose(help="Setup a project. Samples have to be organized as sample/samplerungroup/samplerunid")
    def setup(self):
        if not self._check_project():
            return
        path = pjoin(self.app.config.get("projects", "path", subsection=self.pargs.project_id), self.pargs.data)
        if not os.path.exists(path):
            self.app.log.warn("No such path '{}'; skipping".format(path))
            return
        try:
            self.app.log.info("Looking for samples in '{}'...".format(path))
            samples = setup_project(path)
            samples = self.app._meta.samples_collection_function(path, samples)
        except IOError:
            self.app.log.warn("no samples found for '{}'".format(self.pargs.project_id))
        # Save samples to configuration
        sampleconf = pjoin(self.app.config.get("projects", "path", subsection=self.pargs.project_id), self.app._meta.sample_config)
        if not os.path.exists(os.path.dirname(sampleconf)):
            os.mkdir(os.path.dirname(sampleconf))
            config = {}
        # If old config exists
        if os.path.exists(sampleconf):
            self.app.log.debug("opening existing sample configuration file {}".format(sampleconf))
            with open(sampleconf) as fh:
                config = yaml.load(fh)
            if config:
                config = update(config, samples)
            else:
                config = samples
        else:
            config = samples
        if config:
            LOG.info("Saving sample configuration to '{}'".format(sampleconf))
            with open(sampleconf, "w") as fh:
                fh.write(yaml.safe_dump(config_to_dict(config), default_flow_style=False, allow_unicode=True, width=1000))

    @controller.expose(help="Collect results for a project. Writes results to object store. This function exists for external pipelines to look in to.")
    def collect_results(self):
        if not self._check_project():
            return
        prjdir = os.path.join(self.app.config.get("projects", "path", subsection=self.pargs.project_id))
        samples = {}
        sampleconf = pjoin(prjdir, self.app._meta.sample_config)
        if os.path.exists(sampleconf):
            LOG.info("loading samples from {}".format(sampleconf))
            with open(sampleconf) as fh:
                samples = yaml.load(fh)
        # Process samples and add results according to function admin.collection
        for s in samples.iteritems():
            self.app._meta.results_collection_handler(prjdir, s)
