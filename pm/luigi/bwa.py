import os
import luigi
import time
from pm.luigi.fastq import ExternalFastqFile
from cement.utils import shell

# These should be configurable
BWA="bwa"
OUTPATH=os.curdir
NUM_THREADS=1

class Bwa(object):
    """Main bwa class with parameters necessary for all bwa classes"""
    bwaref = luigi.Parameter(default=None)
    num_threads = luigi.Parameter(default=NUM_THREADS)
    outpath = luigi.Parameter(default=OUTPATH)
    exe = BWA
    
class BwaAln(luigi.Task, Bwa):
    fastq = luigi.Parameter(default=None)

    def requires(self):
        return [ExternalFastqFile(self.fastq)]
    
    def output(self):
        return luigi.LocalTarget(os.path.join(self.outpath, os.path.basename(self.fastq).replace(".gz", "").replace(".fastq", ".sai")))

    def run(self):
        cl = [self.exe, 'aln', '-t', str(self.num_threads), self.bwaref, self.input()[0].fn, ">", self.output().fn]
        out = shell.exec_cmd(" ".join(cl), shell=True)

class BwaSampe(luigi.Task, Bwa):
    fastq1 = luigi.Parameter(default=None)
    fastq2 = luigi.Parameter(default=None)
    read_suffix = luigi.Parameter(default="_R1_001")

    def requires(self):
        return [BwaAln(fastq=self.fastq1, bwaref=self.bwaref), BwaAln(fastq=self.fastq2, bwaref=self.bwaref)]

    def output(self):
        return luigi.LocalTarget(os.path.join(self.outpath, os.path.basename(self.fastq1).replace(self.read_suffix, "").replace(".fastq.gz", ".sam")))
    def run(self):
        sai1 = self.input()[0]
        sai2 = self.input()[1]
        cl = [self.exe, "sampe", self.bwaref, sai1.fn, sai2.fn, self.fastq1, self.fastq2, ">", self.output().fn]
        out = shell.exec_cmd(" ".join(cl), shell=True)
