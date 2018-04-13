#!/usr/bin/env python

"""
Query MWA observation data for an ObsID from NGAS.
"""

import os
import sys
import argparse
import re
import json
try:
    # Python 2.7
    from urllib import urlencode
    from urllib2 import urlopen, URLError, HTTPError
except ImportError:
    # Python 3.x
    from urllib.parse import urlencode
    from urllib.request import urlopen
    from urllib.error import URLError, HTTPError


# NGAS host and port
NGAS_HOST = "159.226.233.198"
NGAS_PORT = 7777


def get_obsid_filenames(obsid, host=NGAS_HOST, port=NGAS_PORT):
    """
    Query the NGAS to get the list of filenames belonging to the
    given ObsID.
    """
    params = {
        "query": "files_like",
        "like": "{0}%.fits".format(obsid),
        "format": "json",
    }
    url = "http://%(host)s:%(port)d/QUERY?%(query)s" % {
        "host": host,
        "port": port,
        "query": urlencode(params),
    }
    print("Query URL: %s" % url)
    try:
        content = urlopen(url).read()
    except (URLError, HTTPError):
        raise
    data = json.loads(content)
    files = data["files_like"]
    # XXX: filename/fileid is 'col3'
    filenames = [item["col3"] for item in files]
    if len(filenames) == 0:
        raise RuntimeError("Observation data do not archived in NGAS")

    # Filter out the raw observation data
    #   * <obsid>_metafits_ppds.fits
    #   * <obsid>_yyyymmddhhmmss_gpubox??_??.fits
    p = re.compile(r'^%(obsid)s_(metafits_ppds|[0-9]{14}_gpubox[0-9][0-9]_[0-9][0-9])\.fits$' %
                   {"obsid": obsid})
    filenames = [fn for fn in filenames if p.match(fn)]
    return filenames


def get_files(files):
    pass


def main():
    parser = argparse.ArgumentParser(
        description="Query the observation data for an ObsID from NGAS")
    parser.add_argument("-H", "--host", default=NGAS_HOST,
                        help="NGAS server name/IP (default: %s)" % NGAS_HOST)
    parser.add_argument("-P", "--port", type=int, default=NGAS_PORT,
                        help="NGAS server port (default: %s)" % NGAS_PORT)
    parser.add_argument("-i", "--obsid", type=int, required=True,
                        help="MWA observation ID")
    parser.add_argument("-o", "--outdir",
                        help="Output directory to store the retrieved " +
                        "observation data (default: a directory with obsid " +
                        "as its name at the current working directory)")
    args = parser.parse_args()

    print("Observation ID: %d" % args.obsid)
    filenames = get_obsid_filenames(args.obsid, host=args.host, port=args.port)
    print("-------------------------------------------------")
    print("Following %d files belonging to ObsID %d:" %
          (len(filenames), args.obsid))
    print("-------------------------------------------------")
    print("\n".join(filenames))
    print("-------------------------------------------------")

    if args.outdir is None:
        args.outdir = str(args.obsid)
    print("Output directory: %s" % args.outdir)
    pathlist = args.outdir + ".list"
    open(pathlist, "w").write("\n".join([
        os.path.join(os.path.abspath(args.outdir), fn) for fn in filenames
    ]) + "\n")
    print("Filenames and output paths saved into file: %s" % pathlist)
    print("-------------------------------------------------")
    print("NOTE: To actually retrieve the observation data, use:")
    print("ngas-get-files.py -F {0} -o {0}".format(pathlist))
    print("-------------------------------------------------")


if __name__ == "__main__":
    main()
