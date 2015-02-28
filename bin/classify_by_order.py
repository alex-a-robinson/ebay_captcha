#!/usr/bin/env python

'''Tool to classify audio captchas based on order, assumes cutting is correct'''

import glob
import pickle
import os
import argparse

# Setup arguments
parser = argparse.ArgumentParser(description='Classify files based on cut order')
parser.add_argument('--outfile', '-o', type=str, required=True,
                    help='The files to save results to')
parser.add_argument('--infiles', '-i', type=str, required=True,
                   help='The location of the input file(s)')
parser.add_argument('--result', '-r', type=str, required=True,
                   help='The captcha result')

# Get the parsed args
args = parser.parse_args()

group = []
groups = []
for i, file in enumerate(glob.glob(args.infiles)):
    if i % len(args.result) == 0 and i != 0:
        groups.append(group)
        group = []
    
    group.append(os.path.abspath(file))


classifications = {}
for group in groups:
    for i, char in enumerate(args.result):
        if char not in classifications:
            classifications[char] = []
        classifications[char].append(group[i])

# Store the classifications
with open(args.outfile, 'wb') as outputfile:
    pickle.dump(classifications, outputfile, pickle.HIGHEST_PROTOCOL)
    outputfile.close()