import os
import luigi
from cement.utils import shell

JAVA="java"
JAVA_OPTS="-Xmx2g"
PICARD_HOME=os.getenv("PICARD_HOME")


class SortSam(luigi.Task):
    bam = luigi.Parameter(default=None)
    opt = "SO=coordinate"

    def requires(self):
        pass
