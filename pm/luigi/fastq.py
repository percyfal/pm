import os
import luigi

class FastqFileLink(luigi.Task):
    fastq = luigi.Parameter(default=None)
    outdir = luigi.Parameter(default=os.curdir)
    indir = luigi.Parameter(default=os.curdir, is_global=True)

    def requires(self):
        return [ExternalFastqFile(fastq=os.path.join(self.indir, os.path.basename(self.fastq)))]

    def output(self):
        return luigi.LocalTarget(os.path.join(self.outdir, os.path.basename(self.fastq)))

    def run(self):
        os.symlink(self.input()[0].fn, self.output().fn)
        
class ExternalFastqFile(luigi.ExternalTask):
    fastq = luigi.Parameter(default=None)

    def output(self):
        return luigi.LocalTarget(self.fastq)
