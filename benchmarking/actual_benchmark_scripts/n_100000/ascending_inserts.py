from pathlib import Path
from current_implementation.create_comparable_string import create_string_from_int_with_byte_size
from current_implementation.new_buffer_tree import BufferTree
from bplus_tree.new_bplus_tree import BPlusTree

benchmark_name = Path(__file__).stem
numbers_to_create = 100_000


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
    byte_size = 79

    insert_list = []
    for i in range(numbers_to_create):
        the_int = i
        insert_list.append(create_string_from_int_with_byte_size(the_int, byte_size))

    return insert_list


def create_buffer_tree():
    b_buffer = 41
    b_leaf = 50
    M = 855
    buffer_tree = BufferTree(B_buffer=b_buffer, B_leaf=b_leaf, M=M)
    return buffer_tree


def create_bplus_tree():
    order = 48
    max_leaf_size = 50
    bpl_tree = BPlusTree(order=order, max_leaf_size=max_leaf_size)
    return bpl_tree


if __name__ == '__main__':
    execute_benchmark()

