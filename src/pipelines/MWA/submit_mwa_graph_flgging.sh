#!/bin/bash

function print_usage {
	echo "$0 [-h | -?] [-d <data_dir>]  [-o <obs_name>]"
	echo
	echo "-h, -?: Show this help"
	echo "-d <data_dir>:    Provide the directory where all the data resides (or will reside)"
	echo "-o <obs_name>: Provide the observation name"
}
#config daliuge enviroment
source /home/blao/MWA/bashrc

# Where are we?
this_dir=`dirname $0`

# The logical graph we want to submit
lg_dir="$this_dir"/../lg
lg_file="$lg_dir"/mwa_flagging.json

# Handle command-line arguments
OBS_NAME=1089045008
DATA_DIR=/home/data1/mwa_download
HOST=localhost
PORT=8001

if [[ -e ${OBS_NAME}_flags.zip ]]
then
      unzip ${OBS_NAME}_flags.zip
      FLAGFILES="-flagfiles ${OBS_NAME}_%%.mwaf"
fi

while getopts "d:o:h?" opt
do
	case "$opt" in
		d)
			DATA_DIR="$OPTARG"
			;;
		o)
			OBS_NAME="$OPTARG"
			;;
		[h?])
			print_usage
			exit 0
			;;
		:)
			print_usage 1>&2
			exit 1
	esac
done

now="$(date -u +%F_%T)"

# Replace the placeholder variables (i.e., transition from a Logical Graph
# Template into a Logical Graph).
# Then translate into a physical graph template, partition, etc, and finally submit
cat ${lg_file} | sed "s;DATA_DIR;${DATA_DIR};g" | sed "s;OBS_NAME;${OBS_NAME};g" | sed "s;FLAGFILES;${FLAGFILES};g" > "${lg_dir}/mwa_flagging_${OBS_NAME}.json" \
	| dlg unroll-and-partition -L "${lg_dir}/mwa_flagging_${OBS_NAME}.json" | dlg map -N "${HOST},${HOST}" -i 1 | dlg submit -H ${HOST} -p ${PORT} -s "${OBS_NAME}_${now}"
