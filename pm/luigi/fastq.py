import os
import luigi
import pm.luigi.external

class FastqFileLink(luigi.Task):
    fastq = luigi.Parameter(default=None)
    outdir = luigi.Parameter(default=os.curdir)
    indir = luigi.Parameter(default=os.curdir, is_global=True)

    def requires(self):
        #return pm.luigi.external.FastqFile(fastq=self.fastq)
        return pm.luigi.external.FastqFile(fastq=os.path.join(self.indir, os.path.basename(self.fastq)))

    def output(self):
        return luigi.LocalTarget(os.path.join(self.outdir, os.path.basename(self.fastq)))

    def run(self):
        os.symlink(self.input().fn, self.output().fn)
        
