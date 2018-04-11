import sys
import os.path as osp
import json
import time
import commands

import argparse


def parse_args():
    """
    Parse input arguments
    """
    parser = argparse.ArgumentParser(description='Trigger a pipeline')
    parser.add_argument('--configfile', dest='config_file', help='each line is an image path',
                        default=None, type=str)
    parser.add_argument('--lgfile', dest='lg_file', help='logical graph path',
                        default='/home/cwu/data/lg/selavy_test.json', type=str)

    args = parser.parse_args()
    if (args.config_file is None):
        parser.print_help()
        sys.exit(1)

    return args

if __name__ == "__main__":
    args = parse_args()
    conf_file = args.config_file
    if (not osp.exists(conf_file)):
        raise Exception('Not found %s' % conf_file)

    with open(conf_file, 'r') as cin:
        nb_lines = len(cin.readlines())

    with open(args.lg_file, 'r') as fin:
        aa = json.load(fin)
        aa['nodeDataArray'][2]['Arg01'] = 'Arg01=%s' % conf_file
        aa['nodeDataArray'][3]['num_of_copies'] = nb_lines

    new_json = osp.basename(args.lg_file).replace('.json', '_%.3f.json' % (time.time()))
    with open('/tmp/%s' % new_json, 'w') as fout:
        json.dump(aa, fout)

    cmd = 'dlg unroll-and-partition -L /tmp/%s | dlg map -N 202.127.29.97,202.127.29.97 -i 1| dlg submit -H 202.127.29.97 -p 8001' % new_json
    ret, msg = commands.getstatusoutput(cmd)
    if (0 != ret):
        print("Something is wrong: %s" % msg)
    else:
        print("Graph submitted sucessfully!")
