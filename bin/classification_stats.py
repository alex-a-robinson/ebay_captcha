#!/usr/bin/env python

'''Returns some stats about the classifications'''

import argparse
import os
import glob
import logging as log
import pickle

# Work out where the data is relative to this file
_file_path = os.path.dirname(os.path.realpath(__file__))
classifications_path = _file_path + '/../classifications.pkl'

# Setup arguments
parser = argparse.ArgumentParser(description='Classify audio captchas')
parser.add_argument('classifications_path', nargs='?', type=str, 
                    default=classifications_path,
                    help='The path to the classifications file')
                    
# Get the parsed args
args = parser.parse_args()
                    
with open(args.classifications_path, 'rb') as fh:
    data = pickle.load(fh)
    fh.close()
    
for label, files in data.items():
    print 'label: %s has %s items' % (label, len(files))
    
'''
with open('classifications2.pkl', 'wb') as fh:
    pickle.dump(new_data, fh, pickle.HIGHEST_PROTOCOL)
    fh.close()
'''