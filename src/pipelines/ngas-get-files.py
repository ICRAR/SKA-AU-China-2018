#!/usr/bin/env python

"""
Get file(s) from NGAS.
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


def get_file(fileid, outfile=None, host=NGAS_HOST, port=NGAS_PORT):
    """
    Get a file from NGAS through:
        http://<host>:<port>/RETRIEVE?file_id=<file_id>
    """
    if outfile is None:
        outfile = fileid
    url = "http://%(host)s:%(port)d/RETRIEVE?file_id=%(file_id)s" % {
        "host": host,
        "port": port,
        "file_id": fileid
    }
    cmd = ["curl", "-o", outfile, url]
    print("Retrieve CMD: %s" % " ".join(cmd))
    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError:
        try:
            os.remove(outfile)
        except FileNotFoundError:
            pass
        raise
    print("<<< Retrieved file as: %s" % outfile)


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
    except (URLError, HTTPError):
        raise
    content = resp.read()
    root = ET.fromstring(content)
    crc32 = root.find(".//FileStatus").attrib["Checksum"]
    crc32 = int(crc32) & 0xFFFFFFFF
    print("CRC32: %d" % crc32)
    return crc32


def calc_crc32(fn):
    """
    Calculate the CRC32 of the file.
    """
    prev = 0
    for line in open(fn, "rb"):
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
        description="Get file(s) from NGAS")
    parser.add_argument("-H", "--host", default=NGAS_HOST,
                        help="NGAS server name/IP (default: %s)" % NGAS_HOST)
    parser.add_argument("-P", "--port", type=int, default=NGAS_PORT,
                        help="NGAS server port (default: %s)" % NGAS_PORT)

    grp = parser.add_mutually_exclusive_group(required=True)
    grp.add_argument("-f", "--fileid", nargs="+",
                     help="File IDs/names in NGAS to be retrieved")
    grp.add_argument("-F", "--fileid-list", dest="fileid_list",
                     help="Text file containing a list of file ID/name in NGAS")

    parser.add_argument("-o", "--outfile",
                        help="Required output filename (if use --fileid)" +
                        "or a text file containing the required output " +
                        "filenames for each file specified in --fileid-list")
    parser.add_argument("-p", "--path",
                        help="Output file containing the absolute path(s) of "
                        "every retrieved file(s)")

    args = parser.parse_args()

    if args.fileid_list:
        files = read_filelist(args.fileid_list)
        if args.outfile:
            outfiles = read_filelist(args.outfile)
        else:
            outfiles = files
    else:
        files = args.fileid
        if args.outfile:
            outfiles = [args.outfile]
        else:
            outfiles = files

    status = {}
    for fid, fn in zip(files, outfiles):
        print(">>> Retrieving file: %s" % fid)
        if os.path.exists(fn):
            print("File already exists: %s" % fn)
            print("Check existing file by CRC32 ...")
            crc32_local = calc_crc32(fn)
            print("Try to get CRC32 for the file from remote ...")
            crc32_remote = get_crc32(fid, host=args.host, port=args.port)
            if crc32_local == crc32_remote:
                status[fid] = "skipped"
                print("Local existing file is identical with the remote one")
                print("*** skip ***")
                continue
            else:
                print("Local existing file is different from the remote one")
                print("*** delete and retrieve ***")
                os.remove(fn)

        outdir = os.path.dirname(fn)
        try:
            os.mkdir(outdir)
        except OSError as e:
            if e.errno == 17:
                pass

        get_file(fid, outfile=fn, host=args.host, port=args.port)
        print("Calculating CRC32 for the local file ...")
        crc32_local = calc_crc32(fn)
        crc32_remote = get_crc32(fid, host=args.host, port=args.port)
        print("Checking the CRC32 between the local and remote files ...")
        if crc32_local == crc32_remote:
            status[fid] = "ok"
            print("Retrieved file CRC32-check OK")
        else:
            status[fid] = "retrieved but CRC32 checking failed!"
            raise ValueError("Retrieved file CRC32-check failed!")

    print("=================================================")
    print("Summary:")
    print("-------------------------------------------------")
    for fid in files:
        print("%s\t\t: %s" % (fid, status[fid]))
    print("-------------------------------------------------")

    if args.path:
        open(args.path, "w").write("\n".join([
            os.path.abspath(fn) for f in outfiles
        ]) + "\n")
        print("Absolute paths of retrieved files saved into: %s" % args.path)


if __name__ == "__main__":
    main()
