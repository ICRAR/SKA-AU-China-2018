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
Example to trigger the ASKAP Imaging pipeline:
    python trigger_askap.py 

The generator script contains all information on data location and 
other parameters. We expect this script to be configured by an independent 
program. For this purpose, we do not need any input arguments. 
"""

def parse_args():
    """
    Parse input arguments
    """
    parser = argparse.ArgumentParser(description='Trigger a basic ASKAP imaging pipeline')

    parser.add_argument('--nodelist', dest='node_list', help='a list of node IP addresses separated by commas',
                        default='202.127.29.97', type=str)
    parser.add_argument('--islandlist', dest='island_list', help='a list of island IP addresses separated by commas',
                        default='202.127.29.97', type=str)
    parser.add_argument('--masternode', dest='master_node', help='The master node IP where the graph is submitted to',
                        default='202.127.29.97', type=str)
    parser.add_argument('--masterport', dest='master_port', help='The master node port where the graph is submitted to',
                        default='8001', type=int)

    parser.add_argument('--lgfile', dest='lg_file', help='logical graph path',
                        default='%s/src/pipelines/lg/askap_2.json' % REPO_HOME, type=str)

    parser.add_argument('--repopath', dest='repopath', help='path to generator script',
                        default='%s/src/pipelines/askap_imaging/' % REPO_HOME, type=str)


    args = parser.parse_args()
    return args

if __name__ == "__main__":
    args = parse_args()

    # generate a working directory
    work_dir = '/tmp/dlg_work_dir_%.3f' % time.time()
    os.mkdir(work_dir)

    gen_script = "source " + args.repopath + 'generator_cimager.sh'
    exec_script = "source " + '/tmp/run_cimager.sh'
    with open(args.lg_file, 'r') as fin:
        aa = json.load(fin)
        nodes = aa['nodeDataArray']

        for node in nodes:
            nk = node['key']
            if (-8 == nk):
                node['Arg01'] = gen_script
            elif (-12 == nk):
                node['Arg01'] = exec_script

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
