#!/usr/bin/env python

import argparse
import astropy.io.fits as fits

parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--im1', type=str, help='First image')
parser.add_argument('--im2', type=str, help='Second image')
options = parser.parse_args()

im1=fits.getdata(options.im1)
im2=fits.getdata(options.im2)

diff = im1-im2

if im1.shape() == im2.shape():
    sumsq = (diff**2).sum()

    if sumsq > 0.:
        print("FAIL")
    else:
        print("PASS")
    
else:
    print("FAIL")
    
