# SKA-AU-China-2018 - **datamanagement**

## WP 3 – Data Management
Deliverable - (a) An NGAS cluster is running inside SHAO cluster that manages all data - including archive, ingest cache, processing cache, and data subscriptions. (b) An IVOA compliant interface that allows users to access visibilities and images (cubes) using IVOA tools and Python API. MWA ASVO.

### Useful links
* NGAS: http://ngas.readthedocs.io/en/latest/
* CASDA VO Tools: https://github.com/csiro-rds/casda_vo_tools
* PostgreSQL: https://www.postgresql.org/
* Aladin: http://aladin.u-strasbg.fr/AladinDesktop/
* TopCat: http://www.star.bris.ac.uk/~mbt/topcat/

### Day 1 Targets
1. Install and configure NGAS instance at SHAO - Done
2. Create PostgeSQL data - DOne
3. Install CASDA VO Tools
4. Describe how catalogues will be accessed - Done
5. Define how trigger will be sent to pipeline to notify new data available
6. Define how pipeline will access data from a new observation

### Interfaces

#### How catalogues will be accessed
1. TopCat access TAP server at http://202.127.29.97:8888/casda_vo_tools/tap
2. Query: select * from ivoa.obscore where dataproduct_subtype = 
3. Select row with appropriate catalogue
4. Click Access URL to download catalogue

### How the pipeline will be triggered by NGAS

It was agreed that:

1. Each different pipeline will provide a simple script that can be invoked by NGAS to kick off the execution of the corresponding pipeline.
2. A piece of code attached to NGAS will be responsible for determining when all the data needed by a given pipeline is available and invoking the script.
3. For the case of the source extraction pipeline, this code will be developed by WP3, and the file ID for the individual image that needs to be source-extracted will be passed down as an argument.
3. For the case of the MWA imagining pipeline, this code will be developed by WP1, and the MWA observation ID and the list of all file IDS for that observation will be passed down as an argument.

### How data will be pulled from NGAS by the pipeline
1. wget http://202.127.97.97:7777/RETRIEVE?file_id=<file_id>

### How data will be pushed into NGAS by the pipeline

Data will be pushed using the following command

```
 wget --post-file <filename> --header 'Content-Type: <content-type>' http://202.127.97.97:7777/ARCHIVE?filename=<filename>
```

This should be repeated for each file that the pipeline needs to store into NGAS.
These are the currently agreed types:

 * *Source extraction pipeline*: A VOTable XML document of type `application/x-votable+xml`
