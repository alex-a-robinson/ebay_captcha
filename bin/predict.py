#!/usr/bin/env python

'''Tool to do a prediction based on a classifier model and some data'''

import audio_file
import argparse
import os
import glob
import logging as log
import pickle
import sys

# Work out where the data is relative to this file
_file_path = os.path.dirname(os.path.realpath(__file__))
noise_model_path = _file_path + '/../noise_classifyer.pkl'
char_model_path = _file_path + '/../char_classifyer.pkl'
test_data_path = _file_path + '/../data/test/split/*.wav'

# Setup arguments
parser = argparse.ArgumentParser(description='Use a classifier to predict labels of data')
parser.add_argument('files', type=str, default=test_data_path, help='The files to label')
parser.add_argument('--noise-model', '-nm', type=str, default=noise_model_path,
                    help='Path to noise classifyer')
parser.add_argument('--char-model', '-cm', type=str, default=char_model_path,
                    help='Path to noise classifyer')
parser.add_argument('--predict-noise', '-pn', action='store_true',
                    help='Output noise label')
parser.add_argument('--predict-char', '-pc', action='store_true',
                    help='Output character label')
parser.add_argument('--verbose', '-v', action='store_true',
                    help='Turn on verbose output')

# Get the parsed args
args = parser.parse_args()

# Setup the log
if args.verbose:
    log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
else:
    log.basicConfig(format="%(levelname)s: %(message)s")
    
def load_classifier(path):
    '''Load a classifier from a file'''
    
    with open(path, 'rb') as fh:
        clf = pickle.load(fh)
        fh.close()
        
    return clf
    
def print_predictions(Y, Z, classifier=None, auto_next=False):
    '''Print the predictions'''
    
    if classifier:
        print 'Predictions for %s classifier:' % classifier
    else:
        print 'Predictions:'
    
    for label, af in zip(Y, Z):
        print '%s - %s' % (chr(label), af.filename)
        af.play()
        
        if not auto_next:
            raw_input('<ENTER to continue>')
    
files = glob.glob(args.files)

X = []
Z = []

log.info('Extracting features from files')
for file in files:
    af = audio_file.AudioFile(file)
    X.append(af.extract_feature())
    Z.append(af)
    
if not args.predict_noise and not args.predict_char:
    print 'You must use either --predict-char or --predict-noise or both'
    sys.exit(1)

if args.predict_noise:
    log.info('Loading noise classifier')
    clf = load_classifier(args.noise_model)
    
    log.info('Predicting noise labels')
    Y = clf.predict(X)
    
    print_predictions(Y, Z, 'noise')
    
if args.predict_char:
    log.info('Loading character classifier')
    clf = load_classifier(args.char_model)
    
    log.info('Predicting character labels')
    Y = clf.predict(X)
    
    print_predictions(Y, Z, 'character')
    
# Close any open handlers
for af in Z:
    af.close()
    
    
