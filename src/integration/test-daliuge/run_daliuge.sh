#!/bin/bash

source /home/kvinsen/virtualenv/shanghai/bin/activate

dlg nm --daemon -vvv --dlg-path=/home/kvinsen/SKA-AU-China-2018/src/integration/test-daliuge -H 202.127.29.9 --log-dir /home/kvinsen/daliuge --max-request-size 10
