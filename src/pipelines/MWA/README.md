To execute MWA calibration and imaging pipeline run

./submit_mwa_graph.sh -j <NCPUS> -d <data_dir>  -o <obs_name>

-j <NCPUS>: number of CPUs to use (single node)
-d <data_dir>: directory where all the data resides (or will reside)
-o <obs_name>: observation name

Data (3C444) directory: /home/data1/mwa_download/1089045008

./submit_mwa_graph_flagging.sh

-d <data_dir>:    Provide the directory where all the data resides (or will reside)
-o <obs_name>: Provide the observation name
-j <cpus>: how many cpus will be used
-H <host>: which host will be used to deploy
-p <port>: provied the port
 

