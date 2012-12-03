"""
Test sample objects.

"""
import os 
import unittest
import yaml
from pm.experiment import Sample, SampleRun, Analysis, setup_project, SampleCollection
from cement.core import backend

LOG = backend.minimal_logger(__name__)
samples = {'P001_101_index3': {'1_120924_AC003CCCXX_TGACCA': {'group': '120924_AC003CCCXX', 'id': '1_120924_AC003CCCXX_3', 'analysis': []}, '1_121015_BB002BBBXX_TGACCA': {'group': '121015_BB002BBBXX', 'id': '1_121015_BB002BBBXX_3', 'analysis': []}}, 'P001_102_index6': {'2_120924_AC003CCCXX_ACAGTG': {'group': '120924_AC003CCCXX', 'id': '2_120924_AC003CCCXX_5', 'analysis': []}}}

samples = {'sample1' : {'samplerun1':{'id':'sr1', 'group':'g1', 'analysis':[{'id':'analysis1', 'type':'align', 'label':'align', 'files':'files'}]},
                        'samplerun2':{'id':'sr2', 'group':'g2', 'analysis':[{'id':'analysis1', 'type':'align', 'label':'align', 'files':'files'}]}},
           'sample2' : {'samplerun1':{'id':'sr1', 'group':'g1', 'analysis':[{'id':'analysis1', 'type':'align', 'label':'align', 'files':'files'}]}},
           }
           

class SampleTest(unittest.TestCase):
    def test_sample_collection(self):
        sc = SampleCollection(**samples)
        self.assertIs(type(sc), SampleCollection)
        for s in sc:
            self.assertIs(type(s), Sample)
            for sr in s:
                self.assertIs(type(sr), SampleRun)
                for a in sr:
                    self.assertIs(type(a), Analysis)

    def test_sample_class(self):
        pass

    def test_convert_samples(self):
        pass
