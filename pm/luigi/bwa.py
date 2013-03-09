import os
import luigi
import time
import shutil
from pm.luigi.fastq import FastqFileLink
from pm.luigi.job import JobTask, DefaultShellJobRunner
from cement.utils import shell

class BwaJobRunner(DefaultShellJobRunner):
    pass

class BwaJobTask(JobTask):
    """Main bwa class with parameters necessary for all bwa classes"""
    _config_section = "bwa"
    bwa = luigi.Parameter(default="bwa")
    bwaref = luigi.Parameter(default=None)
    num_threads = luigi.Parameter(default=1)

    def exe(self):
        """Executable of this task"""
        return self.bwa

    def job_runner(self):
        return BwaJobRunner()

class BwaAln(BwaJobTask):
    _config_subsection = "aln"
    fastq = luigi.Parameter(default=None)
    options = luigi.Parameter(default=None)

    def main(self):
        return "aln"
    
    def opts(self):
        if self.options:
            return '-t {} {}'.format(str(self.num_threads), self.options)            
        else:
            return '-t {}'.format(str(self.num_threads))

    def requires(self):
        return [FastqFileLink(self.fastq)]
    
    def output(self):
        return luigi.LocalTarget(self.input()[0].fn.replace(".gz", "").replace(".fastq", ".sai"))

    def args(self):
        return [self.bwaref, self.input()[0], ">", self.output()]

class BwaSampe(BwaJobTask):
    _config_subsection = "sampe"
    sai1 = luigi.Parameter(default=None)
    sai2 = luigi.Parameter(default=None)
    # Get these with static methods
    read1_suffix = luigi.Parameter(default="_R1_001")
    read2_suffix = luigi.Parameter(default="_R2_001")
    read_group = luigi.Parameter(default=None)

    def main(self):
        return "sampe"

    def requires(self):
        return [BwaAln(fastq=self.sai1.replace(".sai", ".fastq.gz")),
                BwaAln(fastq=self.sai2.replace(".sai", ".fastq.gz"))]

    def output(self):
        return luigi.LocalTarget(os.path.abspath(self.sai1).replace(self.read1_suffix, "").replace(".sai", ".sam"))

    def args(self):
        sai1 = self.input()[0]
        sai2 = self.input()[1]
        fastq1 = luigi.LocalTarget(sai1.fn.replace(".sai", ".fastq.gz"))
        fastq2 = luigi.LocalTarget(sai2.fn.replace(".sai", ".fastq.gz"))
        if not self.read_group:
            foo = sai1.fn.replace(".sai", "")
            self.read_group = "-r \"{}\"".format("\t".join(["@RG", "ID:{}".format(foo), "SM:{}".format(foo)]))
        return [self.read_group, self.bwaref, sai1, sai2, fastq1, fastq2, ">", self.output()]

