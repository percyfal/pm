"""pm cli module"""
from cStringIO import StringIO
from collections import OrderedDict
from cement.core import foundation
from pm.core.controller import PmBaseController
from pm.core.log import PmLogHandler

class PmMainApp(foundation.CementApp):
    """
    Main pm application.
    """
    class Meta:
        label = "pm"
        base_controller = PmBaseController
        log_handler = PmLogHandler
        ## Add command handler here

    def __init__(self, **kw):
        super(PmMainApp, self).__init__(**kw)
        ## Add specific attributes here, such as command

    def setup(self):
        super(PmMainApp, self).setup()
        ## Setup command handler here
        ## Setup output data handling here
        self._output_data = dict(stdout = cStringIO(),
                                 stderr = cStringIO(),
                                 tables = OrderedDict())
