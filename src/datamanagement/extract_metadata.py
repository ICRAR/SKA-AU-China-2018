from __future__ import print_function, division, unicode_literals

import argparse
import os
import re

from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
from astropy import units
import requests


def parseargs():
    """
    Parse the command line arguments
    :return: An args map with the parsed arguments
    """
    parser = argparse.ArgumentParser(description="Extract metadata from a fits file.")
    parser.add_argument("file", help="The file to be processed.")
    
    args = parser.parse_args()
    return args

	
def extract_values(hdulist):
	image = hdulist[0].data
	header = hdulist[0].header
	w = WCS(header)

	fields = ['TELESCOPE', 'SBID', 'PROJECT', 'OBJECT', 'BMAJ', 'BMIN', 'BUNIT', 'BTYPE', 'TMIN', 'TMAX']
	
	values = {}
	
	for field in fields:
		if field in header:
			values[field] = header[field]
	
	if 'RESTFRQ' in header:
		values['RESTFRQ'] = header['RESTFRQ']
	elif 'RESTFREQ' in header:
		values['RESTFRQ'] = header['RESTFREQ']
	
	# Now work with the wcs axes to get spatial and spectral data
	# w.wcs.print_contents()
	corners = []
	ra_size = header['NAXIS1']
	dec_size = header['NAXIS2']
	if header['NAXIS'] == 4:
		samples = [[0,0,0,0], [0, dec_size-1, 0, 0], [ra_size-1, dec_size-1, 0, 0], [ra_size-1, 0, 0, 0] ]
		centre_point = [int(ra_size/2), int(dec_size/2), 0,0]
	elif header['NAXIS'] == 3:
		samples = [[0,0,0], [0, dec_size-1, 0], [ra_size-1, dec_size-1, 0], [ra_size-1, 0, 0] ]
		centre_point = [int(ra_size/2), int(dec_size/2),0]
	else:
		samples = [[0,0], [0, dec_size-1], [ra_size-1, dec_size-1], [ra_size-1, 0] ]
		centre_point = [int(ra_size/2), int(dec_size/2)]
	for sample in samples:
		point = w.all_pix2world([sample], 0)[0]
		corners.append([point[0], point[1]])
	
	values['CORNERS'] = corners
	centre = w.all_pix2world([centre_point], 0)[0]
	values['RA'] = centre[0]
	values['DEC'] = centre[1]
	
	return values

	
def main():
	args = parseargs()
	
	if not os.path.exists(args.file):
		print("Unable to find", args.file)
		return 1
	
	print ("Processing", args.file)
	
	hdulist = fits.open(args.file)
	values = extract_values(hdulist)
	
	print(values)
	return 0

    
if __name__ == '__main__':
    exit(main())
