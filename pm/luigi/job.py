import random
import sys
import os
import datetime
import subprocess
import logging
import warnings
import luigi
from luigi.task import flatten
from cement.utils import shell
from pm.luigi import interface

# Use luigi-interface for now
logger = logging.getLogger('luigi-interface')

class JobRunner(object):
    run_job = NotImplemented

class DefaultShellJobRunner(JobRunner):
    def __init__(self):
        pass

    @staticmethod
    def _fix_paths(job):
        """Modelled after hadoop_jar.HadoopJarJobRunner._fix_paths.
        """
        tmp_files = []
        args = []
        for x in job.args():
            if isinstance(x, luigi.LocalTarget): # input/output
                if x.exists(): # input
                    args.append(x.path)
                else: # output
                    y = luigi.LocalTarget(x.path + \
                                              '-luigi-tmp-%09d' % random.randrange(0, 1e10))
                    logger.info("Using temp path: {0} for path {1}".format(y.path, x.path))
                    args.append(y.path)
                    if job.add_suffix():
                        x = luigi.LocalTarget(x.path + job.add_suffix())
                        y = luigi.LocalTarget(y.path + job.add_suffix())
                    tmp_files.append((y, x))
            else:
                args.append(str(x))
        return (tmp_files, args)

    @staticmethod
    def _get_main(job):
        """Add main program to command. Override this for programs
        where main is given as a parameter, e.g. for GATK"""
        return job.main()

    def run_job(self, job):
        if not job.exe():# or not os.path.exists(job.exe()):
            logger.error("Can't find executable: {0}, full path {1}".format(job.exe(),
                                                                            os.path.abspath(job.exe())))
            raise Exception("executable does not exist")
        arglist = [job.exe()]
        if job.main():
            arglist.append(self._get_main(job))
        if job.opts():
            arglist.append(job.opts())
        (tmp_files, job_args) = DefaultShellJobRunner._fix_paths(job)
        
        arglist += job_args

        logger.info(' '.join(arglist))
        (stdout, stderr, returncode) = shell.exec_cmd(' '.join(arglist), shell=True)

        if returncode == 0:
            logger.info("Shell job completed")
            for a, b in tmp_files:
                logger.info("renaming {0} to {1}".format(a.path, b.path))
                a.move(b.path)
        else:
            raise Exception("Job '{}' failed: \n{}".format(' '.join(arglist).replace("= ", "="), " ".join([stderr])))
                
class BaseJobTask(luigi.Task):
    config_file = luigi.Parameter(is_global=True, default=os.path.join(os.getenv("HOME"), ".pm2", "jobconfig.yaml"))
    options = luigi.Parameter(default=None)
    _config_section = None
    _config_subsection = None
    task_id = None
    n_reduce_tasks = 8

    def __init__(self, *args, **kwargs):
        params = self.get_params()
        param_values = self.get_param_values(params, args, kwargs)
        for key, value in param_values:
            if key == "config_file":
                config_file = value
                kwargs = self._update_config(config_file, **kwargs)
        super(BaseJobTask, self).__init__(*args, **kwargs)

    def _update_config(self, config_file, **kwargs):
        """Update configuration for this task"""
        config = interface.get_config(config_file)
        if not config.has_section(self._config_section):
            return kwargs
        for key, value in self.get_params():
            new_value = None
            if config.has_key(self._config_section, key):
                new_value = config.get(self._config_section, key)
            if config.has_section(self._config_section, self._config_subsection):
                if config.has_key(self._config_section, key, self._config_subsection):
                    new_value = config.get(self._config_section, key, self._config_subsection)
            if new_value:
                kwargs[key] = new_value
                logger.info("Reading config section, setting {0} to {1}".format(key, new_value))
            else:
                logger.debug("Using default value for {0}".format(key))
        return kwargs

    def exe(self):
        """Executable"""
        return None

    def main(self):
        """For commands that have subcommands"""
        return None

    def opts(self):
        """Generic options placeholder"""
        return self.options

    def add_suffix(self):
        """Some programs (e.g. samtools sort) have the bad habit of
        adding a suffix to the output file name. This needs to be
        accounted for in the temporary output file name."""
        return ""
        
    def init_local(self):
        """Setup local settings (e.g. read from config file?)

        """
        pass

    def run(self):
        self.init_local()
        self.job_runner().run_job(self)

    def complete(self):
        """
        If the task has any outputs, return true if all outputs exists.
        Otherwise, return whether or not the task has run or not
        """
        outputs = flatten(self.output())
        inputs = flatten(self.input())
        if len(outputs) == 0:
            # TODO: unclear if tasks without outputs should always run or never run
            warnings.warn("Task %r without outputs has no custom complete() method" % self)
            return False
        for output in outputs:
            if not output.exists():
                return False
            # Local addition: if any dependency is newer, then run
            if any([os.stat(x.fn).st_mtime > os.stat(output.fn).st_mtime for x in inputs if x.exists()]):
                return False
        else:
            return True

    def get_param_default(self, k):
        """Get the default value for a param"""
        params = self.get_params()
        for key, value in params:
            if k == key:
                return value.default
        return None

class JobTask(BaseJobTask):
    def job_runner(self):
        return DefaultShellJobRunner()

    def args(self):
        return []
