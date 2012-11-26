"""test experiment"""
import os
from ..classes import PmTest
from pm.experiment import Project, setup_project
from .. import SCILIFEDIR

class ExperimentTest(PmTest):
    def test_experiment(self):
        s = setup_project(os.pardir)
        print s

