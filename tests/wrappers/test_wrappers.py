import os
import unittest

import pm.wrappers as wrap
from pm.wrappers.gatk import GATKCalculateHsMetricsWrapper
from pm.core import program
import cStringIO
from cement.utils import shell
import subprocess

packet = cStringIO.StringIO()

class LsWrapper(wrap.BaseWrapper):
    class Meta:
        interface = wrap.IWrapper
        exe = "ls"
        cmd_args = [exe]
        
    def cmd_args(self, input_file="./"):
        if input_file:
            self._meta.cmd_args += [input_file]
        return self._meta.cmd_args

    def cl(self, input_file=""):
        return " ".join(self.cmd_args(input_file))

class DuWrapper(wrap.BaseWrapper):
    class Meta:
        interface = wrap.IWrapper
        exe = "du"
        cmd_args = [exe]
        
    def cmd_args(self, input_file="./"):
        if input_file:
            self._meta.cmd_args += [input_file]
        return self._meta.cmd_args

    def cl(self, input_file=""):
        return " ".join(self.cmd_args(input_file))

class TestWrapper(unittest.TestCase):
    def test_wrapper(self):
        """Test basic wrapper functionality"""
        lsw = LsWrapper()
        self.assertEqual(repr(lsw), "<class 'tests.wrappers.test_wrappers.LsWrapper'>")
        print str(lsw)
        print lsw.cmd_args()
        out= shell.exec_cmd(lsw.cmd_args())
        print out

    def test_gatk(self):
        """Test GATK"""
        gatk = GATKCalculateHsMetricsWrapper()
        print gatk
        print "name: " + str(gatk.__class__)

    def test_registering_wrapper(self):
        """Test registering a wrapper"""
        program.register(GATKCalculateHsMetricsWrapper())

    def test_pipeline(self):
        """Test running a simple pipeline"""
        ls = LsWrapper()
        du = DuWrapper()
        packet.write(ls.cl())
        packet.write("\n")
        packet.write(du.cl())
        print packet.getvalue()
        print shell.exec_cmd([ls.cl(), "\n", du.cl()])
