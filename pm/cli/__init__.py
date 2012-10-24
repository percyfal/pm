"""pm cli module"""

from cement.core import foundation
from pm.core.controller import PmBaseController

class PmMainApp(foundation.CementApp):
    """
    Main pm application.
    """
    class Meta:
        label = "pm"
        base_controller = PmBaseController

    def __init__(self, **kw):
        super(PmMainApp, self).__init__(**kw)

    def setup(self):
        super(PmMainApp, self).setup()
