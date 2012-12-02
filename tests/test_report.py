"""Main report test"""
import os
import unittest
from mako.template import Template

class ReportTest(unittest.TestCase):
    def setUp(self):
        self.tpl = {'conf':Template(filename=os.path.join(os.path.dirname(__file__), os.pardir, "templates", "sphinx", "conf.mako"))}
        self.d = {'project':"Test", 'project_lc':"test", 'author':"J.Doe", 'year':'2000', 'date':'1 Jan, 2000', 'description':'J Doe project'}

    def test_sphinx_conf(self):
        print self.tpl['conf'].render(**self.d)

    def test_project_summary(self):
        pass
