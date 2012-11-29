"""pm picard lib"""

import pandas as pd
from pm.io import index_containing_substring
from cement.core import backend

LOG = backend.minimal_logger(__name__)

METRICS_TYPES=['variants', 'variants', 'variants', 'insert']

def read_vcf(f):
    """Read vcf file to pandas DataFrame. Will miss out header information."""
    with open(f) as fh:
        data = fh.readlines()
        i_chr = index_containing_substring(data, "#CHROM")
        if not i_chr:
            LOG.warn("No chromosome line found")
            return
        if len(data) == (i_chr + 1):
            LOG.warn("VCF file empty; no calls present!")
            return
        d = pd.DataFrame([x.split("\t") for x in data[i_chr+1:]], columns=data[i_chr].split("\t"))
    return d
    
