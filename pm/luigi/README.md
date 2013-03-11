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
   variable `PICARD_HOME` to point to your installation path
5. [cutadapt](http://code.google.com/p/cutadapt/) - install with `pip
   install cutadapt`

You also need to install the test data set:

	git clone https://github.com/percyfal/ngs.test.data
	python setup.py develop
	
Note that you **must** use *setup.py develop*.

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
	
## Examples in tests ##

These examples are currently based on the tests in
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
	
## Example scripts  ##

There are also a couple of example scripts in
[pm.luigi.examples](https://github.com/percyfal/pm/tree/feature/luigi-tasks/pm/luigi/examples).
The following examples show how to modify behaviour with configuration
files and custom classes. Note that currently you'll need to modify
the reference paths in the config files manually to point to the
*ngs_test_data* installation. The test data consists of two samples,
one of which (P001_101) has data from two flowcell runs.

The basic configuration setting is 

    bwa:
      bwaref: ../../../../ngs_test_data/data/genomes/Hsapiens/hg19/bwa/chr11.fa
    
    gatk:
      unifiedgenotyper:
        ref: ../../../../ngs_test_data/data/genomes/Hsapiens/hg19/seq/chr11.fa
    
    picard:
      # input_bam_file "pipes" input from other modules
      input_bam_file:
        parent_task: pm.luigi.samtools.SamToBam
      hs_metrics:
        parent_task: pm.luigi.picard.SortSam
        targets: ../../../tests/luigi/targets.interval_list
        baits: ../../../tests/luigi/targets.interval_list
      duplication_metrics:
        parent_task: pm.luigi.picard.SortSam
      alignment_metrics:
        parent_task: pm.luigi.picard.SortSam
      insert_metrics:
        parent_task: pm.luigi.picard.SortSam
    
    samtools:
      samtobam:
        parent_task: pm.luigi.samtools.SampeToSamtools


### Basic align seqcap pipeline ###

In examples directory, running

	python pipeline.py  --project J.Doe_00_01 --indir path/to/ngs_test_data/data/projects --config-file align_seqcap.yaml
	
will execute a basic analysis pipeline:

![AlignSeqcap](https://raw.github.com/percyfal/pm/feature/luigi-tasks/pm/luigi/doc/example_align_seqcap.png)

### Adding adapter trimming  ###

Changing the following configuration section (see `align_adapter_trim_seqcap.yaml`):

	bwa:
	  aln:
        parent_task: pm.luigi.cutadapt.CutadaptJobTask

and running 

	python pipeline.py  --project J.Doe_00_01 --indir /path/to/ngs_test_data/data/projects --config-file align_adapter_trim_seqcap.yaml
	
runs the same pipeline as before, but on adapter-trimmed data.

### Merging samples over several runs ###

Sample *P001_101_index3* has data from two separate runs that should
be merged. The class `pm.luigi.picard.MergeSamFiles` merges sample_run
files and places the result in the sample directory. The
implementation currently depends on the directory structure
'sample/fc1', sample/fc2' etc.

	python pipeline_merge.py  --project J.Doe_00_01 --indir /path/to/ngs_test_data/data/projects --config-file align_seqcap_merge.yaml  --sample P001_101_index3

results in 

![AlignSeqcapMerge](https://raw.github.com/percyfal/pm/feature/luigi-tasks/pm/luigi/doc/example_align_seqcap_merge.png)

See `align_seqcap_merge.yaml` for relevant changes. Note that in this
implementation the merged files end up directly in the sample
directory (i.e. *P001_101_index3*).

### Extending workflows with subclassed tasks ###

It's dead simple to add tasks of a given type. Say you want to
calculate hybrid selection on bam files that have and haven't been
mark duplicated. By subclassing an existing task and giving the new
class it's own configuration file location, you can configure the new
task to depend on whatever you want. In `pipeline_custom.py` I have
added the following class:

	class HsMetricsNonDup(HsMetrics):
		"""Run on non-deduplicated data"""
		_config_subsection = "hs_metrics_non_dup"
		parent_task = luigi.Parameter(default="pm.luigi.picard.DuplicationMetrics")

The `picard` configuration section in the configuration file
`align_seqcap_custom.yaml` now has a new subsection:

	hs_metrics_non_dup:
		parent_task:
		# FIXME: inheritance!
		# Unfortunately need to set this again
		targets: ../../../tests/luigi/targets.interval_list
		baits: ../../../tests/luigi/targets.interval_list

Running 

	python pipeline_custom.py  --project J.Doe_00_01 --indir /path/to/ngs_test_data/data/projects --config-file align_seqcap.yaml --sample P001_102_index6
	
will add hybrid selection calculation on non-deduplicated bam file for sample *P001_102_index6*:

![CustomDedup](https://raw.github.com/percyfal/pm/feature/luigi-tasks/pm/luigi/doc/example_align_seqcap_custom_dup.png)

## Implementation ##

The implementation is still under heavy development and testing so
expect many changes in near future. 

### Basic job task ###

`pm.luigi.job` defines, among other things, a *default shell job
runner*, which is a wrapper for running tasks in shell, and a *base
job task* that subclasses `luigi.Task`. The base job task implements a
couple of functions that are essential for general behaviour:

* `_update_config` that reads the configuration file and overrides
  default settings. It is run from `__init__`, meaning that it is read
  for *every task* (see issues)
  
* `set_parent_task` that sets the parent task for a task. The function
  parses a string (`module.class`) and tries to load `class` from
  `module`, falling back to the default parent task on failure. Here
  it would be nice to implement validation of the parent task in some
  way (via interface classes?)
  
* `set_parent_task_list` that sets a parent task list. Not sure if
  this is the right way to go; the motivation stems from the fact that
  if a task is to be run on several targets (e.g. UnifiedGenotyper on
  sample.bam, sample.clip.bam) the task would only depend on the first
  file. EDIT: or would it? This is probably more related to giving the
  task the correct file name, so this configuration option should
  probably provide a list of 2-tuples of from,to string substitutions.

### Program modules ###

`pm.luigi` submodules are named after the application/program to be
run (e.g. `pm.luigi.bwa` for `bwa`). For consistency, the modules
shoud contain

1. a **job runner** that subclasses
   `pm.luigi.job.DefaultShellJobRunner`. The runner specifies how the
   program is run
   
2. **input** file task(s) that subclass `pm.luigi.job.JobTask` and
   that depend on external tasks in `pm.luigi.external`. The idea is
   that all acceptable file formats be defined as external inputs, and
   that parent tasks therefore must use one/any of these inputs
   
3. a **main job task** that subclasses `pm.luigi.job.JobTask` and has
   as default parent task one of the inputs (previous point). The
   `_config_section` should be set to the module name (e.g. `bwa` for
   `pm.luigi.bwa`). It should also return the *job runner* defined in 1.
   
4. **tasks** that subclass the *main job task*. The
   `_config_subsection` should represent the task name in some way
   (e.g. `aln` for `bwa aln`command)

### Configuration parser ###

Python's standard configuration parser works on `.ini` files allowing
section levels followed by customizations. It would be nice with at
least sections/subsections (python's `ConfigObj` does this), but I
prefer yaml files. Previously, I wrote a config parser that subclasses
an interface from
[cement.core.config](https://github.com/cement/cement/blob/master/cement/core/config.py).
It allows sections and subsections in yaml, treating everything below
that level as lists/dicts/variables. 

## TODO/future ideas/issues ##

NB: many of the issues/ideas are relevant only to our compute
environment.

* Command-line options should override settings in config file - not
  sure if that currently is the case

* UPSTREAM? in `pm.luigi.job.DefaultShellJobRunner._fix_paths`,
  `a.move(b)` doesn't work (I modelled this after
  [luigi hadoop_jar](https://github.com/spotify/luigi/blob/master/luigi/hadoop_jar.py#L63))

* Try: modify __repr__(Task) for better visualization in graphs, via a
  command line option. Currently the graphs include all options,
  making it difficult to read
  
* The previous issue is related to the wish for a dry run: basically
  want to generate a picture of the workflow
  
* Add pm.luigi.pipelines in which pipeline wrappers are put. In the
  main script then import different pre-defined pipelines so one could
  change them via the command line following luigi rules
  
* Pickling states doesn't currently seem to work?

* File suffixes and string substitutions in file names are hard-coded.
  Turning substitutions into options would maybe solve the issue of
  input parameter generation for tasks that are run several times on
  files with different suffixes.

* Speaking of file suffixes, currently assume all fastq files are
  gzipped

* Configuration issues:

  - Read configuration file on startup, and not for every task as is currently the case
  - Variable expansion would be nice (e.g. $GATK_HOME) 
  - Global section for globals, such as num_threads, dbsnp, etc?
  - Reimplement/rethink configuration parser?

* Instead of `bwaref` etc for setting alignment references, utilise
  cloudbiolinux/tool-data

* Make `pm.luigi` a separate module, independent of `pm`? If so, there
  are two dependencies that should removed and implemented in the
  separate module:
  
  - YAML configuration parser (currently in
	[pm.ext.ext_yamlconfigparser.py](https://github.com/percyfal/pm/blob/feature/luigi-tasks/pm/ext/ext_yamlconfigparser.py))
  - shell commands are wrapped with
	[shell.exec_cmd](https://github.com/cement/cement/blob/master/cement/utils/shell.py#L8)
     from the cement package

* DONE? Fix path handling so relative paths can be used (see e.g. run method in
  [fastq](https://github.com/percyfal/pm/blob/feature/luigi-tasks/pm/luigi/fastq.py))
  
* Implement class validation of `parent_task`. Currently, any code can
  be used, but it would be nice if the class be validated against the
  parent class, for instance by using interfaces

* Have tasks talk to a central planner so task lists can be easily
  monitored via a web page

* Integrate with hadoop. This may be extremely easy: set the job
  runner for the JobTasks via the config file; by default, they use
  DefaultShellJobRunner, but could also use a (customized and
  subclassed?) version of `hadoop_jar.HadoopJarJobRunner`

* How control the number of workers/threads in use? An example best
  explains the issue: alignment with `bwa aln` can be done with
  multiple threads. `bwa sampe` is single-threaded, and uses ~5.4GB
  RAM for the human genome. Our current compute cluster has 8-core
  24GB RAM nodes. One solution would be to run 8 samples per node,
  running `bwa aln -t 8` sequentially, wrap them with a `WrappedTask`
  before proceeding with `bwa sampe`, which then should only use 4
  workers simultaneously. For small samples this is ok. For large
  samples, one might imagine partitioning the pipeline into an
  alignment step, in which one sample is run per node, and then
  grouping the remaining tasks and samples in reasonably sized groups.
  This latter approach would probably benefit from SLURM/drmaa
  integration (see following item).

* (Long-term goal?): Integrate with SLURM/drmaa along the lines of
  [luigi.hadoop](https://github.com/spotify/luigi/blob/master/luigi/hadoop.py)
  and
  [luigi.hadoop_jar](https://github.com/spotify/luigi/blob/master/luigi/hadoop_jar.py).
  Currently using the local scheduler on nodes works well enough
