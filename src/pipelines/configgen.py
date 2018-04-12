
import os
import os.path as osp

import argparse
from string import Template

REPO_HOME = '/home/ska_au_china_2018/SKA-AU-China-2018'

parset_tpl = '%s/src/pipelines/Simple_Selavy_Test/selavy-singleSource.tpl' % REPO_HOME

work_dir = '/tmp'

with open(parset_tpl, 'r') as pin:
    tpl_str = pin.read()
    tpl = Template(tpl_str)

def convert(img_path):
    """
    """
    img_id = osp.basename(img_path.strip()).replace('.fits', '')
    #os.mkdir('%s/%s' % (work_dir, img_id))
    conf_str = tpl.safe_substitute({'FILE_PATH': img_path, 'RESULT_PATH': '%s/%s' % (work_dir, img_id)})
    conf_fpath = '%s/%.3f-%s.in' % (work_dir, time.time(), img_id)
    with open(conf_fpath, 'w') as confout:
        confout.write(conf_str)
    return conf_fpath

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Trigger a selavy-ngas pipeline')

    parser.add_argument('--fits-path-file', dest='fits_path_file', help='each line is a file id in NGAS',
                        default=None, type=str)
    parser.add_argument('--config-path-file', dest='config_path_file', help='each line is a file id in NGAS',
                        default=None, type=str)
    args = parser.parse_args()
    fpf = args.fits_path_file
    with open(fpf, 'r') as fin:
        img_path = fin.readline()
        conf_fpath = convert(img_path)

    with open(args.config_path_file, 'w') as fou:
        fou.write(conf_fpath)
