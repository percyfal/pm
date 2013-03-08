import os
import luigi
import logging
import pm.luigi.external
import pm.luigi.bwa
from pm.luigi.job import JobTask, DefaultShellJobRunner

logger = logging.getLogger('luigi-interface')

class SamtoolsJobRunner(DefaultShellJobRunner):
    pass

class SamtoolsJobTask(JobTask):
    """Main samtools job task"""
    _config_section = "samtools"
    sam = luigi.Parameter(default=None)
    bam = luigi.Parameter(default=None)
    samtools = luigi.Parameter(default="samtools")
    require_cls = luigi.Parameter(default="pm.luigi.external.SamFile")

    def exe(self):
        """Executable"""
        return self.samtools

    def job_runner(self):
        return SamtoolsJobRunner()

    def requires(self):
        if (self.require_cls == "pm.luigi.bwa.BwaSampe"):
            return pm.luigi.bwa.BwaSampe(sai1=os.path.join(self.sam.replace(".sam", pm.luigi.bwa.BwaSampe().read1_suffix + ".sai")),
                            sai2=os.path.join(self.sam.replace(".sam", pm.luigi.bwa.BwaSampe().read2_suffix + ".sai")))
        elif (self.require_cls == "pm.luigi.external.BamFile"):
            return pm.luigi.external.BamFile(bam=self.bam)
        elif (self.require_cls == "pm.luigi.external.SamFile"):
            return pm.luigi.external.SamFile(sam=self.sam)
        else:
            logging.warn("No such class {}; using default: {}".format(self.require_cls, self.get_param_default("require_cls")))
            return pm.luigi.external.SamFile(sam=self.sam)

class SamToBam(SamtoolsJobTask):
    _config_subsection = "samtobam"
    options = luigi.Parameter(default="-bSh")
    require_cls = luigi.Parameter(default="pm.luigi.external.SamFile")

    def main(self):
        return "view"

    def output(self):
        return luigi.LocalTarget(os.path.abspath(self.sam).replace(".sam", ".bam"))

    def args(self):
        return [self.sam, ">", self.output()]

class SortBam(SamtoolsJobTask):
    _config_subsection = "sortbam"
    bam = luigi.Parameter(default=None)
    options = luigi.Parameter(default=None)

    def requires(self):
        return [SamToBam(sam=self.bam.replace(".bam", ".sam"))]

    def output(self):
        return luigi.LocalTarget(os.path.abspath(self.bam).replace(".bam", ".sort.bam"))

    def main(self):
        return "sort"

    def add_suffix(self):
        return ".bam"

    def args(self):
        output_prefix = luigi.LocalTarget(self.output().fn.replace(".bam", ""))
        return [self.bam, output_prefix]

class IndexBam(SamtoolsJobTask):
    _config_subsection = "indexbam"
    bam = luigi.Parameter(default=None)
    options = luigi.Parameter(default=None)

    def requires(self):
        return pm.luigi.external.BamFile(bam=self.bam)

    def output(self):
        return luigi.LocalTarget(os.path.abspath(self.bam).replace(".bam", ".bam.bai"))

    def main(self):
        return "index"

    def args(self):
        return [self.bam, self.output()]
