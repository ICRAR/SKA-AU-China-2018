"""

"""
import argparse
import json
import logging

from dlg.droputils import get_roots
from dlg.manager.client import DataIslandManagerClient

from build_graph_common import AbstractBuildGraph
from wait_for_file_drop import WaitForFile

NODE_ID = '192.168.0.101'
LOGGER = logging.getLogger(__name__)


class BuildGraph(AbstractBuildGraph):
    def __init__(self, **kwargs):
        super(BuildGraph, self).__init__(**kwargs)
        self._host_id = kwargs['host']

    def build(self):
        memory_drop_01 = self.create_memory_drop(
            node_id=NODE_ID,
        )
        memory_drop_02 = self.create_memory_drop(
            node_id=NODE_ID,
        )
        memory_drop_03 = self.create_memory_drop(
            node_id=NODE_ID,
        )
        bash_drop = self.create_bash_shell_app(
            node_id=NODE_ID,
            command='source /home/ska_au_china_2018/python-test/bin/activate'
                    ' && cd /home/ska_au_china_2018/SKA-AU-China-2018/src/pipelines'
                    ' && python trigger_pipeline.py '
                    ' --imglist /home/ska_au_china_2018/SKA-AU-China-2018/src/pipelines/Simple_Selavy_Test/selavy-fits-list.txt '
                    ' --nodelist 192.168.0.101,192.168.0.102,192.168.0.103,192.168.0.104 '
                    ' --masterport 8002'
        )
        bash_drop.addInput(memory_drop_01)
        bash_drop.addOutput(memory_drop_02)

        wait_for_file = self.create_app(
            NODE_ID,
            self.get_module_name(WaitForFile),
            'app_wait_for_file',
            root_directory='/tmp',
            starts_with='total.'
        )
        wait_for_file.addInput(memory_drop_02)
        wait_for_file.addOutput(memory_drop_03)


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
