"""
Test reading configuration files

Three configuration files for pm are accepted:

1. pm.yaml
2. project.yaml
3. program.yaml

"""
import os
import unittest
import yaml
from pm.utils import test
from mock import Mock
from pm.lib.utils import config_to_dict
from pm.core.admin import AdminController
from cement.core import handler, backend

LOG = backend.minimal_logger(__name__)

# FIX ME: separate module
from . import SCILIFETEST

def setUpModule():
    with open(os.path.join(SCILIFETEST, "config", "project_summary.yaml")) as fh:
        project_config = yaml.load(fh)

class ConfigTest(test.PmTest):
    def test_configuration(self):
        """Test reading pm and project configuration files"""
        self.app = self.make_app(argv = [])
        self._run_app()
        p_dict2 = {'programs':config_to_dict(self.app.program_config)}
        self.app.config.merge(p_dict2)
        self.assertEqual(self.app.config.get_section_dict("programs"), {})

    def test_config_parser(self):
        """Test config parser"""
        pass

    def test_sample_setup(self):
        """Test setting up a project"""
        self.app = self.make_app(argv = ["admin", "setup", "J.Doe_00_01"])
        LOG.info("Loading admin controller")
        handler.register(AdminController)
        self._run_app()
        samples_conf = os.path.join(SCILIFETEST, "production", "J.Doe_00_01", "config", "samples.yaml")
        with open(samples_conf) as fh:
            samples = yaml.load(fh)
        # NOTE: this is going to change 
        self.assertEqual(samples, {'P001_101_index3': {'120924_AC003CCCXX': {'tables': {}, 'id': '120924_AC003CCCXX', 'results': {}}, '121015_BB002BBBXX': {'tables': {}, 'id': '121015_BB002BBBXX', 'results': {}}}, 'P001_102_index6': {'120924_AC003CCCXX': {'tables': {}, 'id': '120924_AC003CCCXX', 'results': {}}}})
        os.unlink(samples_conf)
