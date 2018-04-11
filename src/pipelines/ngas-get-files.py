#!/usr/bin/env python

"""
Get file(s) from NGAS.
"""

import os
import argparse
import subprocess
import re


# NGAS host and port
NGAS_HOST = "159.226.233.198"
NGAS_PORT = 7777


def get_image(fileid, outfile=None, host=NGAS_HOST, port=NGAS_PORT):
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
    cmd = ["wget", "-O", outfile, url]
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
    parser.add_argument("-p", "--port", type=int, default=NGAS_PORT,
                        help="NGAS server port (default: %s)" % NGAS_PORT)

    grp = parser.add_mutually_exclusive_group(required=True)
    grp.add_argument("-f", "--fileid", help="File ID/name in NGAS")
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
        files = [args.fileid]
        if args.outfile:
            outfiles = [args.outfile]
        else:
            outfiles = files

    for fid, fn in zip(files, outfiles):
        print(">>> Retrieving file: %s" % fid)
        if os.path.exists(fn):
            print("File already exists: %s" % fn)
            print("*** skip ***")
            continue
        get_image(fid, outfile=fn, host=args.host, port=args.port)

    if args.path:
        open(args.path, "w").write("\n".join([
            os.path.abspath(fn) for f in outfiles
        ]) + "\n")
        print("Absolute paths of retrieved files saved into: %s" % args.path)


if __name__ == "__main__":
    main()
