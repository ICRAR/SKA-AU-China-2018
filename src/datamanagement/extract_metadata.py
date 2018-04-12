"""
This script was used to retroactively add metadata from the image cube fits
files that were already in the SHAO NGAS installation like this:

for x in `echo "select file_id, file_name from ngas_files where file_id like 'observations-%.fits';" | sqlite3 ~/NGAS/ngas.sqlite`
do
    lala=`echo $x | sed 's/|/ /g'`
    fileid=`echo $lala | cut -d\  -f1`
    filename=`echo $lala | cut -d\  -f2`
    python extract_metadata.py 'host=localhost user=shaoska dbname=shaoska password=shaoska' $fileid /mnt/data1/askap/$filename
done

Next step is to adapt it to automatically extract the same data out of the
incoming images from the pipeline executions.
"""

from __future__ import print_function, division, unicode_literals

import argparse
import contextlib
import os
import re

from astropy.io import fits
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
from astropy import units
import requests
import psycopg2


def parseargs():
    """
    Parse the command line arguments
    :return: An args map with the parsed arguments
    """
    parser = argparse.ArgumentParser(description="Extract metadata from a fits file.")
    parser.add_argument("dsn", help="The dsn used to connect to the database.")
    parser.add_argument("file_id", help="The ID of the file to be processed.")
    parser.add_argument("filename", help="The file to be processed.")
    
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


def insert_catalogue_dataproduct(dsn, fid, vals):
	ra, dec, obs_id, object_name, project = [vals[x] for x in ('RA', 'DEC', 'SBID', 'OBJECT', 'PROJECT')]
	with contextlib.closing(psycopg2.connect(dsn)) as db:
		with contextlib.closing(db.cursor()) as cursor:
			cursor.execute("UPDATE data_product SET s_ra=%s, s_dec=%s, obs_id=%s, object_name=%s, project=%s WHERE file_id=%s", (ra, dec, obs_id, object_name, project, fid,))
			cursor.execute('COMMIT')

	
def main():
	args = parseargs()
	
	if not os.path.exists(args.filename):
		print("Unable to find", args.filename)
		return 1
	
	print ("Processing", args.filename)
	
	hdulist = fits.open(args.filename)
	values = extract_values(hdulist)
	
	print(values)
	insert_catalogue_dataproduct(args.dsn, args.file_id, values)
	return 0

    
if __name__ == '__main__':
    exit(main())
