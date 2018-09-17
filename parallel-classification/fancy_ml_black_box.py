import hashlib
import random

CLASSIFIER_SLOWNESS=10

"""
This module simulates a black-box classifier that works on Pandas
dataframes.

Adjust CLASSIFIER_SLOWNESS, above, to make the classifier take more time.

"""

def classify_df(df):
    df['CLASSIFICATION'] = df.apply(_classify_row, axis=1)
    return df

def _classify_row(row):
    h = hashlib.sha256()
    for _ in range(CLASSIFIER_SLOWNESS):
        h.update(str(row))
    random.seed(repr(row))
    return random.uniform(0.0, 1.0)
