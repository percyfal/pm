import os
import unittest
import luigi
import time
import cStringIO
import pm.wrappers as wrap
import pm.luigi.bwa as BWA
import pm.luigi.samtools as SAM
import pm.luigi.fastq as FASTQ
from cement.utils import shell
import subprocess
import ngstestdata as ntd

packet = cStringIO.StringIO()

bwa = "bwa"
bwaref = os.path.join(ntd.__path__[0], os.pardir, "data", "genomes", "Hsapiens", "hg19", "bwa", "chr11.fa")
bwaseqref = os.path.join(ntd.__path__[0], os.pardir, "data", "genomes", "Hsapiens", "hg19", "seq", "chr11.fa")
samtools = "samtools"
indir = os.path.join(os.path.dirname(__file__), os.pardir, "data", "projects", "J.Doe_00_01", "P001_101_index3", "121015_BB002BBBXX")
sample = "P001_101_index3_TGACCA_L001"
fastq1 = os.path.join(indir, sample + "_R1_001.fastq.gz")
fastq2 = os.path.join(indir, sample + "_R2_001.fastq.gz")
sai1 = os.path.join(sample + "_R1_001.sai")
sai2 = os.path.join(sample + "_R2_001.sai")
sam = os.path.join(sample + ".sam")
bam = os.path.join(sample + ".bam")

class TestLuigiWrappers(unittest.TestCase):
    def test_fastqln(self):
        luigi.run(['--local-scheduler', '--fastq', fastq1], main_task_cls=FASTQ.FastqFileLink)

    def test_bwaaln(self):
        luigi.run(['--local-scheduler', '--fastq', fastq1, '--bwaref', bwaref, '--indir', indir], main_task_cls=BWA.BwaAln)
        luigi.run(['--local-scheduler', '--fastq', fastq1, '--bwaref', bwaref, '--indir', indir], main_task_cls=BWA.BwaAln)

    def test_bwasampe(self):
        if os.path.exists(sam):
            os.unlink(sam)
        luigi.run(['--local-scheduler', '--sai1', sai1, '--sai2', sai2, '--indir', indir, '--bwaref', bwaref], main_task_cls=BWA.BwaSampe)

    def test_samtobam(self):
        luigi.run(['--local-scheduler', '--sam', sam], main_task_cls=SAM.SamToBam)

    def test_sortbam(self):
        luigi.run(['--local-scheduler', '--bam', bam], main_task_cls=SAM.SortBam)

    def test_set_cls(self):
        if os.path.exists(sam):
            os.unlink(sam)
        print SAM.SamToBam().my_cls
        luigi.run(['--local-scheduler', '--sam', sam], main_task_cls=SAM.SamToBam)
        SAM.SamToBam().my_cls = "BwaSampe"
        print SAM.SamToBam().my_cls
        if os.path.exists(sam):
            os.unlink(sam)
        luigi.run(['--local-scheduler', '--sam', sam], main_task_cls=SAM.SamToBam)

class LuigiExternalTaskFastqFile(luigi.ExternalTask):
    fastq = luigi.Parameter(default=None)

    def output(self):
        return luigi.LocalTarget(self.fastq)

class LuigiTaskBwaAln(luigi.Task):
    fastq = luigi.Parameter(default=None)

    def requires(self):
        return [LuigiExternalTaskFastqFile(self.fastq)]
    
    def output(self):
        return luigi.LocalTarget(os.path.join(os.path.dirname(__file__), os.path.basename(self.fastq.replace(".fastq.gz", ".sai"))))

    def run(self):
        for f in self.input():
            cl = [bwa, 'aln', '-t', "1", bwaref, f.fn, ">", os.path.join(os.path.dirname(__file__), os.path.basename(f.fn.replace(".fastq.gz", ".sai")))]
            out = shell.exec_cmd(" ".join(cl), shell=True)

class LuigiTaskBwaSampe(luigi.Task):
    fastq1 = luigi.Parameter(default=None)
    fastq2 = luigi.Parameter(default=None)
    
    def requires(self):
        return [LuigiTaskBwaAln(self.fastq1), LuigiTaskBwaAln(self.fastq2)]

    def output(self):
        return luigi.LocalTarget(os.path.join(os.path.dirname(__file__), os.path.basename(self.fastq1.replace(".fastq.gz", ".sam"))))
        
    def run(self):
        sai1 = self.input()[0]
        sai2 = self.input()[1]
        cl = [bwa, "sampe", bwaref, sai1.fn, sai2.fn, self.fastq1, self.fastq2, ">", self.output().fn]
        out = shell.exec_cmd(" ".join(cl), shell=True)

class LuigiTaskSamToBam(luigi.Task):
    fastq1 = luigi.Parameter(default=None)
    fastq2 = luigi.Parameter(default=None)

    def requires(self):
        return [LuigiTaskBwaSampe(self.fastq1, self.fastq2)]

    def output(self):
        return luigi.LocalTarget(os.path.join(os.path.dirname(__file__), os.path.basename(self.fastq1.replace(".fastq.gz", ".bam"))))

    def run(self):
        cl = [samtools, "view", "-bhS", self.input()[0].fn, ">", self.output().fn]
        out = shell.exec_cmd(" ".join(cl), shell=True)

class LuigiTaskRunSample(luigi.Task):
    sample = luigi.Parameter(default=None)
    indir = luigi.Parameter(default=os.curdir)
    outdir = luigi.Parameter(default=os.curdir)

    def requires(self):
        fastq1 = os.path.join(self.indir, self.sample + "_R1_001.fastq.gz")
        fastq2 = os.path.join(self.indir, self.sample + "_R2_001.fastq.gz")
        return [LuigiTaskSamToBam(fastq1, fastq2)]
    def output(self):
        return luigi.LocalTarget(os.path.join(self.outdir, self.sample + "_R1_001.bam"))
    def run(self):
        print "running final step"

class LuigiTestWrapper(unittest.TestCase):
    def test_ls(self):
        """Test ls function"""
        LuigiTaskLsWrapper().run()

    def test_requires(self):
        """Test dependence on ls"""
        LuigiTaskPrintWrapper().run()

    def test_map_fastq(self):
        """Test mapping fastq"""
        f1 = os.path.join(os.path.dirname(__file__), os.pardir, "data", "projects", "J.Doe_00_01", "P001_101_index3", "121015_BB002BBBXX", "P001_101_index3_TGACCA_L001_R1_001.fastq.gz")
        f2 = os.path.join(os.path.dirname(__file__), os.pardir, "data", "projects", "J.Doe_00_01", "P001_101_index3", "121015_BB002BBBXX", "P001_101_index3_TGACCA_L001_R2_001.fastq.gz")
        luigi.run(['--local-scheduler', '--fastq1', f1, '--fastq2', f2], main_task_cls=LuigiTaskSamToBam)

    def test_run_sample(self):
        """Test running a pipeline based on sample name, input directory and output directory"""
        indir = os.path.join(os.path.dirname(__file__), os.pardir, "data", "projects", "J.Doe_00_01", "P001_101_index3", "121015_BB002BBBXX")
        luigi.run(['--local-scheduler', '--sample', "P001_101_index3_TGACCA_L001", '--indir', indir], main_task_cls=LuigiTaskRunSample)
        #luigi.run(['--local-scheduler', '-h'], main_task_cls=LuigiTaskRunSample)








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
