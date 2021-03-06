"""Main application test"""
import unittest
from utils.classes import PmTest, BASEDIR

class ApplicationTest(PmTest):
    def test_application(self):
        """Test setting up main application"""
        print BASEDIR
        self.app = self.make_app()
        self._run_app()

    ##Why doesn't the help function work?!?
    #@unittest.expectedFailure
    def test_application_help(self):
        """Test passing help to main application"""
        self.app = self.make_app(argv=['--help'])
        self.app.setup()
        res = self.app.run()
        pass

