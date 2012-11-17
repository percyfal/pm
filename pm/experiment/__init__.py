"""pm experiment module

Basic organization of experimental units. A project is structured as 

PROJECTID/data/SAMPLE/SAMPLERUN

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


MERGENAME = "TOTAL"

class BaseDict(dict):
    _fields = []
    _dict_fields = []
    _list_fields = []
    def __init__(self, **kw):
        for f in fields:
            self[f] = kw.get(f, None)
        for f in dict_fields:
            self[f] = kw.get(f, {})
        for f in list_fields:
            self[f] = kw.get(f, [])

class Project(BaseDict):
    _fields = ["path", "samples"]
    def __init__(self, **kw):
        BaseDict.__init__(**kw)

class Sample(BaseDict):
    _dict_fields = ["sample_run"]
    def __init__(self, **kw):
        BaseDict.__init__(**kw)

class SampleRun(BaseDict):
    _fields = ["id"]
    _dict_fields = ["results", "tables"]
    def __init__(self, **kw):
        BaseDict.__init__(**kw)
        
def load_project_config(path):
    with open(path) as fh:
        config = yaml.load(fh)

def setup_project(path):
    samples = {}
    for root, dirs, files in os.walk(path):
        proot = os.path.relpath(root, path)
        depth = len(proot.split(os.sep))
        if depth == 0 or depth > 2:
            continue
        if proot == os.curdir:
            continue
        if depth == 1:
            samples[proot] = {k:{} for k in dirs}
    return samples
