#!/usr/bin/env python

"""

This file represents the 'old' way of doing things: running everything in
one python process, with direct file access.

"""

import pandas as pd
import sys
import fancy_ml_black_box

infile = sys.argv[1]
outfile = sys.argv[2]

df = pd.read_csv(infile, index_col=0, dtype=unicode, engine='python')
fancy_ml_black_box.classify_df(df)
df.to_csv(outfile, header=False)

