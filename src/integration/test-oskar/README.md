### Test OSKAR

This is a brief introductio to test OSKAR at SHAO cluster and generate simulation data

[TOC]

##### 1. Using

- Log into SHAO GPU server

  ```shell
  ssh username@202.127.29.97
  ssh gpu1
  ```

- Set up the configuration in **'configure.json'** file

  ```shell
  # set the telescope
  "telescope":
      {
        "file": "telescopes/ska1low.tm"
      }
  # set the sky model
      "sky":
      {
        "file": "sky_s1000.osm"
      }
  # set the working OSKAR 
  	"env": "/opt/oskar_gpu/bin"
  # set the imager
    "imaging":
    {
      "overwrite": true,
      "size": 512,
      "fov_deg": 10
    }
  ```

- settings

  ```shell
  # telescope
  we use the ska1low.tm by default
  # sky model
  there are 4 options: sky_s3.osm, sky_s10.osm, sky_s100.osm, sky_s1000.osm
  ```

- run the source-generating script

  ```shell
  python run_oskar.py
  ```

##### 2. Outputs

There are 4 kinds of outputs

- **Log file:** oskar_s10.log
- **.ms file:** out_ms_s10.ms
- **visibility:** out_vis_s10.vis
- **dirtymap:** out_img_s10_I.fits