"""test controller"""
from cement.core import backend
from ..classes import PmTest
from pm.core.controller import PmBaseController

class ControllerTest(PmTest):
    def test_base_controller(self):
        """Test PmBaseController"""
        pm = PmBaseController()
        #print pm.pargs

        pm.pargs = ["test"]
        pm.config
