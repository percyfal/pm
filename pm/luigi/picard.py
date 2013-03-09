import os
import luigi
import logging
import time
import pm.luigi.external
from pm.luigi.job import JobTask, DefaultShellJobRunner
from cement.utils import shell

JAVA="java"
JAVA_OPTS="-Xmx2g"
PICARD_HOME=os.getenv("PICARD_HOME")

logger = logging.getLogger('luigi-interface')

class PicardJobRunner(DefaultShellJobRunner):
    # TODO: make this configurable 
    path = PICARD_HOME

    def run_job(self, job):
        if not job.jar() or not os.path.exists(os.path.join(self.path,job.jar())):
            logger.error("Can't find jar: {0}, full path {1}".format(job.jar(),
                                                                     os.path.abspath(job.jar())))
            raise Exception("job jar does not exist")
        arglist = ['java', job.java_opt(), '-jar', os.path.join(self.path, job.jar())]
        if job.main():
            arglist.append(job.main())
        if job.opts():
            arglist.append(job.opts())
        (tmp_files, job_args) = DefaultShellJobRunner._fix_paths(job)

        arglist += job_args
        cmd = ' '.join(arglist)        
        logger.info(cmd)
        (stdout, stderr, returncode) = shell.exec_cmd(cmd.replace("= ", "="), shell=True)

        if returncode == 0:
            logger.info("Shell job completed")
            for a, b in tmp_files:
                logger.info("renaming {0} to {1}".format(a.path, b.path))
                a.move(b.path)
        else:
            raise Exception("Job '{}' failed: \n{}".format(cmd.replace("= ", "="), " ".join([stderr])))

class InputBamFile(JobTask):
    _config_section = "picard"
    _config_subsection = "input_bam_file"
    bam = luigi.Parameter(default=None)
    parent_task = luigi.Parameter(default="pm.luigi.external.BamFile")
    def requires(self):
        cls = self.set_parent_task()
        return cls(bam=self.bam)
    def output(self):
        return luigi.LocalTarget(os.path.abspath(self.input().fn))
    def run(self):
        pass

class PicardJobTask(JobTask):
    _config_section = "picard"
    java_options = "-Xmx2g"
    parent_task = luigi.Parameter(default="pm.luigi.picard.InputBamFile")

    def jar(self):
        """Path to the jar for this Picard job"""
        return None

    def java_opt(self):
        return self.java_options

    def exe(self):
        return self.jar()

    def job_runner(self):
        return PicardJobRunner()

    def requires(self):
        print "in requires"
        print "have bam file {}".format(self.bam)
        cls = self.set_parent_task()
        return cls(bam=self.bam)

class SortSam(PicardJobTask):
    _config_subsection = "sortsam"
    bam = luigi.Parameter(default=None)
    options = luigi.Parameter(default="SO=coordinate MAX_RECORDS_IN_RAM=750000")

    def jar(self):
        return "SortSam.jar"
    def output(self):
        return luigi.LocalTarget(os.path.abspath(self.input().fn).replace(".bam", ".sort.bam"))
    def args(self):
        return ["INPUT=", self.input(), "OUTPUT=", self.output()]

class AlignmentMetrics(PicardJobTask):
    _config_subsection = "alignment_metrics"
    bam = luigi.Parameter(default=None)
    options = luigi.Parameter(default=None)
    
    def jar(self):
        return "CollectAlignmentSummaryMetrics.jar"
    def output(self):
        return luigi.LocalTarget(os.path.abspath(self.input().fn).replace(".bam", ".align_metrics"))
    def args(self):
        return ["INPUT=", self.input(), "OUTPUT=", self.output()]

class InsertMetrics(PicardJobTask):
    _config_subsection = "insert_metrics"
    bam = luigi.Parameter(default=None)
    options = luigi.Parameter(default=None)
    
    def jar(self):
        return "CollectInsertSizeMetrics.jar"
    def output(self):
        return [luigi.LocalTarget(os.path.abspath(self.input().fn).replace(".bam", ".insert_metrics")), 
                luigi.LocalTarget(os.path.abspath(self.input().fn).replace(".bam", ".insert_hist"))]
    def args(self):
        return ["INPUT=", self.input(), "OUTPUT=", self.output()[0], "HISTOGRAM_FILE=", self.output()[1]]

class DuplicationMetrics(PicardJobTask):
    _config_subsection = "duplication_metrics"
    bam = luigi.Parameter(default=None)
    options = luigi.Parameter(default=None)

    def jar(self):
        return "MarkDuplicates.jar"
    def output(self):
        return [luigi.LocalTarget(os.path.abspath(self.bam).replace(".bam", ".dup.bam")), 
                luigi.LocalTarget(os.path.abspath(self.bam).replace(".bam", ".dup_metrics"))]
    def args(self):
        return ["INPUT=", self.input(), "OUTPUT=", self.output()[0], "METRICS_FILE=", self.output()[1]]

class HsMetrics(PicardJobTask):
    _config_subsection = "hs_metrics"
    bam = luigi.Parameter(default=None)
    options = luigi.Parameter(default=None)
    baits = luigi.Parameter(default=None)
    targets = luigi.Parameter(default=None)
    
    def jar(self):
        return "CalculateHsMetrics.jar"
    def output(self):
        return luigi.LocalTarget(os.path.abspath(self.input().fn).replace(".bam", ".hs_metrics"))
    def args(self):
        return ["INPUT=", self.input(), "OUTPUT=", self.output(), "BAIT_INTERVALS=", self.baits, "TARGET_INTERVALS=", self.targets]

class PicardMetrics(luigi.WrapperTask):
    bam = luigi.Parameter(default=None)
    def requires(self):
        return [DuplicationMetrics(bam=self.bam), HsMetrics(bam=self.bam),
                InsertMetrics(bam=self.bam), AlignmentMetrics(bam=self.bam)]
