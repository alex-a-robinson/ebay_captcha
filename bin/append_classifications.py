#!/usr/bin/env python

'''Tool merge multiple classifications so classifying can be done in chunks and joined latter'''

import argparse
import logging as log
import pickle
import sys

# Setup arguments
parser = argparse.ArgumentParser(description='Merge multiple classifications into a single classicication')
parser.add_argument('files', nargs='+',
                    help='The files to join, last file should be the output file')
parser.add_argument('--verbose', '-v', action='store_true',
                    help='Turn on verbose output')
                    
# Get the parsed args
args = parser.parse_args()

# Setup the log
if args.verbose:
    log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
else:
    log.basicConfig(format="%(levelname)s: %(message)s")   
    
def merge(dict1, dict2):
    '''Merge two dictionaries of the format {key -> array}'''
    
    merged = {}
    
    for key in dict1:
        if key not in dict2:
            merged[key] = dict1[key]
        else:
            merged[key] = dict1[key] + dict2[key]
            
    for key in dict2:
        if key not in dict1:
            merged[key] = dict2[key]
            
    return merged

# Check we have the correct number of arguments
if len(args.files) < 3:
    log.error('Atleast two input files and a single output file is required')
    sys.exit(1)
    
infiles = args.files[:-1]
outfile = args.files[-1] 

# Load all the input files
merged_classifications = {}
for file in infiles:
    with open(file, 'rb') as fh:
        classifications = pickle.load(fh)
        fh.close()
        
    log.info('Merging "%s"' % file)
    merged_classifications = merge(merged_classifications, classifications)
    
# Write merged classifications to output file
with open(outfile, 'wb') as fh:
    log.info('Written merges to "%s"' % outfile)
    pickle.dump(merged_classifications, fh, pickle.HIGHEST_PROTOCOL)
    fh.close()