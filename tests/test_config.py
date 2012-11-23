"""
Test reading configuration files

Three configuration files for pm are accepted:

1. pm.yaml
2. project.yaml
3. program.yaml

"""
import unittest
import yaml
from utils.classes import PmTest
from mock import Mock
from pm.lib.utils import config_to_dict

def setUpModule():
    with open("./data/config/project_summary.yaml") as fh:
        project_config = yaml.load(fh)
    print project_config

class ConfigTest(PmTest):
    def test_configuration(self):
        """Test reading pm and project configuration files"""
        self.app = self.make_app(argv = [])
        self._run_app()
        p_dict2 = {'programs':config_to_dict(self.app.program_config)}
        self.app.config.merge(p_dict2)
        print self.app.config.get_section_dict("programs")

    def test_config_parser(self):
        """Test config parser"""
        pass
