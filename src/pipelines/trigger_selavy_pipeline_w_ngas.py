import sys
import os
import os.path as osp
import json
import time
import commands

import argparse
from string import Template

REPO_HOME = '/home/ska_au_china_2018/SKA-AU-China-2018'

"""
Example to trigger the Selavy pipeline:
    python trigger_pipeline_w_ngas.py --fileidlist
        /home/ska_au_china_2018/SKA-AU-China-2018/src/pipelines/Simple_Selavy_Test/ngas-fileid-list.txt

The ngas-fileid-list.txt is an ASCII file of multiple lines with each line
denoting the file id image file in the NGAS archive
"""

def parse_args():
    """
    Parse input arguments
    """
    parser = argparse.ArgumentParser(description='Trigger a selavy-ngas pipeline')
    # parser.add_argument('--configfile', dest='config_file', help='each line is an image path',
    #                     default=None, type=str)
    parser.add_argument('--fileidlist', dest='file_id_list', help='each line is a file id in NGAS',
                        default=None, type=str)

    parser.add_argument('--nodelist', dest='node_list', help='a list of node IP addresses separated by commas',
                        default='202.127.29.97', type=str)
    parser.add_argument('--islandlist', dest='island_list', help='a list of island IP addresses separated by commas',
                        default='202.127.29.97', type=str)
    parser.add_argument('--masternode', dest='master_node', help='The master node IP where the graph is submitted to',
                        default='202.127.29.97', type=str)
    parser.add_argument('--masterport', dest='master_port', help='The master node port where the graph is submitted to',
                        default='8001', type=int)

    parser.add_argument('--lgfile', dest='lg_file', help='logical graph path',
                        default='%s/src/pipelines/lg/selavy_ngas_test.json' % REPO_HOME, type=str)

    args = parser.parse_args()
    if (args.img_list is None):
        parser.print_help()
        sys.exit(1)

    return args

if __name__ == "__main__":
    args = parse_args()
    fileids_files = args.file_id_list
    if (not osp.exists(fileids_files)):
        raise Exception('Not found %s' % fileids_files)

    with open(fileids_files, 'r') as imgin:
        img_list = imgin.readlines()
        nb_lines = len(img_list)

    with open(args.lg_file, 'r') as fin:
        aa = json.load(fin)
        nodes = aa['nodeDataArray']

        for node in nodes:
            nk = node['key']
            if (-8 == nk):
                node['Arg02'] = '-F %s' % fileids_files
            elif (-12 == nk):
                node['num_of_copies'] = nb_lines

    new_json = osp.basename(args.lg_file).replace('.json', '_%.3f.json' % (time.time()))
    with open('/tmp/%s' % new_json, 'w') as fout:
        json.dump(aa, fout)

    cmd = 'dlg unroll-and-partition -L /tmp/%s | dlg map -N %s,%s -i %d | dlg submit -H %s -p %d'\
            % (new_json, args.island_list.replace(' ', ''), args.node_list.replace(' ', ''), \
               len(args.island_list.split(',')), args.master_node, args.master_port)

    ret, msg = commands.getstatusoutput(cmd)
    if (0 != ret):
        print("Something is wrong: %s" % msg)
    else:
        print("Graph submitted successfully!")
