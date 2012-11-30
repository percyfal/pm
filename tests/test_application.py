"""Main application test"""
import unittest
from pm.utils import test
from utils.classes import BASEDIR
from pm.cli.admin import AdminController
from cement.core import handler

class ApplicationTest(test.PmTest):
    def test_application(self):
        """Test setting up main application"""
        print BASEDIR
        self.app = self.make_app()
        self._run_app()

class AdminTest(test.PmTest):
    def test_admin(self):
        """Test administration command"""
        self.app = self.make_app(argv=["admin"])
        handler.register(AdminController)
        res = self._run_app()
        print res
