from pathlib import Path
import random
from current_implementation.create_comparable_string import create_string_from_int_with_byte_size
from current_implementation.new_buffer_tree import BufferTree
from bplus_tree.new_bplus_tree import BPlusTree

benchmark_name = Path(__file__).stem
byte_size = 79
numbers_to_create_seq_length = 55
num_of_repetitions = 1090
random_max = 1_000_000


# Element: Standard example (see reference... somewhere)
def execute_benchmark():
    buffer_tree = create_buffer_tree()
    bpl_tree = create_bplus_tree()

    insert_sequences = create_insert_and_delete_sequences()
    trees = [buffer_tree, bpl_tree]
    print(f'Starting with {benchmark_name}')

    for tree in trees:
        print(f'Starting benchmark for {tree.__class__}')
        tree.start_tracking_handler()

        for sequence in insert_sequences:
            for element in sequence:
                tree.insert_to_tree(element)

        if type(tree) == BufferTree:
            tree.flush_all_buffers()

        tree.stop_tracking_handler(benchmark_name)

    print(f'Done with {benchmark_name}')


def create_insert_and_delete_sequences() -> list:
    existing_ints_list = []
    # insert-seq, del-seq, insert-seq, del-seq
    all_insert_sequences = []
    for i in range(num_of_repetitions):
        insert_seq = create_insert_sequence()
        all_insert_sequences.append(insert_seq)

    return all_insert_sequences


def create_insert_sequence():
    int_list = []
    for _ in range(numbers_to_create_seq_length):
        int_list.append(random.randint(1, random_max))

    int_list.sort()

    string_insert_list = [create_string_from_int_with_byte_size(i, byte_size) for i in int_list]

    return string_insert_list


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

