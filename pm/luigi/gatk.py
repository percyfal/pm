import os
import luigi
import logging
import pm.luigi.external
from pm.luigi.job import JobTask, DefaultShellJobRunner
from cement.utils import shell

logger = logging.getLogger('luigi-interface')

JAVA="java"
JAVA_OPTS="-Xmx2g"
GATK_HOME=os.getenv("GATK_HOME")
GATK_JAR="GenomeAnalysisTK.jar"

class GATKJobRunner(DefaultShellJobRunner):
    # How configure this best way?
    path = GATK_HOME

    @staticmethod
    def _get_main(job):
        return "-T {}".format(job.main())

    def run_job(self, job):
        if not job.jar() or not os.path.exists(os.path.join(self.path,job.jar())):
            logger.error("Can't find jar: {0}, full path {1}".format(job.jar(),
                                                                     os.path.abspath(job.jar())))
            raise Exception("job jar does not exist")
        arglist = ['java', job.java_opt(), '-jar', os.path.join(self.path, job.jar())]
        if job.main():
            arglist.append(self._get_main(job))
        if job.opts():
            arglist.append(job.opts())
        (tmp_files, job_args) = DefaultShellJobRunner._fix_paths(job)

        arglist += job_args
        cmd = ' '.join(arglist)        
        logger.info(cmd)
        (stdout, stderr, returncode) = shell.exec_cmd(cmd, shell=True)

        if returncode == 0:
            logger.info("Shell job completed")
            for a, b in tmp_files:
                logger.info("renaming {0} to {1}".format(a.path, b.path))
                a.move(b.path)
        else:
            raise Exception("Job '{}' failed: \n{}".format(cmd, " ".join([stderr])))

class GATKJobTask(JobTask):
    _config_section = "gatk"
    gatk = luigi.Parameter(default=GATK_JAR)
    bam = luigi.Parameter(default=None)
    java_options = luigi.Parameter(default="-Xmx2g")
    parent_task = luigi.Parameter(default="pm.luigi.external.BamFile")
    ref = luigi.Parameter(default=None)
    # Additional commonly used options
    target_region = luigi.Parameter(default=None)

    def jar(self):
        return self.gatk

    def exe(self):
        return self.jar()

    def java_opt(self):
        return self.java_options

    def job_runner(self):
        return GATKJobRunner()

    def requires(self):
        if self.parent_task == "pm.luigi.external.BamFile":
            return [pm.luigi.external.BamFile(bam=self.bam), pm.luigi.samtools.IndexBam(bam=self.bam)]
        else:
            logging.warn("No such class {}; using default: {}".format(self.parent_task, self.get_param_default("parent_task")))
            return pm.luigi.external.BamFile(bam=self.bam)

class Realignment(GATKJobTask):
    _config_subsection = "RealignerTargetCreator"
    bam = luigi.Parameter(default=None)
    options = luigi.Parameter(default=None)
    
    def opts(self):
        retval = self.options if self.options else ""
        if not self.ref:
            raise Exception("need reference for Realignment")
        retval += " -R {}".format(self.ref)
        if self.target_region:
            retval += "-L {}".format(self.target_region)
        return retval
    
    def main(self):
        return "RealignerTargetCreator"

class IndelRealigener(GATKJobTask):
    _config_subsection = "IndelRealigner"
    


class UnifiedGenotyper(GATKJobTask):
    _config_subsection = "unifiedgenotyper"
    bam = luigi.Parameter(default=None)
    options = luigi.Parameter(default="-stand_call_conf 30.0 -stand_emit_conf 10.0  --downsample_to_coverage 30 --output_mode EMIT_VARIANTS_ONLY -glm BOTH")

    def opts(self):
        retval = self.options if self.options else ""
        if not self.ref:
            raise Exception("need reference for UnifiedGenotyper")
        retval += " -R {}".format(self.ref)
        if self.target_region:
            retval += "-L {}".format(self.target_region)
        return retval

    def main(self):
        return "UnifiedGenotyper"

    def output(self):
        return luigi.LocalTarget(os.path.abspath(self.input()[0].fn).replace(".bam", ".vcf"))
    #pm.luigi.vcf.IndexVcf(vcf=os.path.abspath(self.input()[0].fn).replace(".bam", ".vcf"))]

    def args(self):
        return ["-I", self.input()[0], "-o", self.output()]

