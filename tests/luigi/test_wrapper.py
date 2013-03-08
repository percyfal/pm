import os
import unittest
import luigi
import time
import pm.luigi.bwa as BWA
import pm.luigi.samtools as SAM
import pm.luigi.fastq as FASTQ
import pm.luigi.picard as PICARD
import pm.luigi.gatk as GATK
import ngstestdata as ntd

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
sortbam = os.path.join(sample + ".sort.bam")

class TestLuigiWrappers(unittest.TestCase):
    # @classmethod
    # def tearDownClass(cls):
    #     for f in [sai1, sai2, sam, bam, sortbam]:
    #         if os.path.exists(f):
    #             os.unlink(f)

    def test_luigihelp(self):
        luigi.run(['-h'], main_task_cls=FASTQ.FastqFileLink)

    def test_fastqln(self):
        luigi.run(['--local-scheduler', '--fastq', fastq1], main_task_cls=FASTQ.FastqFileLink)

    def test_bwaaln(self):
        luigi.run(['--local-scheduler', '--fastq', fastq1, '--indir', indir], main_task_cls=BWA.BwaAln)
        luigi.run(['--local-scheduler', '--fastq', fastq2, '--indir', indir], main_task_cls=BWA.BwaAln)

    def test_bwasampe(self):
        if os.path.exists(sam):
            os.unlink(sam)
        luigi.run(['--local-scheduler', '--sai1', sai1, '--sai2', sai2, '--indir', indir, '--bwaref', bwaref], main_task_cls=BWA.BwaSampe)

    def test_samtobam(self):
        luigi.run(['--local-scheduler', '--sam', sam, '--indir', indir, '--require-cls', 'pm.luigi.bwa.BwaSampe'], main_task_cls=SAM.SamToBam)

    def test_sortbam(self):
        luigi.run(['--local-scheduler', '--bam', bam, '--indir', indir], main_task_cls=SAM.SortBam)

    def test_picard_sortbam(self):
        luigi.run(['--local-scheduler', '--bam', bam, '--indir', indir], main_task_cls=PICARD.SortSam)

    def test_picard_alignmentmetrics(self):
        luigi.run(['--local-scheduler', '--bam', bam,'--options', 'REFERENCE_SEQUENCE={}'.format(bwaseqref)], main_task_cls=PICARD.AlignmentMetrics)

    def test_picard_insertmetrics(self):
        luigi.run(['--local-scheduler', '--bam', bam,'--options', 'REFERENCE_SEQUENCE={}'.format(bwaseqref)], main_task_cls=PICARD.InsertMetrics)

    def test_picard_dupmetrics(self):
        if os.path.exists(sortbam.replace(".bam", ".dup_metrics")):
            os.unlink(sortbam.replace(".bam", ".dup_metrics"))
        luigi.run(['--local-scheduler', '--bam', sortbam], main_task_cls=PICARD.DuplicationMetrics)

    def test_picard_dupmetrics_nolocal(self):
        if os.path.exists(sortbam.replace(".bam", ".dup_metrics")):
            os.unlink(sortbam.replace(".bam", ".dup_metrics"))
        luigi.run(['--bam', sortbam], main_task_cls=PICARD.DuplicationMetrics)

    def test_picard_dupmetrics_altconfig(self):
        if os.path.exists(sortbam.replace(".bam", ".dup_metrics")):
            os.unlink(sortbam.replace(".bam", ".dup_metrics"))
        luigi.run(['--local-scheduler', '--bam', sortbam, '--config', os.path.join(os.getenv("HOME"), ".pm2", "jobconfig2.yaml")], main_task_cls=PICARD.DuplicationMetrics)

    def test_gatk_ug(self):
        if os.path.exists(sortbam.replace(".bam", ".dup_metrics")):
            os.unlink(sortbam.replace(".bam", ".dup_metrics"))
        luigi.run(['--local-scheduler', '--bam', sortbam], main_task_cls=GATK.UnifiedGenotyper)
