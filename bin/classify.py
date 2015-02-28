#!/usr/bin/env python

'''Tool to classify audio samples'''

import audio_file
import argparse
import os
import glob
import logging as log
import pickle
import sys

# Work out where the data is relative to this file
_file_path = os.path.dirname(os.path.realpath(__file__))
data_path = _file_path + '/../data/train/split/*.wav'
out_path  = _file_path + '/../classifications.pkl'

# Setup arguments
parser = argparse.ArgumentParser(description='Classify audio captchas')
parser.add_argument('--outputfile', '-o', type=str, default=out_path,
                    help='The output file to save the results to')
parser.add_argument('--infile', '-i', type=str, default=data_path,
                   help='The location of the input file(s)')
parser.add_argument('--verbose', '-v', action='store_true',
                    help='Turn on verbose output')

# Get the parsed args
args = parser.parse_args()

# Setup the log
if args.verbose:
    log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
else:
    log.basicConfig(format="%(levelname)s: %(message)s")
    

def get_classificaiton(af, replay=False, last_label=None):
    '''Get the users classification of an audiofile'''
    # Ouput which file we are on and play it
    log.info('%i/%i - playing "%s"' % (i, len(files), af.filename))
    af.play()
    
    prompt = '> '
    if replay: prompt = 'replay ' + prompt
    label = raw_input(prompt).upper().strip()
    
    if label == 'HELP': # Show help
        print '''Help:
            DONE       - Stop classifying and save
            REPLAY (?) - Replay the audio
            IGNORE (!) - Ignore the audio, don't save it
            INFO (*)   - Show current audio, and place in total dataset
            LAST       - Show the last label
            EXIT       - Exit without saving
        '''
        return get_classificaiton(audio_file.AudioFile(af.filename), True, label)
    elif label == 'DONE': # Stop classifying
        return None
    elif label in ('REPLAY', '?'): # Replay the file
        return get_classificaiton(audio_file.AudioFile(af.filename), True, label)
    elif label in ('IGNORE', '!'): # Ignore the file
        return '!'
    elif label in ('*', 'INFO'): # Show info
        print '%i/%i - playing "%s"' % (i, len(files), af.filename)
        return get_classificaiton(audio_file.AudioFile(af.filename), True, label)
    elif label in ('', '.'): # Mark file as noise
        return '.'
    elif label in ('EXIT'): # Exit
        print 'Exiting, not saving'
        sys.exit(0)
    elif label in ('LAST'): # Show the last label
        print 'Last label was "%s"' % last_label
        return get_classificaiton(audio_file.AudioFile(af.filename), True, label)
    elif len(label) > 1:
        print 'Didn\'t reconfise "%s", try again' % label
        return get_classificaiton(audio_file.AudioFile(af.filename), True, label)
    else:
        return label
    

# Get the files, loop through each and get user classification
files = glob.glob(args.infile)
classified_files = []
last_label = None
for i, filename in enumerate(files):
        
    af = audio_file.AudioFile(os.path.abspath(filename))
    
    # Get the classification
    label = get_classificaiton(af, last_label=last_label)
    last_label = label
    
    af.close() # Close the filehandle (no longer needed)
    
    # assign the classification, skip this file or stop classifying
    if label == '!':
        log.info('Skipping "%s"' % af.filename)
        continue
    elif label:
        af.label = label
        classified_files.append(af)
    else:
        log.info('Stopping classification')
        break
        
# Store the classifications in an easy to read format ({lable -> [files with label]})
classifications = {}

for af in classified_files:
    if af.label not in classifications:
        classifications[af.label] = []
        
    classifications[af.label].append(af.filename)
    
# Store the classifications
with open(args.outputfile, 'wb') as outputfile:
    log.info('Saving classifications to "%s"' % args.outputfile)
    pickle.dump(classifications, outputfile, pickle.HIGHEST_PROTOCOL)
    outputfile.close()
    
    


