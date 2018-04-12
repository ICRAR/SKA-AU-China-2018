# SKA-AU-China-2018 - **hwswcodesign**

## WP 4 – Hardware/software co-design
### Deliverable
Set up the workload characterisation framework on SHAO cluster that will inform the future hardware/software co-design work using an established algorithm (e.g. gridding, calibration).

### Achievements
Installed and configured a time series database (openTSDB) a metric capturing software package (glances) and some benchmark grpahs to load the cluster with a synthetic workload. The framework is monitoring the machines directly without the need to modify any code. Thus it will capture whatever workload is thrown on the cluster. 

### Left out 
When running glances with the default configuration, which essentially monitors everything possible, the process required 100% of one CPU most of the time. Thus this clearly would not scale very well. Thus we have enabled just a few things and the resulting load is quite low. 

We have concentrated on the implementation of monitoring CPU load, memory consumption and I/O and have skipped power monitring for now. 

We have also left out any feedback loop to DALiuGE or SLURM, which would be a whole project by itself. This would produce models for DALiuGE to use during scheduling and partitioning. The dynamic version of such models would very likely benefit from machine learning algorithms, which would then analyse the measurements collected during the latest run and update the models accordingly. 

The current system has quite obvious scalability issues and it would take a bit of work to analyse those in detail and find solutions for them. One obvious bottleneck is the currently single server database running on the login node. The other is that the number of events collected by DALiuGE for every single drop running in a multi-million node graph would be very big and thus might pose a scalability issue as well.

