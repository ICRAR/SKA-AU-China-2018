#!/usr/bin/env python

"""
Get an ASKAP image from NGAS.
"""

import argparse
import subprocess


# NGAS host and port
NGAS_HOST = "159.226.233.198"
NGAS_PORT = 7777


def get_image(fileid, outfile, host, port):
    """
    Get the ASKAP image from:
        http://<host>:<port>/RETRIEVE?file_id=<file_id>
    """
    url = "http://%(host)s:%(port)d/RETRIEVE?file_id=%(file_id)s" % {
        "host": host,
        "port": port,
        "file_id": fileid
    }
    cmd = ["wget", "-O", outfile, url]
    print("Retrieve CMD: %s" % " ".join(cmd))
    subprocess.check_call(cmd)
    print("Retrieved image as: %s" % outfile)


def main():
    parser = argparse.ArgumentParser(
        description="Get an ASKAP image from NGAS")
    parser.add_argument("-H", "--host", default=NGAS_HOST,
                        help="NGAS server name/IP (default: %s)" % NGAS_HOST)
    parser.add_argument("-p", "--port", type=int, default=NGAS_PORT,
                        help="NGAS server port (default: %s)" % NGAS_PORT)
    parser.add_argument("-f", "--file-id", dest="fileid", required=True,
                        help="ASKAP image file ID/name")
    parser.add_argument("-o", "--outfile",
                        help="Output filename (default: same file name " +
                        "under the working directory")
    args = parser.parse_args()

    if args.outfile is None:
        args.outfile = args.fileid

    get_image(args.fileid, outfile=args.outfile, host=args.host,
              port=args.port)


if __name__ == "__main__":
    main()
