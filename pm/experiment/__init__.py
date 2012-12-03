"""pm experiment module

Basic organization of *experimental* units. A project is structured as 

PROJECTID/data/SAMPLE/SAMPLERUNGROUP/

This is mapped to the sample structure 

sample:
  sample_run:
    id:
    group:
    analysis:
      - id:
        type:
        label:
        files:

As a consequence, each analysis type will need a specific representation/object. Note that 
this representation does not store metadata *about* samples, it only serves to 
collect the sample runs themselves.
"""
import os
import json
import yaml
from cement.core import backend
from collections import Iterator

LOG = backend.minimal_logger(__name__)

# FIX ME: use config setting
# These names may not be used to name a sample
MERGENAME = "TOTAL"
PROTECTED = [MERGENAME, "config", "doc", "intermediate", "results"]

class BaseDict(dict):
    """Base dictionary class. 

    Subclasses define all fields for each object. Should have validating functions.
    """
    _fields = []
    _dict_fields = []
    _list_fields = []
    def __init__(self, **kw):
        for f in self._fields:
            self[f] = kw.get(f, None)
        for f in self._dict_fields:
            self[f] = kw.get(f, {})
        for f in self._list_fields:
            self[f] = kw.get(f, [])

class Project(BaseDict):
    _fields = ["path", "samples"]
    def __init__(self, **kw):
        BaseDict.__init__(self, **kw)

class SampleCollection(dict):
    """Base sample collection.

    """
    def __iter__(self, **kw):
        return iter([Sample(**x) for x in self.values()])

class Sample(dict):
    """Base Sample class. 

    A Sample consists of several sample runs. 
    """
    def __init__(self, **kw):
        super(Sample, self).__init__( **kw)
    def __iter__(self, **kw):
        return iter([SampleRun(**x) for x in self.values()])

class SampleRun(BaseDict):
    _fields = ["id", "group"]
    _list_fields = ["analysis"]
    def __init__(self, **kw):
        BaseDict.__init__(self, **kw)
    def __iter__(self):
        return iter([Analysis(**x) for x in self["analysis"]])

class Analysis(BaseDict):
    _fields = ["id", "type", "label", "files", "status"]
    def __init__(self, **kw):
        BaseDict.__init__(self, **kw)

def save_samples(sample_conf, samples):
    """Save samples to a yaml configuration file.
    """
    with open(sample_conf, "w") as fh:
        fh.write(yaml.dump(sample_conf))

def load_samples(sample_conf):
    """Load samples from a yaml configuration file.

    """
    with open(sample_conf) as fh:
        samples_d = yaml.load(fh)
    return SampleCollection(**samples_d)

def setup_project(path):
    """Setup project collecting samples from a path"""
    # This should be a simple sample collection that iterates over samples
    samples = SampleCollection()
    for root, dirs, files in os.walk(path):
        proot = os.path.relpath(root, path)
        depth = len(proot.split(os.sep))
        if depth == 0 or depth > 2:
            continue
        if proot == os.curdir:
            continue
        if proot in PROTECTED:
            LOG.debug("skipping namespace-protected directory {}".format(proot))
            continue
        if depth == 1:
            LOG.debug("Tree depth=1; assuming sample level")
            samples[proot] = Sample()
        else:
            LOG.debug("Tree depth=2; assuming sample run group level")
    return samples
