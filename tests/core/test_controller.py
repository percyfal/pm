"""test controller"""
from ..classes import PmTest

class ControllerTest(PmTest):
    def test_controller(self):
        """Test setting up a controller"""
        self.app = self.make_app()
        self._run_app()

    def test_controller_help(self):
        """Test passing help"""
        self.app = self.make_app(argv=['-h'])
        self._run_app()
