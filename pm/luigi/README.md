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
[pm.tests.luigi.test_wrapper](https://github.com/percyfal/pm/blob/feature/luigi-tasks/tests/luigi/test_wrapper.py)

### Creating file links ###

The task
[pm.luigi.fastq.FastqFileLink](https://github.com/percyfal/pm/blob/feature/luigi-tasks/pm/luigi/fastq.py#L5)
creates a link from source to a target. The source in this case
depends on an *external* task
([pm.luigi.external.FastqFile](https://github.com/percyfal/pm/blob/feature/luigi-tasks/pm/luigi/external.py#L24)),
meaning this file was created by some outside process (e.g. sequencing
machine).

	nosetests -v -s test_fastqln.py

![FastqLn](https://github.com/percyfal/pm/tree/feature/luigi-tasks/pm/luigi/doc/test_fastqln.png)
	
	
### Alignment with bwa ###

	nosetests -v -s test_wrapper.py


## Implementation ##

The implementation is still under heavy development and testing so
expect many changes in near future. 

### Basic job task ###


### Program modules ###

`pm.luigi` submodules are named after the application/ 

### Configuration parser ###



## Issues  ##

* 

## TODO/future ideas ##

* Make `pm.luigi` a separete module, independent of `pm`? If so, there
  are two dependencies that should be implemented in the separate module:
  
  1. YAML configuration parser (currently in [pm.ext]


