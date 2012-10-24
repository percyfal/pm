import os
from cement.core import backend, handler, output
from cement.utils import test, shell
from pm.cli import PmMainApp

## Set default configuration
filedir = os.path.abspath(os.curdir)
config_defaults = backend.defaults('config', 'project','log')
config_defaults['project']['root']  = os.path.join(filedir, "data", "projects")
config_defaults['config']['ignore'] = ["slurm*", "tmp*"]
config_defaults['log']['level']  = "INFO"
config_defaults['log']['file']  = os.path.join(filedir, "log", "pm.log")

def safe_makedir(dname):
    """Make directory"""
    if not os.path.exists(dname):
        try:
            os.makedirs(dname)
        except OSError:
            if not os.path.isdir(dname):
                raise
    else:
        print "Directory %s already exists" % dname
    return dname


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

## Main pm test 
class PmTest(test.CementTestCase):
    app_class = PmTestApp
    app = None
    OUTPUT_FILES = []

    def setUp(self):
        pass
        
    def _run_app(self):
        try:
            self.app.setup()
            self.app.run()
            #self.app.render(self.app._output_data)
        finally:
            self.app.close()
            
