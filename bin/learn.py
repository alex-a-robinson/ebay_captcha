#!/usr/bin/env python

'''Tool create classifyer model from classifications'''

import pickle
import argparse
import logging as log
import os
import audio_file
import sklearn
import sklearn.svm
import numpy as np
import matplotlib.pyplot as plt


# Work out where the data is relative to this file
_file_path = os.path.dirname(os.path.realpath(__file__))
classifications_path = _file_path + '/../classifications.pkl'
noise_model_out_path = _file_path + '/../noise_classifyer.pkl'
char_model_out_path = _file_path + '/../char_classifyer.pkl'

# Setup arguments
parser = argparse.ArgumentParser(description='Create classifyer model from classifications')
parser.add_argument('--classifications', '-c', type=str, 
                    default=classifications_path,
                    help='The location of the classifications created by classify.py')
parser.add_argument('--no-noise-model', '-nm', action='store_true',
                    help='Don\'t create a noise classifyer model')
parser.add_argument('--no-char-model', '-cm', action='store_true',
                    help='Don\'t create a character classifyer model')
parser.add_argument('--noise-model-output', '-no', type=str, default=noise_model_out_path, 
                    help='Where to save the noise classifyer model')
parser.add_argument('--char-model-output', '-co', type=str, default=char_model_out_path, 
                    help='Where to save the character classifyer model')
parser.add_argument('--cross-validation', '-cv', action='store_true',
                    help='Use some of the input data to perform cross validation')
parser.add_argument('--verbose', '-v', action='store_true',
                    help='Turn on verbose output')
                    
# Get the parsed args
args = parser.parse_args()

# Setup the log
if args.verbose:
    log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
else:
    log.basicConfig(format="%(levelname)s: %(message)s")
    
def load_classifications(filename):
    '''Load the classifications file'''
    
    log.info('Loading classifications from "%s"' % filename)
    
    with open(filename, 'rb') as infile:
        classifications = pickle.load(infile)
        infile.close()
        
    return classifications
    
def save_model(path, model):
    '''Save a model'''
    
    log.info('Saving model to "%s"' % path)
    
    with open(path, 'wb') as outfile:
        pickle.dump(model, outfile)
        outfile.close()
    
def parse_classifications_noise(classifications):
    '''Create X and Y arrays with labels and features for noise classification'''
    
    log.info('Extracting features for noise model')
    
    X = []
    Y = []
    skipped = 0
    
    for label, files in classifications.items():
        
        # Group all labels except noise
        if label == '.':
            noise_label = 1
        else:
            noise_label = 0
            
        for file in files:
            af = audio_file.AudioFile(file, noise_label)
            
            features = af.extract_feature()
            
            # Skip file on error
            if features is None:
                skipped += 1
                continue
            
            X.append(features)
            Y.append(noise_label)
            
    log.info('Skipped %i due to errors' % skipped)
            
    return (np.array(X), np.array(Y))
            
    
def parse_classifications_characters(classifications):
    '''Create X and Y arrays with labels and features for character classification'''
    
    log.info('Extracting features for character model')
    
    X = []
    Y = []
    for label, files in classifications.items():
            
        # Skip noise labels
        if label == '.':
            continue        
        
        for file in files:            
            af = audio_file.AudioFile(file, label)
            
            features = af.extract_feature()
            
            # Skip file on error
            if features is None:
                continue
            
            X.append(features)
            Y.append(ord(label))
            
    return (np.array(X), np.array(Y))
    
def create_svm(X, Y, cross_validation=False):
    '''Create an svm'''
        
    clf = sklearn.svm.SVC(kernel='linear', C=1)
    
    if not cross_validation:
        log.info('SVM being fit with X.shape=%s, Y.shape=%s' % (X.shape, Y.shape))
        
        clf.fit(X, Y)
        return clf
        
    # Otherwise doing cross validation
    X_train, X_test, Y_train, Y_test = sklearn.cross_validation.train_test_split(X, Y, test_size=0.2, random_state=42)
    
    log.info(('SVM being fit and validated with X_train.shape=%s, Y_train.shape=%s, ' +
              'X_test.shape=%s, Y_test.shape=%s') % (X_train.shape, Y_train.shape, X_test.shape, Y_test.shape))

    clf.fit(X_train, Y_train)
    score = clf.score(X_test, Y_test)
    
    print 'Cross validation score: %f' % score
    
    return clf

# Load the classifications file
classifications = load_classifications(args.classifications)

# Create a noise model and save it
if not args.no_noise_model:
    log.info('Noise Model:')
    X, Y = parse_classifications_noise(classifications)
    clf = create_svm(X, Y, args.cross_validation)
    save_model(args.noise_model_output, clf)

# Create a noise model and save it
if not args.no_char_model:
    log.info('Character Model:')
    X, Y = parse_classifications_characters(classifications)
    clf = create_svm(X, Y, args.cross_validation)
    save_model(args.char_model_output, clf)

