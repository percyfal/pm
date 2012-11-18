"""pm cli module"""
import os
from cStringIO import StringIO
from collections import OrderedDict
from cement.core import foundation
from pm.core.controller import PmBaseController
from pm.core.log import PmLogHandler
from pm.ext import ext_yamlconfigparser

class PmMainApp(foundation.CementApp):
    """
    Main pm application.
    """
    class Meta:
        label = "pm2"
        base_controller = PmBaseController
        log_handler = PmLogHandler
        project_config = os.path.join(os.getenv("HOME"), ".pm2", "projects.yaml")
        ## Add command handler here
        config_handler = ext_yamlconfigparser.YAMLParserConfigHandler
        """
        A handler class that implements the IConfig interface. 
        """

    def __init__(self, **kw):
        super(PmMainApp, self).__init__(**kw)
        ## Add specific attributes here, such as command

    def setup(self):
        super(PmMainApp, self).setup()
        ## Setup command handler here
        ## Setup output data handling here
        self._output_data = dict(stdout = StringIO(),
                                 stderr = StringIO(),
                                 tables = OrderedDict())


