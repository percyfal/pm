"""pm experiment module

Basic organization of experimental units. A project is structured as 

PROJECTID/data/SAMPLE/SAMPLERUNGROUP/

In the SAMPLERUNGROUP folder

A project configuration consists of a dictionary with (at least) the following hierarchy 

{ 'metadata': dict(project_name, path, sampledir, resultdir),
  'samples' : dict()}

where a sample consists of several sample runs

{ 'sampleruns' : dict() }

and a sample run of

"""
import os
import json
import yaml

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
    _dict_fields = ["sample_run"]
    def __init__(self, **kw):
        BaseDict.__init__(self, **kw)

class SampleRun(BaseDict):
    _fields = ["id"]
    _dict_fields = ["results", "tables"]
    def __init__(self, **kw):
        BaseDict.__init__(self, **kw)

def setup_project(path):
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
            samples[proot] = {k:SampleRun(**{'id':k}) for k in dirs}
    return samples
