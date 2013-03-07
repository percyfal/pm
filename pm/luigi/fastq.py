import luigi

class ExternalFastqFile(luigi.ExternalTask):
    fastq = luigi.Parameter(default=None)

    def output(self):
        return luigi.LocalTarget(self.fastq)

    
