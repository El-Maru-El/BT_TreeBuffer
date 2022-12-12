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
SORTED_STRING = 'sorted_'
# TODO Which file extension to use? CSV? TXT?
FILE_EXTENSION = ''

node_counter = 0


def get_new_node_id():
    global node_counter
    node_counter += 1
    return str(node_counter)


def generate_new_buffer_block_id(amount_previous_blocks):
    return str(amount_previous_blocks + 1)


# Returns the timestamp, by which the rest can be reconstructed
def generate_new_nodes_dir():
    timestamp = get_new_node_id()
    new_node_dir = get_node_dir_path_from_timestamp(timestamp)

    new_node_dir.mkdir(parents=True, exist_ok=False)

    return timestamp


# Returns Node directory path
def get_node_dir_path_from_timestamp(node_id):
    node_dir_name = nodes_dir_name_from_timestamp(node_id)
    return Path(os.path.join(NODES_DIR, node_dir_name))


# Returns Node directory name
def nodes_dir_name_from_timestamp(timestamp):
    return NODE_STRING + timestamp


# Returns node meta information file path
def node_information_file_path_from_timestamp(timestamp):
    return os.path.join(get_node_dir_path_from_timestamp(timestamp), NODE_INFORMATION_FILE_STRING)


# TODO The only thing we still need timestamps for is BufferElements. How to achieve they aren't the same?
def get_current_timestamp():
    return datetime.now().strftime(TIMESTAMP_FORMAT)


# Returns buffer file name
def buffer_file_name_from_timestamp(timestamp):
    return BLOCK_STRING + timestamp


# Returns buffer file path
def get_buffer_file_path_from_timestamps(node_id, buffer_block_id):
    return Path(os.path.join(get_node_dir_path_from_timestamp(node_id), buffer_file_name_from_timestamp(buffer_block_id)))


# Returns leaf file name
def leaf_file_name_from_timestamp(timestamp):
    return LEAF_STRING + timestamp()


# Returns sorted file name
def sorted_file_name_from_timestamp(timestamp):
    return SORTED_STRING + timestamp


# Returns sorted file path
def get_sorted_file_path_from_timestamps(node_id, sorted_timestamp):
    return Path(os.path.join(get_node_dir_path_from_timestamp(node_id), sorted_file_name_from_timestamp(sorted_timestamp)))


# Returns life file path
def get_leaf_file_path_from_timestamps(node_id, leaf_timestamp):
    return Path(os.path.join(get_node_dir_path_from_timestamp(node_id), leaf_file_name_from_timestamp(leaf_timestamp)))


# https://stackoverflow.com/questions/6340351/iterating-through-list-of-list-in-python
# Returns the elements of all lists within a super-list in order
def traverse_lists_in_list(super_list):
    for sublist in super_list:
        for element in sublist:
            yield element


def delete_all_nodes():
    if os.path.exists(NODES_DIR):
        shutil.rmtree(NODES_DIR)


def delete_several_buffer_files_with_timestamps(node_id, buffer_block_ids):
    for buffer_block_id in buffer_block_ids:
        delete_buffer_file_with_timestamp(node_id, buffer_block_id)


def delete_buffer_file_with_timestamp(node_id, buffer_block_id):
    buffer_file_path = get_buffer_file_path_from_timestamps(node_id, buffer_block_id)
    os.remove(buffer_file_path)


def get_file_reader_for_sorted_filepath(node_id, sorted_timestamp):
    sorted_filepath = get_sorted_file_path_from_timestamps(node_id, sorted_timestamp)
    return open(sorted_filepath, 'r')


def delete_sorted_files_with_timestamps(node_id, sorted_timestamps):
    for sorted_timestamp in sorted_timestamps:
        delete_sorted_file_with_timestamp(node_id, sorted_timestamp)


def delete_sorted_file_with_timestamp(node_id, sorted_timestamp):
    sorted_filepath = get_sorted_file_path_from_timestamps(node_id, sorted_timestamp)
    os.remove(sorted_filepath)


# String representations of node and buffer elements:
IS_INTERNAL_STR = 'T'
IS_NOT_INTERNAL_STR = 'F'
SEP = ';'


def append_to_sorted_buffer_elements_file(node_id, sorted_timestamp, elements: list):
    sorted_filepath = get_sorted_file_path_from_timestamps(node_id, sorted_timestamp)
    with open(sorted_filepath, 'a') as f:
        elements_as_str = [element.to_output_string() for element in elements]
        f.writelines(elements_as_str)


class SortedIDGenerator:
    def __init__(self):
        self.counter = 0

    def get_new_id(self):
        self.counter += 1
        return self.counter
