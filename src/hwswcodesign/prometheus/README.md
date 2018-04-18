# Prometheus monitoring framework

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
correlate the results with the OS metrics. In Grafana this can be achieved by
using the annotation feature, which is also based on a data source. Later, the
data collected can be used to optimise the partitioning and scheduling of
DALiuGE graphs.

INSTALLATION:
For test purposes the whole system can be deployed in docker containers using
the command 'docker_compose up' in the prometheus sub-directory. Before running
that command you will need to adjust the file prometheus/prometheus.yml to
include the IP address of the host running the containers. Please refer to the
description in that file. When executing the docker_compose command this will
first build the images and then start the containers. If successful you can
connect to the Grafana container using the url http://localhost:3000. The
default username and password is admin/admin. In Grafana import the dashboard
file dashboardDocker.json from the subdirectory prometheus/grafana/dashboards.
You will also need to add the Prometheus data source, which is running in
another container. Use Prometheus as the datasource name and the URL is
http://<host-ip>:9090. Once that is done the Dashboard should just work and show
the metrics of the Docker container running the collector (node_exporter).

For a more realistic deployment node-exporters can be launched on multiple
Linux machines. After adjusting the prometheus.yml file to point to the various
node_exporter instances and restarting the containers you will need to create a
new Dashboard using the file dashboardLinux.json. This is required because the
metrics of a standard Linux machine are different from the Docker ones and thus
the diagrams of the dashboardDocker.json would not work. The dashboards are just
a starting point. The node_exporter is collecting many different metrics and
thus a lot of graphs could be produced.
