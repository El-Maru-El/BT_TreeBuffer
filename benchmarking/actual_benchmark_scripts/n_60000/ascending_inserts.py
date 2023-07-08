from current_implementation.create_comparable_string import create_string_from_int_with_byte_size
from current_implementation.new_buffer_tree import BufferTree
from bplus_tree.new_bplus_tree import BPlusTree

benchmark_name = 'OUTDATED_ascending_inserts_60k'


# Element: Standard example (see reference... somewhere)
def execute_benchmark():
    insert_seq = create_insert_sequence()
    buffer_tree = create_buffer_tree()
    bpl_tree = create_bplus_tree()

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


def create_insert_sequence():
    numbers_to_create = 60_000
    byte_size = 79

    insert_list = []
    for i in range(numbers_to_create):
        the_int = i
        insert_list.append(create_string_from_int_with_byte_size(the_int, byte_size))

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

