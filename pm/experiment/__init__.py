"""pm experiment module

Basic organization of experimental units. A project is structured as 

PROJECTID/data/SAMPLE/SAMPLERUNGROUP/

This is mapped to the sample structure 

sample:
  sample_run_group:
    sample_run:
      id:
      analyses:
        - id:
          type:
          label:
          files:

As a consequence, each analysis type will need a specific representation/object.
"""
import os
import json
import yaml
from cement.core import backend

LOG = backend.minimal_logger(__name__)

# FIX ME: use config setting
# These names may not be used to name a sample
MERGENAME = "TOTAL"
PROTECTED = [MERGENAME, "config", "doc", "intermediate", "results"]

class BaseDict(dict):
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
        
class Sample(BaseDict):
    def __init__(self, **kw):
        BaseDict.__init__(self, **kw)

class SampleRunGroup(BaseDict):
    def __init__(self, **kw):
        BaseDict.__init__(self, **kw)
    
class SampleRun(BaseDict):
    _fields = ["id"]
    _list_fields = ["analysis"]
    def __init__(self, **kw):
        BaseDict.__init__(self, **kw)

class Analysis(BaseDict):
    _fields = ["id", "type", "label", "files", "status"]
    def __init__(self, **kw):
        BaseDict.__init__(self, **kw)

def setup_project(path):
    """Setup project collecting samples from a path"""
    samples = {}
    for root, dirs, files in os.walk(path):
        proot = os.path.relpath(root, path)
        depth = len(proot.split(os.sep))
        if depth == 0 or depth > 2:
            continue
        if proot == os.curdir:
            continue
        if proot in PROTECTED:
            continue
        if depth == 1:
            LOG.debug("Tree depth=1; assuming sample level")
            samples[proot] = {k:SampleRunGroup() for k in dirs}
        else:
            LOG.debug("Tree depth=2; assuming sample run group level")
    return samples
