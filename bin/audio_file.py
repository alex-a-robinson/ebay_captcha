import pyaudio
import wave
import sys
import warnings

import scipy.io.wavfile
import scikits.talkbox.features.mfcc

import numpy as np

class AudioFile:
    '''An object representing a single audio file
    
    Example:
      >>> a = AudioFile("1.wav")
      >>> a.play()
      >>> a.close()
    '''
    chunk = 1024

    def __init__(self, filename, label=None):
        
        self.label = label
        self.filename = filename

    def play(self):
        ''' Play entire file '''
        
        # Open the file
        self.wf = wave.open(self.filename, 'rb')
        
        # Create an audio object and stream
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(
            format = self.p.get_format_from_width(self.wf.getsampwidth()),
            channels = self.wf.getnchannels(),
            rate = self.wf.getframerate(),
            output = True
        )
        
        data = self.wf.readframes(self.chunk)
        while data != '':
            self.stream.write(data)
            data = self.wf.readframes(self.chunk)
            
        self.close()

    def close(self):
        ''' Graceful shutdown ''' 
        self.stream.close()
        self.p.terminate()
        
    def __str__(self):
        '''Implment str method'''
        return '%s - %s' % (self.filename, self.label)
            
    def extract_feature(self):
        '''Extract mfcc feature'''
        
        # Load file with scipy
        # Note: scipy.io.wavfile raises warning when opening cut files
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            sample_rate, audio_data = scipy.io.wavfile.read(self.filename)
        
        # Compute Mel Frequency Cepstral Coefficients
        # Note: scikits.talkbox gives a divide by zero warning
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            ceps, mspec, spec = scikits.talkbox.features.mfcc(audio_data)
        
        num_ceps = len(ceps)
        feature_vector =  np.mean(ceps[int(num_ceps / 10):int(num_ceps * 9 / 10)], axis=0)
    
        # Check the result is finite
        if not all(np.isfinite(feature_vector)):
            #raise Exception('A non finite result was returned when extracting_features')
            return None
    
        return feature_vector