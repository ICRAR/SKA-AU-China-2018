1. The MWA observation data retrieval is split into 2 steps:

    * Query NGAS to get the list of files that belongs to the specified
      ObsID (observation ID):

      ```
      ./query_mwa_obsid.py -i <obsid>
      ```

    * Then utilize the `ngas-get-files.py` script to do the data retrieval
      from NGAS:

      ```
      ../ngas-get-files.py -F <obsid>.list -o <obsid>.list
      ```

2. To execute MWA calibration and imaging pipeline run:

    ```
    ./submit_mwa_graph.sh -j <NCPUS> -d <data_dir>  -o <obs_name>

    -j <NCPUS>: number of CPUs to use (single node)
    -d <data_dir>: directory where all the data resides (or will reside)
    -o <obs_name>: observation name
    ```

3. Data (3C444) directory: `/home/data1/mwa_download/1089045008`

    ```
    ./submit_mwa_graph_flagging.sh

    -d <data_dir>: Provide the directory where all the data resides (or will reside)
    -o <obs_name>: Provide the observation name
    -j <cpus>: how many cpus will be used
    -H <host>: which host will be used to deploy
    -p <port>: provied the port
    ```
