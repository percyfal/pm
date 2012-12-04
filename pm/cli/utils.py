"""Pm2 utils controller module"""
import os
import yaml
import pandas as pd
from os.path import join as pjoin
from cement.core import controller, backend, hook
from pm.cli.controller import PmAbstractBaseController
from pm.lib.utils import update, config_to_dict
from pm.experiment import setup_project

LOG = backend.minimal_logger(__name__)

class UtilsController(PmAbstractBaseController):
    """
    pm2 utilities
    """
    class Meta:
        label = 'utils'
        description = 'Project utilities'
        compress_opt = "-v"
        compress_prog = "gzip"
        compress_suffix = ".gz"
        file_ext = []
        include_dirs = []
        wildcard = []
        path = None

    def _setup(self, base_app):
        super(PmAbstractBaseController, self)._setup(base_app)

        group = base_app.args.add_argument_group('file types', 'Options that set file types.')
        group.add_argument('--flowcell', help="Workon on a specific flowcell", action="store", default=None)
        group.add_argument('--sam', help="Workon sam files", default=False, action="store_true")
        group.add_argument('--bam', help="Workon bam files", default=False, action="store_true")
        group.add_argument('--fastq', help="Workon fastq files", default=False, action="store_true")
        group.add_argument('--fastqbam', help="Workon fastq-fastq.bam files", default=False, action="store_true")
        group.add_argument('--pileup', help="Workon pileup files", default=False, action="store_true")
        group.add_argument('--split', help="Workon *-split directories", default=False, action="store_true")
        group.add_argument('--tmp', help="Workon staging (tx) and tmp directories", default=False, action="store_true")
        group.add_argument('--txt', help="Workon txt files", default=False, action="store_true")
        group.add_argument('--glob', help="Workon freetext glob expression. CAUTION: using wildcard expressions will remove *everything* that matches.", default=None, action="store")

        group = base_app.args.add_argument_group('file transfer', 'Options affecting file transfer operations.')
        group.add_argument('--move', help="Transfer file with move", default=False, action="store_true")
        group.add_argument('--copy', help="Transfer file with copy (default)", default=True, action="store_true")
        group.add_argument('--rsync', help="Transfer file with rsync", default=False, action="store_true")

        group = base_app.args.add_argument_group('compression/decompression', 'Options affecting compression/decompression.')
        group.add_argument('--pbzip2', help="Use pbzip2 as compressing device", default=False, action="store_true")
        group.add_argument('--pigz', help="Use pigz as compressing device", default=False, action="store_true")


    def _process_args(self):
        if self.command in ["compress", "decompress"]:
            if not self._meta.path:
                self.app.log.warn("not running {} on root directory".format(self.command))
                sys.exit()
        if self.pargs.flowcell:
            self._meta.wildcard += [self.pargs.flowcell]
        ## Setup file patterns to use
        if self.pargs.fastq:
            self._meta.file_ext += [".fastq", "fastq.txt", ".fq"]
        if self.pargs.pileup:
            self._meta.file_ext += [".pileup", "-pileup"]
        if self.pargs.txt:
            self._meta.file_ext += [".txt"]
        if self.pargs.fastqbam:
            self._meta.file_ext += ["fastq-fastq.bam"]
        if self.pargs.sam:
            self._meta.file_ext += [".sam"]
        if self.pargs.bam:
            self._meta.file_ext += [".bam"]
        if self.pargs.split:
            self._meta.file_ext += [".intervals", ".bam", ".bai", ".vcf", ".idx"]
            self._meta.include_dirs += ["realign-split", "variants-split"]
        if self.pargs.tmp:
            self._meta.file_ext += [".idx", ".vcf", ".bai", ".bam", ".idx", ".pdf"]
            self._meta.include_dirs += ["tmp", "tx"]
        if self.pargs.glob:
            self._meta.file_ext += [self.pargs.glob]
            
        ## Setup zip program
        if self.pargs.pbzip2:
            self._meta.compress_prog = "pbzip2"
        elif self.pargs.pigz:
            self._meta.compress_prog = "pigz"

        if self._meta.path:
            assert os.path.exists(os.path.join(self._meta.path), "no such folder '{}' in {} directory '{}'".format(self._meta.path))

    @controller.expose(hide=True)
    def default(self):
        print self._help_text

    def _compress(self, label="compress"):
        flist = filtered_walk(os.path.join(self._meta.path), self._filter_fn)

        if len(flist) == 0:
            self.app.log.info("No files matching pattern '{}' found".format(self._meta.pattern))
            return
        if len(flist) > 0 and not query_yes_no("Going to {} {} files ({}...). Are you sure you want to continue?".format(label, len(flist), ",".join([os.path.basename(x) for x in flist[0:10]])), force=self.pargs.force):
            sys.exit()
        for f in flist:
            self.log.info("{}ing {}".format(label, f))
            self.app.cmd.command([self._meta.compress_prog, self._meta.compress_opt, "%s" % f], label, ignore_error=True, **{'workingDirectory':os.path.dirname(f), 'outputPath':os.path.join(os.path.dirname(f), "{}-{}-drmaa.log".format(label, os.path.basename(f)))})

    ## decompress
    @controller.expose(help="Decompress files")
    def decompress(self):
        """Decompress files"""
        if not self._check_project():
            return
        self._meta.path = self.app.config.get_section_dict("projects", option="path", subsection=self.pargs.project_id)

        self._meta.compress_opt = "-dv"
        if self.pargs.pbzip2:
            self._meta.compress_suffix = ".bz2"
        self._meta.pattern = "|".join(["{}{}$".format(x, self._meta.compress_suffix) for x in self._meta.file_ext])
        self._compress(label="decompress")

    @controller.expose(help="Compress files")
    def compress(self):
        if not self._check_project():
            return
        self._meta.path = self.app.config.get_section_dict("projects", option="path", subsection=self.pargs.project_id)
        self._meta.compress_opt = "-v"
        self._meta.pattern = "|".join(["{}$".format(x) for x in self._meta.file_ext])
        self._compress()

