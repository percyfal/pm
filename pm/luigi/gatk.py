import os
import luigi
from cement.utils import shell

JAVA="java"
JAVA_OPTS="-Xmx2g"
GATK_HOME=os.getenv("GATK_HOME")
GATK_JAR="GenomeAnalysisTK.jar"

class GATK(object):
    exe = "{} {} {}".format(JAVA, JAVA_OPTS, os.path.join(GATK_HOME, GATK_JAR))

