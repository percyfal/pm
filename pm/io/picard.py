"""pm picard lib"""

import os
import re
import pandas as pd
import cStringIO

METRICS_TYPES=['align', 'hs', 'dup', 'insert']

# http://stackoverflow.com/questions/2170900/get-first-list-index-containing-sub-string-in-python
def index_containing_substring(the_list, substring):
    for i, s in enumerate(the_list):
        if substring in s:
              return i
    return -1

def read_metrics(f, ext):
    """Read metrics"""
    with open(f) as fh:
        data = fh.readlines()
        tmp = [x.rstrip().split("\t") for x in data[0:8] if not re.match("^[ #\n]", x)]
        metrics = pd.DataFrame(tmp)
        # Find histogram line
        i_hist = index_containing_substring(data, "## HISTOGRAM")
        if i_hist == -1:
            return (metrics, None)
        tmp = [x.rstrip().split("\t") for x in data[i_hist:len(data)] if not re.match("^[ #\n]", x)]
        hist = pd.DataFrame(tmp)
        return (metrics, hist)
