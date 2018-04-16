#!/bin/bash
#use this script to submit MWA calibration & imaging pipeline to Dailuge
function print_usage {
	echo "$0 [-h | -?] [-j <NCPUS>] [-d <data_dir>]  [-o <obs_name>]"
	echo
	echo "-h, -?: Show this help"
	echo "-j <NCPUS>: Provide the number of CPUs to use"
	echo "-d <data_dir>: Provide the directory where all the data resides (or will reside)"
	echo "-o <obs_name>: Provide the observation name"
}

# Where are we?
lg_file=/home/ska_au_china_2018/SKA-AU-China-2018/src/pipelines/lg/mwa.json

# Handle command-line arguments
OBS_NAME=observation
DATA_DIR=.

while getopts "j:d:o:h?" opt
do
	case "$opt" in
		j)
		  NCPUS="$OPTARG"
			;;
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
sed "s|\${NCPUS}|${NCPUS}|g; s|\${DATA_DIR}|${DATA_DIR}|g; s|\${OBS_NAME}|${OBS_NAME}|g" "$lg_file" \
	| dlg unroll-and-partition | dlg map -N 202.127.29.97,202.127.29.97 -i 1 | dlg submit -s "${OBS_NAME}_${now}" -H 202.127.29.97 -p 8001
