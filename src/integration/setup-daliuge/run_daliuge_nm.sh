#!/bin/bash

source /home/kvinsen/virtualenv/shanghai/bin/activate

export DLG_ROOT=/tmp/daliuge/`hostname`
mkdir -p ${DLG_ROOT}
dlg nm --daemon -vvv -H 0.0.0.0 --log-dir /tmp/daliuge --dlg-path=/home/ska_au_china_2018/common
