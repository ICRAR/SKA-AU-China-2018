import sys
import os
import os.path as osp
import json
import time
import commands

import argparse
from string import Template

"""
Example to trigger the pipeline:
    python trigger_pipeline.py --configfile /home/cwu/data/config/single_config.txt

The single_config.txt is an ASCII file with multiple lines with each line
denoting the full path of an image file (e.g. the FITS image cube)
"""


def parse_args():
    """
    Parse input arguments
    """
    parser = argparse.ArgumentParser(description='Trigger a pipeline')
    # parser.add_argument('--configfile', dest='config_file', help='each line is an image path',
    #                     default=None, type=str)
    parser.add_argument('--imglist', dest='img_list', help='each line is an image path',
                        default=None, type=str)
    parser.add_argument('--parset', dest='parset_tpl', help='parset template file',
                        default='/home/cwu/SKA-AU-China-2018/src/pipelines/Simple_Selavy_Test/selavy-singleSource.tpl',
                        type=str)
    parser.add_argument('--lgfile', dest='lg_file', help='logical graph path',
                        default='/home/cwu/data/lg/selavy_test.json', type=str)

    args = parser.parse_args()
    if (args.img_list is None):
        parser.print_help()
        sys.exit(1)

    return args

if __name__ == "__main__":
    args = parse_args()
    imgfiles = args.img_list
    if (not osp.exists(imgfiles)):
        raise Exception('Not found %s' % imgfiles)

    # generate a working directory
    work_dir = '/tmp/dlg_work_dir_%.3f' % time.time()
    os.mkdir(work_dir)

    # for each image, generate its ParsetFile
    with open(args.parset_tpl, 'r') as pin:
        tpl_str = pin.read()
        tpl = Template(tpl_str)

    conf_in_list = []
    with open(imgfiles, 'r') as imgin:
        img_list = imgin.readlines()
        for img_path in img_list:
            img_id = osp.basename(img_path).replace('.fits', '')
            conf_str = tpl.safe_substitute({'FILE_PATH': img_path, 'RESULT_PATH': '%s/%s' % (work_dir, img_id)})
            conf_fpath = '%s/%s.in' % (work_dir, img_id)
            with open(conf_fpath, 'w') as confout:
                confout.write(conf_str)
            conf_in_list.append(conf_fpath)

    conf_file = '%s/total.conf' % (work_dir)
    with open(conf_file, 'w'):
        conf_file.write(os.linesep.join(conf_in_list))

    nb_lines = len(conf_in_list)

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
        print("Graph submitted successfully!")
