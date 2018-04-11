#!/bin/bash

source /home/kvinsen/virtualenv/shanghai/bin/activate

export DLG_ROOT=/tmp/daliuge/`hostname`
mkdir -p ${DLG_ROOT}
dlg dim --daemon -vvv --port=8002 --log-dir /tmp/daliuge/dim.log --nodes 192.168.0.101,192.168.0.102,192.168.0.103,192.168.0.104
