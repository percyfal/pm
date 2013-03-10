import luigi
import os
import glob
from pm.luigi.job import JobTask
from pm.luigi.picard import PicardMetrics
from pm.luigi.fastq import FastqFileLink

class AlignSeqcap(luigi.WrapperTask):
    sample = luigi.Parameter(default=[], is_list=True)
    flowcell = luigi.Parameter(default=[], is_list=True)
    project = luigi.Parameter()
    indir = luigi.Parameter()

    # NB: ok, problem: we need to know what the target names will look
    # like. would like to work with more generic feature, e.g. sample
    # name
    def requires(self):
        fastq_list, bam_list = self.set_bam_files()
        return [FastqFileLink(fastq=x[0], outdir=x[1]) for x in fastq_list] + [PicardMetrics(bam=y) for y in bam_list]

    def run(self):
        print "Analysing files {}".format(self.input())

    def set_bam_files(self):
        """Function for collecting samples and generating *target* file names"""
        project_indir = os.path.join(self.indir, self.project)
        if not os.path.exists(project_indir):
            return []
        fastq_list = []
        samples = os.listdir(project_indir)
        for s in samples:
            flowcells = os.listdir(os.path.join(project_indir, s))
            for fc in flowcells:
                fastq_files = glob.glob(os.path.join(project_indir, s, fc, "{}*.fastq.gz".format(s)))
                fastq_list.extend([(x, os.path.join(os.curdir, s, fc)) for x in fastq_files])
        bam_list = []
        for i in range(0, len(fastq_list), 2):
            bam_list.append(os.path.join(fastq_list[i][1], os.path.basename(fastq_list[i][0]).replace(".fastq.gz", ".sort.dup.bam").replace("_R1_001", "")))
        return fastq_list, bam_list

if __name__ == "__main__":
    luigi.run(main_task_cls=AlignSeqcap)
