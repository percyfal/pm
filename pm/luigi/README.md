## pm.luigi ##

The `pm.luigi` module is a library of
[luigi](https://github.com/spotify/luigi) tasks, currently focused on,
but not limited to, common bioinformatical tasks.

## Installing  ##

### Pre-requisites ###

It is recommended that you first create a virtual environment in which
to install the packages. Install
[virtualenvwrapper](http://virtualenvwrapper.readthedocs.org/en/latest/)
and use
[mkvirtualenv](http://virtualenvwrapper.readthedocs.org/en/latest/command_ref.html)
to create a virtual environment.

### Installation ###

Currently, `pm.luigi` resides in the `pm` package, even though this is
likely to change in the near future. Furthermore, the luigi code is
part of a feature branch,
[luigi-tasks](https://github.com/percyfal/pm/tree/feature/luigi-tasks).
Therefore, after installation you need to check out this branch. To
install the development version of `pm` and try out `pm.luigi`, do
	
	git clone https://github.com/percyfal/pm
	git fetch origin
	git checkout feature/luigi-tasks
	python setup.py develop

### Dependencies ###

To begin with, you may need to install
[Tornado](http://www.tornadoweb.org/) and
[Pygraphviz](http://networkx.lanl.gov/pygraphviz/) (see
[Luigi](https://github.com/spotify/luigi/blob/master/README.md) for
further information).

The tests depend on the following software to run:

1. [bwa](http://bio-bwa.sourceforge.net/)
2. [samtools](http://samtools.sourceforge.net/)
3. [GATK](http://www.broadinstitute.org/gatk/) - set an environment
   variable `GATK_HOME` to point to your installation path
4. [picard](http://picard.sourceforge.net/) - set an environment
   variabl `PICARD_HOME` to point to your installation path

You also need to install the test data set:

	git clone https://github.com/percyfal/ngs.test.data
	python setup.py install

## Running the tests  ##

Cd to the luigi test directory (`pm/tests/luigi/`) and run

	nosetests -v -s test_wrapper.py
	
To run a given task (e.g. TestLuigiWrappers.test_fastqln), do

	nosetests -v -s test_wrapper.py:TestLuigiWrappers.test_fastqln

### Task visualization and tabulation ###

By default, the tests use a local scheduler, implemented in luigi. For
production purposes, there is also a
[central planner](https://github.com/spotify/luigi/blob/master/README.md#using-the-central-planner).
Among other things, it allows for visualization of the task flow by
using [Tornado](http://www.tornadoweb.org/) and
[Pygraphviz](http://networkx.lanl.gov/pygraphviz/). Results are
displayed in *http://localhost:8081*, results "collected" at
*http://localhost:8082/api/graph*. 

In addition, I have extended the luigi daemon and server code to
generate a table representation of the tasks (in
*http://localhost:8083*). The aim here would be to define a grouping
function that groups task lists according to a given feature (e.g.
sample, project).

In order to view tasks, run

	pm/bin/luigid &
	
in the background, set the PYTHONPATH to the current directory and run
the tests:

	PYTHONPATH=. nosetests -v -s test_wrapper.py
	
## Examples ##

NB: the examples are currently based on the tests in
[pm.tests.luigi.test_wrapper](https://github.com/percyfal/pm/blob/feature/luigi-tasks/tests/luigi/test_wrapper.py).

### Creating file links ###

The task
[pm.luigi.fastq.FastqFileLink](https://github.com/percyfal/pm/blob/feature/luigi-tasks/pm/luigi/fastq.py#L5)
creates a link from source to a target. The source in this case
depends on an *external* task
([pm.luigi.external.FastqFile](https://github.com/percyfal/pm/blob/feature/luigi-tasks/pm/luigi/external.py#L24)),
meaning this file was created by some outside process (e.g. sequencing
machine).

	nosetests -v -s test_wrapper.py:TestLuigiWrappers.test_fastqln

![FastqLn](https://raw.github.com/percyfal/pm/feature/luigi-tasks/pm/luigi/doc/test_fastqln.png)
	       
	
### Alignment with bwa sampe ###

Here I've created the links manually. Orange means dependency on
external task.

	nosetests -v -s test_wrapper.py:TestLuigiWrappers.test_bwasampe

![BwaSampe](https://raw.github.com/percyfal/pm/feature/luigi-tasks/pm/luigi/doc/test_bwasampe.png)
	
### Wrapping up metrics tasks ###

The class
[pm.luigi.picard.PicardMetrics](https://github.com/percyfal/pm/blob/feature/luigi-tasks/pm/luigi/picard.py#L145)
subclasses
[luigi.WrapperTask](https://github.com/spotify/luigi/blob/master/luigi/task.py#L294)
that can be used to require that several tasks have completed. Here
I've used it to group picard metrics tasks:

	nosetests -v -s test_wrapper.py:TestLuigiWrappers.test_picard_metrics

![PicardMetrics](https://raw.github.com/percyfal/pm/feature/luigi-tasks/pm/luigi/doc/test_picard_metrics.png)

This example utilizes a configuration file that links tasks together.
More about that in the next example.

### Working with parent tasks and configuration files ###

All tasks have a default requirement, which I call `parent_task`. In
the current implementation, all tasks subclass `pm.luigi.job.JobTask`,
which provides a `parent_task` class variable. This variable can be
changed, either at the command line (option `--parent-task`) or in a
configuration file. The `parent_task` variable is a string
representing a class in a python module, and could therefore be any
python code of choice. In addition to the `parent_task` variable,
`JobTask` provides variables `_config_section` and
`_config_subsection` that point to sections and subsections in the
config file, which should be in yaml format (see
[google app](https://developers.google.com/appengine/docs/python/config/appconfig)
for nicely structured config files). By default, all `metrics`
functions have as parent class `pm.luigi.picard.InputBamFile`. This
can easily be modified in the config file to:

	picard:
	  # input_bam_file "pipes" input from other modules
	  input_bam_file:
	    parent_task: pm.luigi.samtools.SamToBam
      hs_metrics:
        parent_task: pm.luigi.picard.SortSam
        targets: targets.interval_list
        baits: targets.interval_list
      duplication_metrics:
        parent_task: pm.luigi.picard.SortSam
      alignment_metrics:
        parent_task: pm.luigi.picard.SortSam
      insert_metrics:
        parent_task: pm.luigi.picard.SortSam
  
    samtools:
      samtobam:
        parent_task: tests.luigi.test_wrapper.SampeToSamtools

Note also that `input_bam_file` has been changed to depend on
`pm.luigi.samtools.SamToBam` (default value is
`pm.luigi.external.BamFile`). In addition, the parent task to
`pm.luigi.samtools.SamToBam` has been changed to
`tests.luigi.test_wrapper.SampeToSamtools`, a class defined in the
test as

    class SampeToSamtools(SAM.SamToBam):
        def requires(self):
            return BWA.BwaSampe(sai1=os.path.join(self.sam.replace(".sam", BWA.BwaSampe().read1_suffix + ".sai")),
                                sai2=os.path.join(self.sam.replace(".sam", BWA.BwaSampe().read2_suffix + ".sai")))

This is necessary as there is no default method to go from bam to sai.
Future implementations should possibly include commong 'module
connecting tasks' as these.
	

## Implementation ##

The implementation is still under heavy development and testing so
expect many changes in near future. 

### Basic job task ###


### Program modules ###

`pm.luigi` submodules are named after the application/ 

### Configuration parser ###



## Issues  ##

* Command-line options should override settings in config file - not
  sure if that currently is the case

## TODO/future ideas ##

* Make `pm.luigi` a separate module, independent of `pm`? If so, there
  are two dependencies that should removed and implemented in the
  separate module:
  
  1. YAML configuration parser (currently in
     [pm.ext.ext_yamlconfigparser.py](https://github.com/percyfal/pm/blob/feature/luigi-tasks/pm/ext/ext_yamlconfigparser.py))
  2. shell commands are wrapped with
     [shell.exec_cmd](https://github.com/cement/cement/blob/master/cement/utils/shell.py#L8)
     from the cement package

* DONE? Fix path handling so relative paths can be used (see e.g. run method in
  [fastq](https://github.com/percyfal/pm/blob/feature/luigi-tasks/pm/luigi/fastq.py))
  
* Implement class validation of `parent_task`. Currently, any code can
  be used, but it would be nice if the class be validated against the
  parent class, for instance by using interfaces
