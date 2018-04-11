#!/bin/bash

source /home/cwu/python27/bin/activate

dlg nm --daemon -vvv -H $1 --log-dir /tmp/daliuge/$1.log
