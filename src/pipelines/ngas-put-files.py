#!/usr/bin/env python

"""
Put file(s) onto NGAS.
"""

import os
import argparse
import subprocess
import re
import zlib
import xml.etree.ElementTree as ET
try:
    # Python 2.7
    from urllib2 import Request, urlopen, URLError, HTTPError
except ImportError:
    # Python 3.x
    from urllib.request import Request, urlopen
    from urllib.error import URLError, HTTPError


# NGAS host and port
NGAS_HOST = "159.226.233.198"
NGAS_PORT = 7777


def put_file(fp, host=NGAS_HOST, port=NGAS_PORT):
    """
    Put a file into NGAS via:
    $ curl -X POST -i -H "Content-Type: application/octet-stream" \
           --data-binary "@/path/to/<filename>" \
           http://<host>:<port>/ARCHIVE?filename=<filename>

    References:
    * http://ngas.readthedocs.io/en/latest/commands/storage.html#qarchive
    """
    url = "http://%(host)s:%(port)d/ARCHIVE?filename=%(filename)s" % {
        "host": host,
        "port": port,
        "filename": os.path.basename(fp),
    }
    cmd = ["curl", "-X", "POST",
           "-H", "Content-Type: application/octet-stream",
           "--data-binary", "@%s" % os.path.abspath(fp),
           url]
    print("Put CMD: %s" % " ".join(cmd))
    subprocess.check_call(cmd)
    print("<<< Put file: %s" % fp)


def get_crc32(fileid, host=NGAS_HOST, port=NGAS_PORT):
    """
    Get the CRC32 checksum of the specified file from NGAS.
    """
    url = "http://%(host)s:%(port)d/STATUS?file_id=%(file_id)s" % {
        "host": host,
        "port": port,
        "file_id": fileid
    }
    print("Retrieving file status: %s" % url)
    req = Request(url)
    try:
        resp = urlopen(req)
    except HTTPError:
        # e.g., file does not exist in NGAS
        return None
    except URLError:
        raise
    content = resp.read()
    root = ET.fromstring(content)
    try:
        crc32 = root.find(".//FileStatus").attrib["Checksum"]
        crc32 = int(crc32) & 0xFFFFFFFF
        print("CRC32: %d" % crc32)
        return crc32
    except AttributeError:
        # FileStatus/Checksum does not exist (e.g., file does not exist in NGAS)
        return None


def calc_crc32(fp):
    """
    Calculate the CRC32 of the file.
    """
    prev = 0
    for line in open(fp, "rb"):
        prev = zlib.crc32(line, prev)
    return (prev & 0xFFFFFFFF)


def read_filelist(filelist):
    """
    Read the given text file containing a list of filenames, while
    ignore the empty lines and comment lines.
    """
    files = [l.strip() for l in open(filelist).readlines()]
    p = re.compile(r"^\s*($|#)")
    files = [f for f in files if not p.match(f)]
    return files


def main():
    parser = argparse.ArgumentParser(
        description="Put file(s) onto NGAS")
    parser.add_argument("-H", "--host", default=NGAS_HOST,
                        help="NGAS server name/IP (default: %s)" % NGAS_HOST)
    parser.add_argument("-P", "--port", type=int, default=NGAS_PORT,
                        help="NGAS server port (default: %s)" % NGAS_PORT)

    grp = parser.add_mutually_exclusive_group(required=True)
    grp.add_argument("-f", "--files", nargs="+",
                     help="Files to be put onto NGAS")
    grp.add_argument("-F", "--files-list", dest="files_list",
                     help="Text file containing a list of files to be " +
                     "put onto NGAS")

    args = parser.parse_args()

    if args.files_list:
        files = read_filelist(args.files_list)
    else:
        files = args.files

    status = {}
    for fp in files:
        fn = os.path.basename(fp)
        print(">>> Putting file: %s" % fp)
        if not os.path.exists(fp):
            status[fp] = "not exists"
            print("WARNING: File does not exist: %s" % fp)
            print("*** skip ***")
            continue

        print("Calculating CRC32 for the local file ...")
        crc32_local = calc_crc32(fp)
        print("Try to get CRC32 for the file from remote ...")
        crc32_remote = get_crc32(fn, host=args.host, port=args.port)
        if crc32_local == crc32_remote:
            status[fp] = "skipped (already in NGAS)"
            print("Identical file already exists in NGAS")
            print("*** skip ***")
            continue

        put_file(fp, host=args.host, port=args.port)
        print("Checking the CRC32 between the local and remote files ...")
        crc32_remote = get_crc32(fn, host=args.host, port=args.port)
        if crc32_local == crc32_remote:
            status[fp] = "ok"
            print("Put file CRC32-check OK")
        else:
            status[fp] = "put but CRC32 checking failed!"
            raise ValueError("Put file CRC32-check failed!")

    print("=================================================")
    print("Summary:")
    print("-------------------------------------------------")
    for fp in files:
        print("%s\t\t: %s" % (fp, status[fp]))


if __name__ == "__main__":
    main()
