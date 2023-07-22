from pathlib import Path
from current_implementation.create_comparable_string import create_string_from_int_with_byte_size
from current_implementation.new_buffer_tree import BufferTree
from bplus_tree.new_bplus_tree import BPlusTree
import random
import datetime

benchmark_name = Path(__file__).stem
byte_size = 79
numbers_to_create_seq_length = 50
numbers_to_del_seq_length = 20
num_of_repetitions = 14_285
max_random_number = 999_999_999_999_999_999_999


# Element: Standard example (see reference... somewhere)
def execute_benchmark():
    buffer_tree = create_buffer_tree()
    bpl_tree = create_bplus_tree()

    insert_and_delete_sequences = create_insert_and_delete_sequences()
    trees = [buffer_tree, bpl_tree]
    insert_mode = True
    print(f'Starting with {benchmark_name}')

    for tree in trees:
        print(f'{datetime.datetime.now()}: Starting benchmark for {tree.__class__}')
        tree.start_tracking_handler()

        for sequence in insert_and_delete_sequences:
            if insert_mode:
                for element in sequence:
                    tree.insert_to_tree(element)
            else:
                for element in sequence:
                    tree.delete_from_tree(element)

            insert_mode = not insert_mode

        if type(tree) == BufferTree:
            tree.flush_all_buffers()

        tree.stop_tracking_handler(benchmark_name)

    print(f'Done with {benchmark_name}')


def create_insert_and_delete_sequences() -> list:

    existing_ints_set = set()
    alternating_sequences = []
    for i in range(num_of_repetitions):
        insert_seq = create_insert_sequence(existing_ints_set)
        del_seq = create_delete_sequence(existing_ints_set)
        alternating_sequences.append(insert_seq)
        alternating_sequences.append(del_seq)

    return alternating_sequences


def create_insert_sequence(current_ints_set: set):

    insert_list = []
    for _ in range(numbers_to_create_seq_length):
        i = random.randint(1, max_random_number)
        current_ints_set.add(i)
        insert_list.append(create_string_from_int_with_byte_size(i, byte_size))

    return insert_list


def create_delete_sequence(existing_ints_set: set):
    existing_ints_list = list(existing_ints_set)
    random.shuffle(existing_ints_list)

    int_delete_sequence = []
    for _ in range(numbers_to_del_seq_length):
        int_to_be_deleted = existing_ints_list.pop(-1)
        int_delete_sequence.append(int_to_be_deleted)
        existing_ints_set.remove(int_to_be_deleted)

    string_del_sequence = [create_string_from_int_with_byte_size(i, byte_size) for i in int_delete_sequence]

    return string_del_sequence


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

