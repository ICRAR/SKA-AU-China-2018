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

    parser.add_argument('--parset', dest='parset_tpl', help='parset template file',
                        default='%s/src/pipelines/Simple_Selavy_Test/selavy-singleSource.tpl' % REPO_HOME,
                        type=str)
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

    # generate a working directory
    work_dir = '/tmp/dlg_work_dir_%.3f' % time.time()
    os.mkdir(work_dir)

    # for each image, generate its ParsetFile
    with open(args.parset_tpl, 'r') as pin:
        tpl_str = pin.read()
        tpl = Template(tpl_str)

    conf_in_list = []
    with open(fileids_files, 'r') as imgin:
        img_list = imgin.readlines()
        for img_path in img_list:
            img_id = osp.basename(img_path.strip()).replace('.fits', '')
            os.mkdir('%s/%s' % (work_dir, img_id))
            conf_str = tpl.safe_substitute({'FILE_PATH': img_path, 'RESULT_PATH': '%s/%s' % (work_dir, img_id)})
            conf_fpath = '%s/%s.in' % (work_dir, img_id)
            with open(conf_fpath, 'w') as confout:
                confout.write(conf_str)
            conf_in_list.append(conf_fpath)

    conf_file = '%s/total.conf' % (work_dir)
    with open(conf_file, 'w') as confout:
        confout.write(os.linesep.join(conf_in_list))

    nb_lines = len(conf_in_list)

    with open(args.lg_file, 'r') as fin:
        aa = json.load(fin)
        aa['nodeDataArray'][2]['Arg01'] = 'Arg01=%s' % conf_file
        aa['nodeDataArray'][3]['num_of_copies'] = nb_lines

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
