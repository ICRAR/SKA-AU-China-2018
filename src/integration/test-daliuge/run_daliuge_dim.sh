#!/bin/bash

source /home/cwu/python27/bin/activate

dlg dim --daemon -vvv -H 202.127.29.97 --port=8002 --log-dir /tmp/daliuge/dim.log --nodes 192.168.0.101,192.168.0.102,192.168.0.103,192.168.0.104
