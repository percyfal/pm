"""
Test sample objects.

"""
import os 
import unittest
import yaml
from pm.experiment import Sample, SampleRun, Analysis, setup_project, SampleCollection, load_samples, save_samples
from cement.core import backend

LOG = backend.minimal_logger(__name__)

samples = {'sample1' : {'samplerun1':{'id':'sr1', 'group':'g1', 'analysis':[{'id':'analysis1', 'type':'align', 'label':'align', 'files':'files'}]},
                        'samplerun2':{'id':'sr2', 'group':'g2', 'analysis':[{'id':'analysis1', 'type':'align', 'label':'align', 'files':'files'}]}},
           'sample2' : {'samplerun1':{'id':'sr1', 'group':'g1', 'analysis':[{'id':'analysis1', 'type':'align', 'label':'align', 'files':'files'}]}},
           }
           

class SampleTest(unittest.TestCase):
    def setUp(self):
        with open("samples.yaml", "w") as fh:
            fh.write(yaml.dump(samples))

    def tearDown(self):
        pass

    def test_sample_collection(self):
        sc = SampleCollection(**samples)
        self.assertIs(type(sc), SampleCollection)
        for s in sc:
            self.assertIs(type(s), Sample)
            for sr in s:
                self.assertIs(type(sr), SampleRun)
                for a in sr:
                    self.assertIs(type(a), Analysis)

    def test_load_sample(self):
        """Test loading samples"""
        sc = load_samples("samples.yaml")
        self.assertIs(type(sc), SampleCollection)
        for s in sc:
            self.assertIs(type(s), Sample)
            for sr in s:
                self.assertIs(type(sr), SampleRun)
                for a in sr:
                    self.assertIs(type(a), Analysis)


    def test_save_samples(self):
        """Test saving samples"""
        save_samples("samples2.yaml", samples)
        with open("samples2.yaml") as fh:
            sample_conf = yaml.load(fh)
        self.assertEqual(sample_conf, samples)
