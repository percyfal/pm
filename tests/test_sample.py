"""
Test sample objects.

"""
import os 
import unittest
import yaml
from pm.experiment import Sample, SampleRun, Analysis, setup_project
from cement.core import backend

LOG = backend.minimal_logger(__name__)

class SampleTest(unittest.TestCase):
    def test_sample_class(self):
        pass

    def test_convert_samples(self):
        pass
