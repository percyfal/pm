import os
import luigi
import logging
import pm.luigi.external
from pm.luigi.job import JobTask

logger = logging.getLogger('luigi-interface')

class FastqFileLink(JobTask):
    _config_section = "fastq"
    _config_subsection = "link"
    fastq = luigi.Parameter(default=None)
    outdir = luigi.Parameter(default=os.curdir)
    # This is tricky: it is easy enough to make links based on
    # absolute file names. The problem is that the information about
    # the original path is lost in successive tasks, so that a task
    # that takes as input a bam file in the current directory will not
    # know where the link came from; hence, we need an indir parameter
    # for downstream tasks.
    indir = luigi.Parameter(default=os.curdir)
    parent_task = luigi.Parameter(default="pm.luigi.external.FastqFile")

    def requires(self):
        cls = self.set_parent_task()
        return cls(fastq=os.path.abspath(self.fastq))

    def output(self):
        return luigi.LocalTarget(os.path.join(os.path.abspath(self.outdir), os.path.basename(self.fastq)))

    def run(self):
        if not os.path.exists(self.outdir):
            os.makedirs(self.outdir)
        os.symlink(self.input().fn, self.output().fn)
        
