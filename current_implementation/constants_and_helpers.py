import os
import current_implementation
from datetime import datetime
from pathlib import Path
import shutil


WORKING_DIR = os.path.dirname(current_implementation.__file__)
NODES_DIR = os.path.join(WORKING_DIR, 'nodes_collection')
NODE_STRING = 'node_'
TIMESTAMP_FORMAT = '%Y_%m_%d-%H_%M_%S_%f'
BUFFERS_DIR_STRING = 'buffers'
BLOCK_STRING = 'block_'
# TODO Which file extension to use? CSV? TXT?
FILE_EXTENSION = ''


def generate_new_nodes_dir():
    new_dir_name = NODE_STRING + get_current_timestamp()
    new_node_dir = Path(os.path.join(NODES_DIR, new_dir_name))
    buffer_dir_for_node = get_buffer_dir_for_node(new_node_dir)

    buffer_dir_for_node.mkdir(parents=True, exist_ok=False)

    return new_node_dir


def get_buffer_dir_for_node(node_dir):
    return Path(os.path.join(node_dir, BUFFERS_DIR_STRING))


def get_current_timestamp():
    return datetime.now().strftime(TIMESTAMP_FORMAT)


def delete_all_nodes():
    shutil.rmtree(NODES_DIR)


def generate_buffer_file_name():
    return BLOCK_STRING+get_current_timestamp()


def write_buffer_block(file_path, elements):
    # TODO
    pass
