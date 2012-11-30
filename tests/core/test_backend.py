"""test backend"""
from ..classes import PmTest
from pm.cli.controller import PmBaseController

class ControllerTest(PmTest):
    def test_base_controller(self):
        """Test PmBaseController"""
        pm = PmBaseController()
        #print pm.pargs

        pm.pargs = ["test"]
        pm.config
