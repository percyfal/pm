import os
import luigi
import time
import shutil
import pm.luigi
from pm.luigi.fastq import FastqFileLink
from cement.utils import shell

# These should be configurable
BWA="bwa"
NUM_THREADS=1

class BwaJobTask(object):
    """Main bwa class with parameters necessary for all bwa classes"""
    bwaref = luigi.Parameter(default=None)
    num_threads = luigi.Parameter(default=NUM_THREADS)

    def exe(self):
        """Executable of this task"""
        return BWA

    def main(self):
        """compulsory main method for bwa"""
        return None
    
class BwaAln(pm.luigi.Task, BwaJobTask):
    fastq = luigi.Parameter(default=None)

    def main(self):
        return "aln"
    
    def requires(self):
        return [FastqFileLink(self.fastq)]
    
    def output(self):
        return luigi.LocalTarget(self.input()[0].fn.replace(".gz", "").replace(".fastq", ".sai"))

    def run(self):
        args = ['-t', str(self.num_threads), self.bwaref, self.input()[0], ">", self.output()]
        self.run_job(args)


class BwaSampe(pm.luigi.Task, BwaJobTask):
    sai1 = luigi.Parameter(default=None)
    sai2 = luigi.Parameter(default=None)
    read_suffix = luigi.Parameter(default="_R1_001")

    def main(self):
        return "sampe"
    
    def requires(self):
        return [BwaAln(fastq=self.sai1.replace(".sai", ".fastq.gz"), bwaref=self.bwaref),
                BwaAln(fastq=self.sai2.replace(".sai", ".fastq.gz"), bwaref=self.bwaref)]

    def output(self):
        return luigi.LocalTarget(os.path.abspath(self.sai1).replace(self.read_suffix, "").replace(".sai", ".sam"))

    def run(self):
        sai1 = self.input()[0]
        sai2 = self.input()[1]
        fastq1 = luigi.LocalTarget(sai1.fn.replace(".sai", ".fastq.gz"))
        fastq2 = luigi.LocalTarget(sai2.fn.replace(".sai", ".fastq.gz"))
        args = [self.bwaref, sai1, sai2, fastq1, fastq2, ">", self.output()]
        self.run_job(args)
