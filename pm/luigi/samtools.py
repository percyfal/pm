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
        
    def requires(self):
        print self.sam_cls
        if self.sam_cls == "BwaSampe":
            fastq1 = os.path.join(BwaSampe().outpath, self.sam.replace(".sam", BwaSampe().read_suffix + ".fastq.gz"))
            fastq2 = os.path.join(BwaSampe().outpath, self.sam.replace(".sam", BwaSampe().read_suffix + ".fastq.gz").replace("_R1_", "_R2_"))
            return [BwaSampe(fastq1=fastq1, fastq2=fastq1)]
        else:
            pass

    def output(self):
        #print "in output: " + str(self.sam)
        return luigi.LocalTarget("tabort.txt")
        
#return luigi.LocalTarget(self.sam.replace(".sam", ".bam"))

    def run(self):
        print "running on {}".format(self.sam)
