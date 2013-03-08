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

class PicardJobTask(JobTask):
    _config_section = "picard"
    java_options = "-Xmx2g"
    # would want to use class definitions, not strings
    #require_cls = luigi.Parameter(default=ExternalBamFile)
    # Basically want to do introspection; see
    # http://www.blog.pythonlibrary.org/2012/07/31/advanced-python-how-to-dynamically-load-modules-or-classes/
    # Actually this is a problem with luigi.Parameter: in the config
    # file this is a string: how instantiate a class?
    require_cls = luigi.Parameter(default="pm.luigi.external.BamFile")

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
        """Enumerate all types of cases here; ExternalBamFile,
        pm.luigi.bwa.BwaSampe, pm.luigi.samtools.SamToBam..."""
        if self.require_cls == "pm.luigi.external.BamFile":
            return pm.luigi.external.BamFile(bam=self.bam)
        else:
            raise ValueError("No such class '{}'".format(self.require_cls))
    

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
    def requires(self):
        return ExternalBamFile(bam=self.bam)
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
    def requires(self):
        return ExternalBamFile(bam=self.bam)
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
    def requires(self):
        return SortSam(bam=self.bam.replace(".sort", ""))
    def output(self):
        return [luigi.LocalTarget(os.path.abspath(self.input().fn).replace(".bam", ".dup.bam")), 
                luigi.LocalTarget(os.path.abspath(self.input().fn).replace(".bam", ".dup_metrics"))]
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
    def requires(self):
        return ExternalBamFile(bam=self.bam)
    def output(self):
        return luigi.LocalTarget(os.path.abspath(self.input().fn).replace(".bam", ".hs_metrics"))
    def args(self):
        return ["INPUT=", self.input(), "OUTPUT=", self.output(), "BAIT_INTERVALS_FILE=", self.baits, "TARGET_INTERVALS=", self.targets]
