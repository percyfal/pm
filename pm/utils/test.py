import os
from cement.core import backend, handler, output
from cement.utils import test, shell
from pm.cli import PmMainApp

import scilifelab
SCILIFETEST=os.path.join(os.path.dirname(scilifelab.__file__), os.pardir, "tests", "full", "data")

LOG = backend.minimal_logger(__name__)

config_defaults = backend.defaults('config', 'projects','log', 'bcbio')
config_defaults['log']['level']  = "INFO"
config_defaults['log']['file']  = os.path.join(os.curdir, "log", "pm.log")
config_defaults['projects']['J.Doe_00_01'] = {'alias':"null", 'path':os.path.join(SCILIFETEST, "production", "J.Doe_00_01")}

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
            
