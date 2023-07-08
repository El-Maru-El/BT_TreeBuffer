from current_implementation.create_comparable_string import create_string_from_int_with_byte_size
from current_implementation.new_buffer_tree import BufferTree
from bplus_tree.new_bplus_tree import BPlusTree
import random

benchmark_name = 'OUTDATED_insert_all_delete_all_60k'
byte_size = 79


# Element: Standard example (see reference... somewhere)
def execute_benchmark():
    buffer_tree = create_buffer_tree()
    bpl_tree = create_bplus_tree()

    insert_seq = create_insert_sequence()

    print(f'Starting with {benchmark_name}')
    trees = [buffer_tree, bpl_tree]
    for tree in trees:
        print(f'Starting benchmark for {tree.__class__}')
        tree.start_tracking_handler()
        for element in insert_seq:
            tree.insert_to_tree(element)

        if type(tree) == BufferTree:
            tree.flush_all_buffers()

        tree.stop_tracking_handler(benchmark_name)

    print(f'Done with {benchmark_name}')


def create_insert_and_delete_sequence() -> (list, list):
    existing_ints_in_tree = set()
    create_insert_sequence(existing_ints_in_tree)


def create_delete_sequence(existing_ints_in_tree: set):
    amount_to_delete = len(existing_ints_in_tree)
    existing_ints_list = list(existing_ints_in_tree)
    random.shuffle(existing_ints_list)

    int_delete_sequence = []
    for _ in range(amount_to_delete):
        int_delete_sequence.append(existing_ints_list.pop(-1))

    string_del_sequence = [create_string_from_int_with_byte_size(i, byte_size) for i in int_delete_sequence]
    return string_del_sequence


def create_insert_sequence(current_ints_list: set):
    random_max = 1_000_000_000
    numbers_to_create = 60_000

    insert_list = []
    for _ in range(numbers_to_create):
        random_int = random.randint(1, random_max)
        current_ints_list.add(random_int)
        insert_list.append(create_string_from_int_with_byte_size(random_int, byte_size))

    return insert_list


def create_buffer_tree():
    buffer_tree = BufferTree(B_buffer=41, B_leaf=50, M=349)
    return buffer_tree


def create_bplus_tree():
    bpl_tree = BPlusTree(order=48, max_leaf_size=50)
    return bpl_tree


def how_many_duplicates(some_list):
    from collections import defaultdict
    amount_per_i = defaultdict(int)
    for i in some_list:
        amount_per_i[i] += 1

    print('Duplicates:')
    found_some = False
    for i, v in amount_per_i.items():
        if v > 1:
            print(f'String {i}: {v} times')
            found_some = True

    if not found_some:
        print('No dupes :)')


if __name__ == '__main__':
    execute_benchmark()

