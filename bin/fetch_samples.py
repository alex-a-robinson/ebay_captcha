#!/usr/bin/env python

'''Tool to fetch audio samples'''

import urllib2
import os
import argparse
import logging as log

# Work out where the data is relative to this file
_file_path = os.path.dirname(os.path.realpath(__file__))
out_path = _file_path + '/../data/train/raw/'

# Setup arguments
parser = argparse.ArgumentParser(description='Fetch audio samples')
parser.add_argument('--outputdir', '-o', type=str, default=out_path,
                    help='The output directory to save samplse to')
parser.add_argument('--samples', '-s', type=int, default=50,
                    help='The number of samples to fetch')
parser.add_argument('--outputname', '-n', type=str, 
                    default='ebay-captcha', help='The filename for these samples')
parser.add_argument('--url', '-u', type=str, 
                    default='http://signin.ebay.com/ws/eBayISAPI.dll?FetchAudioCaptcha&siteid=0&co_brandId=0&tokenString=OCNTiAoAAAA%3D&t=1424900118153',
                    help='The url to fetch samples from')
parser.add_argument('--verbose', '-v', action='store_true',
                    help='Turn on verbose output')
                    
# Get the parsed args
args = parser.parse_args()

# Setup the log
if args.verbose:
    log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
else:
    log.basicConfig(format="%(levelname)s: %(message)s")

for i in range(args.samples):
    log.info('%i/%i done' % (i + 1, args.samples))
    
    filename = args.outputname + '-%s.wav' % (i + 1)
    
    # Try fettching the url
    try: 
        response = urllib2.urlopen(args.url)
    except urllib2.HTTPError, e:
        log.error('HTTPError: ' + str(e.code))
        continue
    except urllib2.URLError, e:
        log.error('URLError: ' + str(e.reason))
        continue
    except httplib.HTTPException, e:
        log.error('HTTPException')
        continue
    
    # Read the response and write it
    data = response.read()
    with open(filename, 'wb') as output_file:
        output_file.write(data)
        output_file.close()
