"""pm cli module"""
import os
from cStringIO import StringIO
from collections import OrderedDict
from cement.core import foundation, backend, hook
from pm.core.controller import PmBaseController
from pm.core.log import PmLogHandler
from pm.core.output import PmOutputHandler
from pm.ext import ext_yamlconfigparser
import pm.core.admin

LOG = backend.minimal_logger(__name__)    

class PmMainApp(foundation.CementApp):
    """
    Main pm application.
    """
    class Meta:
        label = "pm2"
        base_controller = PmBaseController
        log_handler = PmLogHandler
        output_handler = PmOutputHandler
        project_config = os.path.join(os.getenv("HOME"), ".pm2", "projects.yaml")
        sample_config = os.path.join("config", "samples.yaml")
        ## Add command handler here
        config_handler = ext_yamlconfigparser.YAMLParserConfigHandler
        # Setting up projects
        def f(p, x): return x
        samples_collection_function = f
        # For collecting results
        results_collection_handler = pm.core.admin.collect_results
        """A handler class that implements the IConfig interface."""
        program_config_files = None

    def __init__(self, **kw):
        super(PmMainApp, self).__init__(**kw)
        ## Add specific attributes here
        self.program_config = None
        
    def setup(self):
        super(PmMainApp, self).setup()
        # Setup command handler here
        self._setup_program_config()
        # Setup project and sample configuration files
        self._setup_project_config()
        # Setup output data handling here
        self._output_data = dict(stdout = StringIO(),
                                 stderr = StringIO(),
                                 tables = OrderedDict())

        # Hooks
        hook.define('post_setup_samples')

    def _setup_project_config(self):
        project_config = self.config.get("config", "project")
        sample_config = self.config.get("config", "sample")

    def _setup_program_config(self):
        # FIX ME: should use function similar to _resolve_config_handler to setup
        self.program_config = ext_yamlconfigparser.YAMLParserConfigHandler()
        if self._meta.program_config_files is None:
            user_home = os.path.abspath(os.path.expanduser(os.environ['HOME']))
            self._meta.program_config_files = [
                os.path.join(user_home, '.pm2', 'programs.yaml'),
                ]
        for _file in self._meta.program_config_files:
            self.program_config.parse_file(_file)
