#
#    ICRAR - International Centre for Radio Astronomy Research
#    (c) UWA - The University of Western Australia, 2018
#    Copyright by UWA (in the framework of the ICRAR)
#    All rights reserved
#
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 2.1 of the License, or (at your option) any later version.
#
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#    Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston,
#    MA 02111-1307  USA
#
"""Ditto from filename

This script was used to import all the ASKAP datasets already stored in the
NGAS SHAO installation into the VOTools database for exposing them as
VO data products through the obscore interface.

To achieve this, we ran this script as such:

$> echo "select file_id from ngas_files;" | sqlite3 ~/NGAS/ngas.sqlite | \
   xargs python register_existing_askap_data_into_votools_db.py 'host=XXX username=XXX password=XXX dbname=XXX'
"""


import contextlib
import logging
import re

import psycopg2

logger = logging.getLogger(__name__)

cubes_re = re.compile(r'observations-.*-image_cubes.*.fits')
visibilities_re = re.compile(r'observations-.*-measurement_sets-.*.tar')

def register_dataproduct(dsn, fid, dptype):
    with contextlib.closing(psycopg2.connect(dsn)) as db:
        with contextlib.closing(db.cursor()) as cursor:
            cursor.execute("INSERT INTO data_product(file_id, dataproduct_type, deposit_state) VALUES (%s, %s, 'DEPOSITED')", (fid, dptype))
            cursor.execute('COMMIT')
            logger.info('Registered %s as a %s', fid, dptype)

def register_file(dsn, fname):

    if cubes_re.match(fname):
        register_dataproduct(dsn, fname, 'cube')
    elif visibilities_re.match(fname):
        register_dataproduct(dsn, fname, 'visibility')
    else:
        logger.info('Unknown file type: %s', fname)

if __name__ == '__main__':
    import sys

    logging.basicConfig(level=logging.INFO)
    dsn = sys.argv[1]
    for fid in sys.argv[2:]:
        register_file(dsn, fid)