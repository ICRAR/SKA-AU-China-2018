#!/bin/bash

source /home/cwu/python27/bin/activate

export DLG_ROOT=/tmp/`hostname`
dlg nm --daemon -vvv -H 0.0.0.0 --log-dir /tmp/daliuge
