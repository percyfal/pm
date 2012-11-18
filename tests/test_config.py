"""
Test reading configuration files

Two configuration files for pm are required:

1. pm.conf
2. project.conf

"""
import unittest
import yaml
from utils.classes import PmTest
from mock import Mock

def setUpModule():
    with open("./data/config/project_summary.yaml") as fh:
        project_config = yaml.load(fh)


class ConfigTest(PmTest):
    def test_configuration(self):
        """Test reading pm and project configuration files"""
        self.app = self.make_app(argv = [])
        self._run_app()

        
