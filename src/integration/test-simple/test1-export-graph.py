"""

"""
import argparse
import json
import logging

from dlg.droputils import get_roots
from dlg.manager.client import DataIslandManagerClient

from build_graph_common import AbstractBuildGraph

NODE_ID = '192.168.0.101'
LOGGER = logging.getLogger(__name__)


class BuildGraph(AbstractBuildGraph):
    def __init__(self, **kwargs):
        super(BuildGraph, self).__init__(**kwargs)
        self._host_id = kwargs['host']

    def build(self):
        start_drop = self.create_memory_drop(
            node_id=NODE_ID,
        )
        end_drop = self.create_memory_drop(
            node_id=NODE_ID,
        )
        bash_drop = self.create_bash_shell_app(
            node_id=NODE_ID,
            command='echo "hello world"'
        )
        bash_drop.addInput(start_drop)
        bash_drop.addOutput(end_drop)


def build_and_deploy_graph(**kwargs):
    graph = BuildGraph(**kwargs)
    graph.build()

    LOGGER.info('Connection to {0}:{1}'.format(kwargs['host'], kwargs['port']))
    client = DataIslandManagerClient(kwargs['host'], kwargs['port'], timeout=30)

    client.create_session(graph.session_id)
    json_dumps = json.dumps(graph.drop_list, indent=2)
    LOGGER.info('json:\n{}'.format(json_dumps))
    client.append_graph(graph.session_id, json_dumps)
    client.deploy_session(graph.session_id, get_roots(graph.drop_list))


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
