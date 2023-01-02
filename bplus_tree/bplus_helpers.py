import sys
from pathlib import Path
import os
import bplus_tree
import shutil


DUMMY_INFINITY_STRING = 'THIS_IS_INFINITY'

WORKING_DIR = os.path.dirname(bplus_tree.__file__)
NODES_DIR = os.path.join(WORKING_DIR, 'nodes_collection')
NODE_STRING = 'node_'


TRUE_STRING = 'T'
FALSE_STRING = 'F'
SEP = ';'

node_counter = 0


def get_new_node_id():
    global node_counter
    node_counter += 1
    return str(node_counter)


def clean_up_and_initialize_resource_directories():
    global node_counter
    node_counter = 0
    delete_all_tree_data()
    Path(NODES_DIR).mkdir(parents=True, exist_ok=True)


def get_file_path_for_node_id(node_id):
    return os.path.join(NODES_DIR, get_node_file_name(node_id))


def get_node_file_name(node_id):
    return f'{NODE_STRING}_{node_id}_data.txt'


def get_max_int():
    return sys.maxsize


def get_dummy_infinity_child():
    return DUMMY_INFINITY_STRING


def delete_all_tree_data():
    if os.path.exists(NODES_DIR):
        shutil.rmtree(NODES_DIR)


def delete_node_data_from_ext_memory(node_id):
    file_path = get_file_path_for_node_id(node_id)
    os.remove(file_path)


