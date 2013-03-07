import os
import luigi
from pm.luigi.bwa import BwaSampe
from cement.utils import shell

SAMTOOLS="samtools"

class Samtools(object):
    exe = SAMTOOLS

class SamToBam(luigi.Task, Samtools):
    sam = luigi.Parameter(default=None)
    sam_cls = luigi.Parameter(default="BwaSampe")
    opt = luigi.Parameter(default="-bSh")
    my_cls = "test"

    def requires(self):
        # Sam file can come from different Tasks - how cope in best way?
        # Probably by using external task and separating 
        print "In requires: " + self.my_cls + "\n\n"
        if self.sam_cls == "BwaSampe":
            sai1 = os.path.join(self.sam.replace(".sam", BwaSampe().read_suffix + ".sai"))
            sai2 = os.path.join(self.sam.replace(".sam", BwaSampe().read_suffix + ".sai").replace("_R1_", "_R2_"))
            return [BwaSampe(sai1=sai1, sai2=sai2)]
        else:
            print "No such class " + self.sam_cls
            pass

    def output(self):
        return luigi.LocalTarget(self.sam.replace(".sam", ".bam"))

    def run(self):
        cl = [self.exe, "view", self.opt, self.sam, "-o", self.sam.replace(".sam", ".bam")]
        (stdout, stderr, returncode) = shell.exec_cmd(" ".join(cl), shell=True)
        if returncode == 1:
            os.unlink(self.output().fn)

class SortBam(luigi.Task, Samtools):
    bam = luigi.Parameter(default=None)
    opt = luigi.Parameter(default="")

    def requires(self):
        return [SamToBam(sam=self.bam.replace(".bam", ".sam"))]

    def output(self):
        return luigi.LocalTarget(self.bam.replace(".bam", ".sort.bam"))

    def run(self):
        cl = [self.exe, "sort", self.opt, self.bam, self.bam.replace(".bam", ".sort")]
        out = shell.exec_cmd(" ".join(cl), shell=True)
