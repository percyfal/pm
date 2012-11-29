import os
from cement.core import backend, handler, output
from cement.utils import test, shell
from pm.cli import PmMainApp

LOG = backend.minimal_logger(__name__)

config_defaults = backend.defaults('config', 'projects','log', 'bcbio')
config_defaults['log']['level']  = "INFO"
config_defaults['log']['file']  = os.path.join(os.curdir, "log", "pm.log")
# This should really be setup by test init script
config_defaults['projects']['J.Doe_00_01'] = {'alias':"null", 'path':os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "tests", "data", "projects", "J.Doe_00_01")}
config_defaults['projects']['J.Doe_00_02'] = {'alias':"null", 'path':os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "tests", "data", "projects", "J.Doe_00_02")}
config_defaults['projects']['J.Doe_00_03'] = {'alias':"null", 'path':os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "tests", "data", "projects", "J.Doe_00_03")}
# Project and sample default configuration files
config_defaults['config']['project'] = os.path.join(os.getenv("HOME"), ".pm2", "projects.yaml")
config_defaults['config']['sample'] = os.path.join("config", "samples.yaml")

## Output handler for tests
class PmTestOutputHandler(output.CementOutputHandler):
    class Meta:
        label = 'pmtest'

    def render(self, data, template = None):
        for key in data:
            if data[key]:
                print "{} => {}".format(key, data[key].getvalue())

## Testing app
class PmTestApp(PmMainApp):
    class Meta:
        argv = []
        config_files = []
        config_defaults = config_defaults
        output_handler = PmTestOutputHandler
        program_config_files = []

## Main pm test 
class PmTest(test.CementTestCase):
    app_class = PmTestApp
    app = None
    OUTPUT_FILES = []

    def setUp(self):
        super(PmTest, self).setUp()
        
    def _run_app(self):
        try:
            LOG.info("setting up app")
            self.app.setup()
            LOG.info("running  app")
            self.app.run()
            self.app.render(self.app._output_data)
        finally:
            LOG.info("closing app")
            self.app.close()
            
