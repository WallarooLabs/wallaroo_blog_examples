#!/usr/bin/env python

"""
  Generate a large input file to simluate a 'batch'-style workflow

"""
import csv
import hashlib
import random
import sys

def md5(x):
    h = hashlib.md5()
    h.update(str(x))
    return h.hexdigest()

def gen_row(i):
    return [ i,
             random.randint(1,100000),
             random.random(),
             md5(i),
             md5(random.randint(1,20000))*2
    ]

rows = int(sys.argv[1])
sys.stderr.write("Generating {}-row CSV file\n".format(rows))
writer = csv.writer(sys.stdout)
writer.writerow(["ID","SKU","FLUX","MANUFACTURER_NAME","DESCRIPTION"])
for i in range(1, rows):
    writer.writerow(gen_row(i))
