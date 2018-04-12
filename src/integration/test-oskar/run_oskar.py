"""
first try to run
"""

import os
from os.path import join
import subprocess
import argparse
import json
import time


def run_interferometer(cmd, ini, setting=False, item='', value=''):
    """Run the OSKAR interferometer simulator."""
    cmd = join(cmd, "oskar_sim_interferometer")
    if setting:
#        print(''.join([cmd, "--set", ini, item, str(value)]))
        subprocess.call([cmd, "--set", ini, item, str(value)])
    else:
#        print(''.join([cmd, ini]))
        subprocess.call([cmd, ini])
        
        
def run_imager(cmd, ini, setting=False, item='', value=''):
    """Run the OSKAR imager."""
    cmd = join(cmd, "oskar_imager")
    if setting:
        # print(''.join([cmd, "--set", ini, item, str(value)]))
        subprocess.call([cmd, "--set", ini, item, str(value)])
    else:
        # print(''.join([cmd, ini]))
        subprocess.call([cmd, ini])


def run(env, freq, telescope, sky_model, source_num, img_size, img_deg):
    # ini files
    current_path = os.getcwd()
    ini_imager = 'sim_imager.ini'
#     ini_imager = join(current_path, ini_imager)
    ini_interferometer = 'sim_interferometer.gpu.ini'

    # define outputs
    ms_file = 'out_ms_s{0}.ms'.format(source_num)
    vis_file = 'out_vis_s{0}.vis'.format(source_num)
    img_file = 'out_img_s{0}'.format(source_num)

    #configurations
    run_interferometer(env, ini_interferometer, True, "observation/start_frequency_hz", freq)
    run_interferometer(env, ini_interferometer, True, "telescope/input_directory", telescope)
    run_interferometer(env, ini_interferometer, True, "sky/oskar_sky_model/file", sky_model)
    run_interferometer(env, ini_interferometer, True, "interferometer/oskar_vis_filename", vis_file)
    run_interferometer(env, ini_interferometer, True, "interferometer/ms_filename", ms_file)

    run_imager(env, ini_imager, True, "image/size", img_size)
    run_imager(env, ini_imager, True, "image/fov_deg", img_deg)
    run_imager(env, ini_imager, True, "image/input_vis_data", vis_file)
    run_imager(env, ini_imager, True, "image/root_path", img_file)

    print("--Simulation configured")
    #  run it
    run_interferometer(env, ini_interferometer, False)
    print("--Visibility data generated")
    run_imager(env, ini_imager, False)
    print("--Dirty Map generated")


def main():
    try:
        settings = json.load(open('configure.json'))
    except ValueError as e:
        print('ERROR: FAILED TO PARSE JSON CONFIG FILE!!')
        print(e.message)
        exit(1)
    print("--Configuration file loaded!")

    sim = settings["sim"]
    # print(sim)
    observation = sim["observation"]
    telescope = sim["telescope"]
    sky_model = sim["sky"]
    img = settings["imaging"]

    run(settings["env"], str(observation["freq_hz"]), telescope["file"], sky_model["file"],
        str(settings["source_num"]), str(img["size"]), str(img["fov_deg"]))


if __name__ == '__main__':
    main()
    print("-------------------------------------------------------------")
