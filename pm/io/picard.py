"""pm picard lib"""
import os
import re
import pandas as pd
from pm.io import index_containing_substring

METRICS_TYPES=['align', 'hs', 'dup', 'insert']

def _raw(x):
    return (x, None)

def _read_picard_metrics(f):
    with open(f) as fh:
        data = fh.readlines()
        # Find histogram line
        i_hist = index_containing_substring(data, "## HISTOGRAM")
        if i_hist == -1:
            i = len(data)
        else:
            i = i_hist
        tmp = [x.rstrip("\n").split("\t") for x in data[0:i] if not re.match("^[ #\n]", x)]
        metrics = pd.DataFrame(tmp[1:], columns=tmp[0])
        if i_hist == -1:
            return (metrics, None)
        tmp = [x.rstrip("\n").split("\t") for x in data[i_hist:len(data)] if not re.match("^[ #\n]", x)]
        hist = pd.DataFrame(tmp[1:], columns=tmp[0])
    return (metrics, hist)

# For now: extension maps to tuple (label, description). Label should
# be reused for analysis definitions
EXTENSIONS={'.align_metrics':('align', 'alignment', _read_picard_metrics),
            '.hs_metrics':('hs', 'hybrid selection', _read_picard_metrics),
            '.dup_metrics':('dup', 'duplication metrics', _read_picard_metrics),
            '.insert_metrics':('insert', 'insert size', _read_picard_metrics),
            '.eval_metrics':('eval', 'snp evaluation', _raw)
            }


def read_metrics(f):
    """Read metrics"""
    (_, metrics_type) = os.path.splitext(f)
    d = EXTENSIONS[metrics_type][2](f)
    return d
