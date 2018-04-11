#!/bin/bash

source /home/kvinsen/virtualenv/shanghai/bin/activate

dlg nm --daemon -vvv --dlg-path=/home/kvinsen/SKA-AU-China-2018/src/integration/test-daliuge -H 0.0.0.0 --log-dir /mnt/kvinsen/daliuge --max-request-size 10
