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
