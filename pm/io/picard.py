"""pm picard lib"""

import re
import pandas as pd
from pm.io import index_containing_substring

METRICS_TYPES=['align', 'hs', 'dup', 'insert']


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
