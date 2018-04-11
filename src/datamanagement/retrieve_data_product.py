from __future__ import print_function, division, unicode_literals

import argparse
import os

from astropy.io import votable
from astropy.coordinates import SkyCoord
from astropy import units
import requests


shao_ska_tap_url = 'http://202.127.29.97:8888/casda_vo_tools/tap'

def parseargs():
    """
    Parse the command line arguments
    :return: An args map with the parsed arguments
    """
    parser = argparse.ArgumentParser(description="Check for a deposited file_id in NGAS and download it if present")
    parser.add_argument("file_id", help="The id of the data product to be checked.")
    parser.add_argument("destination_directory", help="The directory where the resulting files will be stored")

    args = parser.parse_args()
    return args

# take in a file id

# Find it in obscore
def get_access_addr(file_id, filename='sync.xml', file_write_mode='wb'):
    data_product_id_query = "select * from ivoa.obscore where obs_publisher_did = '" + file_id + "'"
    params = {'query': data_product_id_query, 'request': 'doQuery', 'lang': 'ADQL', 'format': 'votable'}
    response = requests.get(shao_ska_tap_url+'/sync', params=params)
    response.raise_for_status()
    with open(filename, file_write_mode) as f:
        f.write(response.content)

    result_votable = votable.parse(filename, pedantic=False)
    results_array = result_votable.get_table_by_id('results').array
    print(results_array)
    row = results_array[0]
    print (row)
    return row['access_url']

    #casda.sync_tap_query(data_product_id_query, filename, username=username, password=password)

def download_file(access_addr, destination_directory):
    response = requests.get(access_addr, stream=True)
    if response.status_code != requests.codes.ok:
        if response.status_code == 404:
            print("Unable to download " + access_addr)
            return None
        else:
            response.raise_for_status()

    name = list(filter(bool, access_addr.split("/")))[-1]
    if 'Content-Disposition' in response.headers:
        header_cd = response.headers['Content-Disposition']
        if header_cd is not None and len(header_cd) > 0:
            result = re.findall('filename=(\S+)', header_cd[0])
            if result is not None and len(result) > 0:
                name = result[0]
    content_len = ""
    if 'Content-Length' in response.headers:
        content_len = str(response.headers['Content-Length']) + ' bytes'
    if destination_dir is None and not os.path.exists('temp'):
        os.makedirs('temp')

    file_name = ('temp' if destination_dir is None else destination_dir) + '/' + name
    print('Downloading {} from {} to {}'.format(content_len, access_addr, file_name))
    block_size = 64 * 1024
    with open(file_name, write_mode) as f:
        for chunk in response.iter_content(chunk_size=block_size):
            f.write(chunk)
    print('Download complete\n')


def main():
    args = parseargs()

    if not os.path.exists(args.destination_directory):
        os.makedirs(args.destination_directory)
    
    access_addr = get_access_addr(args.file_id)

    if not access_addr:
        print("File", args.file_id, "is not present in the archive.")
        return 1

    # Download the file
    download_file(access_addr, args.destination_directory)
    
    return 0

    
if __name__ == '__main__':
    exit(main())
