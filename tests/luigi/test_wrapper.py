import os
import glob
import sys
import unittest
import luigi
import time
import logging
import pm.luigi.bwa as BWA
import pm.luigi.samtools as SAM
import pm.luigi.fastq as FASTQ
import pm.luigi.picard as PICARD
import pm.luigi.gatk as GATK
import pm.luigi.external
import ngstestdata as ntd

logger = logging.getLogger('luigi-interface')

bwa = "bwa"
bwaref = os.path.join(ntd.__path__[0], os.pardir, "data", "genomes", "Hsapiens", "hg19", "bwa", "chr11.fa")
bwaseqref = os.path.join(ntd.__path__[0], os.pardir, "data", "genomes", "Hsapiens", "hg19", "seq", "chr11.fa")
samtools = "samtools"
indir = os.path.join(os.path.dirname(__file__), os.pardir, "data", "projects", "J.Doe_00_01", "P001_101_index3", "121015_BB002BBBXX")
projectdir = os.path.join(os.path.dirname(__file__), os.pardir, "data", "projects", "J.Doe_00_01")
sample = "P001_101_index3_TGACCA_L001"
fastq1 = os.path.join(indir, sample + "_R1_001.fastq.gz")
fastq2 = os.path.join(indir, sample + "_R2_001.fastq.gz")
sai1 = os.path.join(sample + "_R1_001.sai")
sai2 = os.path.join(sample + "_R2_001.sai")
sam = os.path.join(sample + ".sam")
bam = os.path.join(sample + ".bam")
sortbam = os.path.join(sample + ".sort.bam")

local_scheduler = '--local-scheduler'
process = os.popen("ps x -o pid,args | grep luigid | grep -v grep").read() #sometimes have to use grep -v grep
if process:
   local_scheduler = None

def _luigi_args(args):
    if local_scheduler:
        return [local_scheduler] + args
    return args

class TestLuigiWrappers(unittest.TestCase):
    # @classmethod
    # def tearDownClass(cls):
    #     for f in [sai1, sai2, sam, bam, sortbam]:
    #         if os.path.exists(f):
    #             os.unlink(f)

    def test_luigihelp(self):
        luigi.run(['-h'], main_task_cls=FASTQ.FastqFileLink)

    def test_fastqln(self):
        luigi.run(_luigi_args(['--fastq', fastq1]), main_task_cls=FASTQ.FastqFileLink)

    def test_bwaaln(self):
        luigi.run(_luigi_args(['--fastq', fastq1, '--indir', indir]), main_task_cls=BWA.BwaAln)
        luigi.run(_luigi_args(['--fastq', fastq2, '--indir', indir]), main_task_cls=BWA.BwaAln)

    def test_bwasampe(self):
        if os.path.exists(sam):
            os.unlink(sam)
        luigi.run(_luigi_args(['--sai1', sai1, '--sai2', sai2, '--indir', indir]), main_task_cls=BWA.BwaSampe)

    def test_samtobam(self):
        luigi.run(_luigi_args(['--sam', sam, '--indir', indir, '--parent-task', 'pm.luigi.bwa.BwaSampe']), main_task_cls=SAM.SamToBam)

    def test_sortbam(self):
        luigi.run(_luigi_args(['--bam', bam, '--indir', indir]), main_task_cls=SAM.SortBam)

    def test_picard_sortbam(self):
        luigi.run(_luigi_args(['--bam', bam, '--indir', indir]), main_task_cls=PICARD.SortSam)

    def test_picard_alignmentmetrics(self):
        luigi.run(_luigi_args(['--bam', bam,'--options', 'REFERENCE_SEQUENCE={}'.format(bwaseqref)]), main_task_cls=PICARD.AlignmentMetrics)

    def test_picard_insertmetrics(self):
        luigi.run(_luigi_args(['--bam', bam,'--options', 'REFERENCE_SEQUENCE={}'.format(bwaseqref)]), main_task_cls=PICARD.InsertMetrics)

    def test_picard_dupmetrics(self):
        if os.path.exists(sortbam.replace(".bam", ".dup_metrics")):
            os.unlink(sortbam.replace(".bam", ".dup_metrics"))
        luigi.run(_luigi_args(['--bam', sortbam]), main_task_cls=PICARD.DuplicationMetrics)

    def test_picard_dupmetrics_altconfig(self):
        if os.path.exists(sortbam.replace(".bam", ".dup_metrics")):
            os.unlink(sortbam.replace(".bam", ".dup_metrics"))
        luigi.run(_luigi_args(['--bam', sortbam, '--config', os.path.join(os.getenv("HOME"), ".pm2", "jobconfig2.yaml")]), main_task_cls=PICARD.DuplicationMetrics)

    def test_gatk_ug(self):
        if os.path.exists(sortbam.replace(".bam", ".dup_metrics")):
            os.unlink(sortbam.replace(".bam", ".dup_metrics"))
        luigi.run(_luigi_args(['--bam', sortbam]), main_task_cls=GATK.UnifiedGenotyper)

    def test_picard_metrics(self):
        luigi.run(_luigi_args(['--bam', bam, '--config', 'pipeconf.yaml']), main_task_cls=PICARD.PicardMetrics)
        
class TestLuigiParallel(unittest.TestCase):
    def test_bwa_samples(self):
        pass

    def test_sample_list(self):
        class BwaAlnSamples(BWA.BwaJobTask):
            samples = luigi.Parameter(default=[], is_list=True)

            def main(self):
                return "aln"

            def requires(self):
                indir = FASTQ.FastqFileLink().indir
                fastq = []
                for s in self.samples:
                    print "setting up requirements for sample {}".format(s)
                    if not os.path.exists(os.path.join(indir, s)):
                        print("No such sample {0} found in input directory {1}; skipping".format(s, indir))
                        continue
                    for fc in os.listdir(os.path.join(indir, s)):
                        fcdir = os.path.join(indir, s, fc)
                        if not os.path.isdir(fcdir):
                            print("{0} not a directory; skipping".format(fcdir))
                            continue
                        glob_str = os.path.join(fcdir, "{}*.fastq.gz".format(s))
                        print("looking in flowcell directory {} with glob {}".format(fcdir, glob_str))
                        fastqfiles = glob.glob(glob_str)
                        logging.info("found fastq files {}".format(fastqfiles))
                        fastq += fastqfiles
                print ("Found {} fastq files".format(len(fastq)))
                #print ("Found {}".format(self.fastq))

                return [FASTQ.FastqFileLink(x) for x in fastq]

            def args(self):
                return []

            def run(self):
                print "Found {} fastq files".format(len(self.input()))

                
            def output(self):
                return luigi.LocalTarget("tabort.txt")
        luigi.run(_luigi_args(['--samples', "P001_101_index3", '--indir', projectdir]), main_task_cls=BwaAlnSamples)
        

class SampeToSamtools(SAM.SamToBam):
    def requires(self):
        return BWA.BwaSampe(sai1=os.path.join(self.sam.replace(".sam", BWA.BwaSampe().read1_suffix + ".sai")),
                            sai2=os.path.join(self.sam.replace(".sam", BWA.BwaSampe().read2_suffix + ".sai")))

# class BwaToPicard(PICARD.BamFile):
#     def requires(self):
#         return BWA.BwaSampe(sai1=os.path.join(self.sam.replace(".sam", BWA.BwaSampe().read1_suffix + ".sai")),
#                             sai2=os.path.join(self.sam.replace(".sam", BWA.BwaSampe().read2_suffix + ".sai")))
        
#     parent_task = "pm.luigi.bwa.Sampe"

class TestLuigiPipelines(unittest.TestCase):
    def test_sampe_to_samtools(self):
        luigi.run(_luigi_args(['--sam', sam, '--indir', indir]), main_task_cls=SampeToSamtools)

    def test_sampe_to_samtools_sort(self):
        luigi.run(_luigi_args(['--bam', bam, '--indir', indir, '--config-file', 'pipeconf.yaml']), main_task_cls=SAM.SortBam)

    def test_sampe_to_picard_sort(self):
        luigi.run(_luigi_args(['--bam', bam, '--indir', indir, '--config-file', 'pipeconf.yaml']), main_task_cls=PICARD.SortSam)
