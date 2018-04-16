The Prometheus (https://prometheus.io) framework is an open source monitoring
solution. It integrates well with the time-series visualisation tool
Grafana (http://grafana.com) and also with a number of backend data bases.
Prometheus also comes with a pluggable architecture to capture data from a
arbitrary sources. A built-in data capturer is the node_exporter
(https://github.com/prometheus/node_exporter), which reads a large number of
metrics from OS provided logging services. By far the most complete coverage is
provided for Linux, but BSD based \*ix based systems like Mac OSX are also
covered.
This project uses the parts described above to construct a monitoring system
tailored for clusters running DALiuGE. Starting point is passive monitoring of
the OS provided metrics.
Next steps are to design a system to monitor the DALiuGE drops directly and
correlate the results with the OS metrics. This data can then be used to
optimise the partitioning and scheduling of DALiuGE graphs.
