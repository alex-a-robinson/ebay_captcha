#!/usr/bin/env python

'''Tool to cut audio file on detected beats'''

import argparse
import os
import glob
import logging as log
import warnings
import sys

from aubio import onset, tempo, source, sink
from aubio.slicing import slice_source_at_stamps

# Work out where the data is relative to this file
_file_path = os.path.dirname(os.path.realpath(__file__))
in_path = _file_path + '/../data/train/raw/*.wav'
out_path  = _file_path + '/../data/train/split/'

# Setup arguments
parser = argparse.ArgumentParser(description='Cut audio files on detected beats')
parser.add_argument('--outputdir', '-o', type=str, default=out_path,
                    help='The directory to save results to')
parser.add_argument('--infiles', '-i', type=str, default=in_path,
                   help='The location of the input file(s)')
parser.add_argument('--no-write', '-nw', action='store_true',
                   help='Dont\'t write output files')
parser.add_argument('--verbose', '-v', action='store_true',
                    help='Turn on verbose output')
                    
# Get the parsed args
args = parser.parse_args()

# Setup the log
if args.verbose:
    log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
else:
    log.basicConfig(format="%(levelname)s: %(message)s")
    
def detect_beats(filename):
    '''Detect beats in a wav file'''
    
    hopsize = 512
    bufsize = 512
    minioi = 80    # minimum inter onset interval in ms
    threshold = 0.6
        
    # Load the file, get sample rate
    try:
        s = source(filename, 0, hopsize)
    except:
        return (None, None)
    samplerate = s.get_samplerate()
    
    method = 'energy' # complexdomain|hfc|phase|specdiff|energy|kl|mkl|default
    
    o = onset(method, bufsize, hopsize)
    o.set_minioi_ms(minioi)
    o.set_threshold(threshold)
    
    timestamps = []
    total_frames = 0
    
    # analyze pass
    while True:
        samples, read = s()
        if o(samples):
            timestamps.append(o.get_last())
        total_frames += read
        if read < hopsize: break
    del s
    
    return (timestamps, samplerate)
    
def write_beats(beats, filename, output_dir, samplerate):
    '''Write a series of beats to differnt files'''
    
    if len(beats) == 0:
        return

    timestamps_end = None

    num_of_samples = 6
    if num_of_samples:
        timestamps_end = [t + num_of_samples for t in beats[1:]]
        timestamps_end += [ 1e120 ]
        
    slice_source_at_stamps(filename, beats, timestamps_end=timestamps_end,
            output_dir=output_dir, samplerate=samplerate)
    
if __name__ == '__main__':
    for file in glob.glob(args.infiles):
        log.info('Detecting beats for %s' % file)
        beats, samplerate = detect_beats(file)
        if beats is None:
            log.warning('Skipping %s due to error when reading' % file)
            continue
    
        if len(beats) <= 5:
            log.warning('Skipping %s due to too few beats' % file)
            continue 
    
        log.info('%i beats found, saving to %s' % (len(beats), args.outputdir))
        
        # Write ouput
        if not args.no_write:
            write_beats(beats, file, args.outputdir, samplerate)