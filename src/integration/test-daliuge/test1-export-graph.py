"""

"""
import logging
import argparse
import getpass
import time
from abc import ABCMeta

from build_graph_common import AbstractBuildGraph
from dlg.droputils import get_roots
from dlg.manager.client import DataIslandManagerClient

LOGGER = logging.getLogger(__name__)


class BuildGraph(AbstractBuildGraph):
    def __init__(self, **kwargs):
        super(BuildGraph).__init__(**kwargs)
        self._host_id = kwargs['host']

    def build(self):
        start_drop = self.create_memory_drop(
            node_id= self._host_id,
        )
        end_drop = self.create_memory_drop(
            node_id= self._host_id,
        )
        bash_drop = self.create_bash_shell_app(
            node_id= self._host_id,
            command='echo "hello world"'
        )
        bash_drop.addInput(start_drop)
        bash_drop.addOutput(end_drop)


def build_and_deploy_graph(**kwargs):
    build_graph = BuildGraph(**kwargs)

    LOGGER.info('Connection to {0}:{1}'.format(kwargs['host'], kwargs['port']))
    client = DataIslandManagerClient(kwargs['host'], kwargs['port'], timeout=30)

    client.create_session(build_graph.session_id)
    client.append_graph(build_graph.session_id, build_graph.drop_list)
    client.deploy_session(build_graph.session_id, get_roots(build_graph.drop_list))


def main():
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
    parser = argparse.ArgumentParser(description='GW Training')
    parser.add_argument('host', help='host IP address')
    parser.add_argument('--port', type=int, default=8001, help='port number (default: 8001)')

    kwargs = vars(parser.parse_args())
    LOGGER.info(kwargs)

    build_and_deploy_graph(**kwargs)


if __name__ == '__main__':
    main()
