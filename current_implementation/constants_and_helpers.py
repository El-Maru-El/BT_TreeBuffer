import os
import current_implementation
from datetime import datetime
from pathlib import Path
import shutil


WORKING_DIR = os.path.dirname(current_implementation.__file__)
NODES_DIR = os.path.join(WORKING_DIR, 'nodes_collection')
NODE_STRING = 'node_'
NODE_INFORMATION_FILE_STRING = 'data.txt'
TIMESTAMP_FORMAT = '%Y_%m_%d-%H_%M_%S_%f'
BLOCK_STRING = 'block_'
LEAF_STRING = 'leaf_'
# TODO Which file extension to use? CSV? TXT?
FILE_EXTENSION = ''


# Returns the timestamp, by which the rest can be reconstructed
def generate_new_nodes_dir():
    timestamp = get_current_timestamp()
    new_node_dir = get_node_dir_path_from_timestamp(timestamp)

    new_node_dir.mkdir(parents=True, exist_ok=False)

    return timestamp


# Returns Node directory path
def get_node_dir_path_from_timestamp(node_timestamp):
    node_dir_name = nodes_dir_name_from_timestamp(node_timestamp)
    return Path(os.path.join(NODES_DIR, node_dir_name))


# Returns Node directory name
def nodes_dir_name_from_timestamp(timestamp):
    return NODE_STRING + timestamp


# Returns node meta information file path
def node_information_file_path_from_timestamp(timestamp):
    return os.path.join(get_node_dir_path_from_timestamp(timestamp), NODE_INFORMATION_FILE_STRING)


def get_current_timestamp():
    return datetime.now().strftime(TIMESTAMP_FORMAT)


# Returns buffer file name
def buffer_file_name_from_timestamp(timestamp):
    return BLOCK_STRING + timestamp


# Returns buffer file path
def get_buffer_file_path_from_timestamps(node_timestamp, buffer_timestamp):
    return Path(os.path.join(get_node_dir_path_from_timestamp(node_timestamp), buffer_file_name_from_timestamp(buffer_timestamp)))


# Returns leaf file name
def leaf_file_name_from_timestamp(timestamp):
    return LEAF_STRING + timestamp()


# Returns life file path
def get_leaf_file_path_from_timestamps(node_timestamp, leaf_timestamp):
    return Path(os.path.join(get_node_dir_path_from_timestamp(node_timestamp), leaf_file_name_from_timestamp(leaf_timestamp)))


# https://stackoverflow.com/questions/6340351/iterating-through-list-of-list-in-python
# Returns the elements of all lists within a super-list in order
def traverse_lists_in_list(super_list):
    for sublist in super_list:
        for element in sublist:
            yield element


def delete_all_nodes():
    shutil.rmtree(NODES_DIR)


# String representations of node and buffer elements:
IS_INTERNAL_STR = 'T'
IS_NOT_INTERNAL_STR = 'F'
SEP = ';'
