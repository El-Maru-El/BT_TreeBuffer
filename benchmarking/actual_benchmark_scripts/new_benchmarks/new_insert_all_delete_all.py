from pathlib import Path
from current_implementation.create_comparable_string import create_string_from_int_with_byte_size
from current_implementation.new_buffer_tree import BufferTree
from bplus_tree.new_bplus_tree import BPlusTree
import random
import datetime

benchmark_name = Path(__file__).stem
byte_size = 79
numbers_to_create = 500_000
numbers_to_delete = 500_000


# Element: Standard example (see reference... somewhere)
def execute_benchmark():
    buffer_tree = create_buffer_tree()
    bpl_tree = create_bplus_tree()

    insert_seq, del_seq = create_insert_and_delete_sequence()

    print(f'Starting with {benchmark_name}')
    trees = [buffer_tree, bpl_tree]

    for tree in trees:
        print(f'{datetime.datetime.now()}: Starting benchmark for {tree.__class__}')
        tree.start_tracking_handler()

        for element in insert_seq:
            tree.insert_to_tree(element)

        for element in del_seq:
            tree.delete_from_tree(element)

        if type(tree) == BufferTree:
            tree.flush_all_buffers()

        tree.stop_tracking_handler(benchmark_name)

    print(f'Done with {benchmark_name}')


def create_insert_and_delete_sequence() -> (list, list):
    insert_seq, existing_ints_list = create_insert_sequence()
    del_seq, existing_ints_list = create_delete_sequence(existing_ints_list)
    return insert_seq, del_seq


def create_delete_sequence(existing_ints_list: list):
    random.shuffle(existing_ints_list)

    string_del_sequence = []
    for _ in range(numbers_to_delete):
        string_del_sequence.append(create_string_from_int_with_byte_size(existing_ints_list.pop(-1), byte_size))

    return string_del_sequence, existing_ints_list


def create_insert_sequence():
    int_list = [i for i in range(numbers_to_create)]
    random.shuffle(int_list)
    insert_list = [create_string_from_int_with_byte_size(i, byte_size) for i in int_list]

    return insert_list, int_list


def create_buffer_tree():
    b_buffer = 41
    b_leaf = 50
    M = 855
    buffer_tree = BufferTree(B_buffer=b_buffer, B_leaf=b_leaf, M=M)
    return buffer_tree


def create_bplus_tree():
    bpl_tree = BPlusTree(order=48, max_leaf_size=50)
    return bpl_tree


if __name__ == '__main__':
    execute_benchmark()

