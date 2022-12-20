import os
import current_implementation
import time
from pathlib import Path
import shutil


WORKING_DIR = os.path.dirname(current_implementation.__file__)
RESOURCES_DIR = os.path.join(WORKING_DIR, 'resource_data')
NODES_DIR = os.path.join(RESOURCES_DIR, 'nodes_collection')
LEAVES_DIR = os.path.join(RESOURCES_DIR, 'leaves_collection')
NODE_STRING = 'node_'
NODE_INFORMATION_FILE_STRING = 'data.txt'
TIMESTAMP_FORMAT = '%Y_%m_%d-%H_%M_%S_%f'
BLOCK_STRING = 'block_'
LEAF_STRING = 'leaf_'
SORTED_STRING = 'sorted_'
# TODO Which file extension to use? CSV? TXT?
FILE_EXTENSION = ''

node_counter = 0

sorted_counter = 0

leaf_counter = 0


def clean_up_and_initialize_resource_directories():
    delete_all_tree_data()
    Path(NODES_DIR).mkdir(parents=True, exist_ok=True)
    Path(LEAVES_DIR).mkdir(parents=False, exist_ok=True)


def get_new_node_id():
    global node_counter
    node_counter += 1
    return str(node_counter)


def generate_new_buffer_block_id(amount_previous_blocks):
    return str(amount_previous_blocks + 1)


def get_new_sorted_id():
    global sorted_counter
    sorted_counter += 1
    return str(sorted_counter)


def generate_new_leaf_id():
    global leaf_counter
    leaf_counter += 1
    return str(leaf_counter)


# Returns the node_id, by which the rest of file-paths can be reconstructed
def generate_new_node_dir():
    new_node_id = get_new_node_id()
    generate_node_dir_for_id(new_node_id)
    return new_node_id


def generate_node_dir_for_id(node_id):
    new_node_dir = get_node_dir_path_from_id(node_id)
    new_node_dir.mkdir(parents=False, exist_ok=True)


# Returns Node directory path
def get_node_dir_path_from_id(node_id):
    node_dir_name = nodes_dir_name_from_id(node_id)
    return Path(os.path.join(NODES_DIR, node_dir_name))


# Returns Node directory name
def nodes_dir_name_from_id(timestamp):
    return NODE_STRING + timestamp


# Returns node meta information file path
def node_information_file_path_from_id(node_id):
    return os.path.join(get_node_dir_path_from_id(node_id), NODE_INFORMATION_FILE_STRING)


def get_current_timer_as_float() -> float:
    return time.perf_counter()


# Returns buffer file name
def buffer_file_name_from_id(buffer_block_id):
    return BLOCK_STRING + buffer_block_id


# Returns buffer file path
def get_buffer_file_path_from_ids(node_id, buffer_block_id):
    return Path(os.path.join(get_node_dir_path_from_id(node_id), buffer_file_name_from_id(buffer_block_id)))


# Returns leaf file name
def leaf_file_name_from_id(leaf_id):
    return LEAF_STRING + leaf_id


# Returns sorted file name
def sorted_file_name_from_id(sorted_id):
    return SORTED_STRING + sorted_id


# Returns sorted file path
def get_sorted_file_path_from_ids(node_id, sorted_id):
    return Path(os.path.join(get_node_dir_path_from_id(node_id), sorted_file_name_from_id(sorted_id)))


# Returns life file path
def get_leaf_file_path_from_id(leaf_id):
    return Path(os.path.join(LEAVES_DIR, leaf_file_name_from_id(leaf_id)))


# https://stackoverflow.com/questions/6340351/iterating-through-list-of-list-in-python
# Returns the elements of all lists within a super-list in order
def traverse_lists_in_list(super_list):
    for sublist in super_list:
        for element in sublist:
            yield element


def delete_all_tree_data():
    if os.path.exists(RESOURCES_DIR):
        shutil.rmtree(RESOURCES_DIR)


def delete_several_buffer_files_with_ids(node_id, buffer_block_ids):
    for buffer_block_id in buffer_block_ids:
        delete_buffer_file_with_id(node_id, buffer_block_id)


def delete_buffer_file_with_id(node_id, buffer_block_id):
    buffer_file_path = get_buffer_file_path_from_ids(node_id, buffer_block_id)
    os.remove(buffer_file_path)


def get_file_reader_for_sorted_filepath_with_ids(node_id, sorted_id):
    sorted_filepath = get_sorted_file_path_from_ids(node_id, sorted_id)
    return open(sorted_filepath, 'r')


def delete_sorted_files_with_ids(node_id, sorted_id):
    for sorted_id in sorted_id:
        delete_sorted_file_with_id(node_id, sorted_id)


def delete_sorted_file_with_id(node_id, sorted_id):
    sorted_filepath = get_sorted_file_path_from_ids(node_id, sorted_id)
    os.remove(sorted_filepath)


def delete_old_leaves(leaf_ids):
    for leaf_id in leaf_ids:
        leaf_file_path = get_leaf_file_path_from_id(leaf_id)
        os.remove(leaf_file_path)


def delete_filepath(file_path):
    os.remove(file_path)


# String representations of node and buffer elements:
TRUE_STRING = 'T'
FALSE_STRING = 'F'
SEP = ';'


def append_to_sorted_buffer_elements_file(node_id, sorted_id, elements: list):
    sorted_filepath = get_sorted_file_path_from_ids(node_id, sorted_id)
    with open(sorted_filepath, 'a') as f:
        elements_as_str = [element.to_output_string() for element in elements]
        f.writelines(elements_as_str)
