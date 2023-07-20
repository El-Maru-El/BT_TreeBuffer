from unittest import TestCase
from current_implementation.test.is_proper_tree import assert_is_proper_tree
import time
from pathlib import Path
from current_implementation.create_comparable_string import create_string_from_int_with_byte_size
from current_implementation.new_buffer_tree import BufferTree
from bplus_tree.new_bplus_tree import BPlusTree
import random
from current_implementation.new_buffer_tree import write_leaf_block, read_leaf_block_elements_as_deque_from_filepath

FIND_INSERT_AGAIN = "FIXED_INPUT_INSERT_SEQ"
FIND_DELETE_AGAIN = "FIXED_INPUT_DELETE_SEQ"
insert_seq_file_path = r'C:\Users\marua\PycharmProjects\BT_TreeBuffer\benchmarking\test_broken_stuff\leaf_FIXED_INPUT_DELETE_SEQ'
delete_seq_file_path = r'C:\Users\marua\PycharmProjects\BT_TreeBuffer\benchmarking\test_broken_stuff\leaf_FIXED_INPUT_INSERT_SEQ'


# TODO Debug
import logging, sys

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
logger = logging.getLogger(__file__)
logger.setLevel(logging.DEBUG)

benchmark_name = Path(__file__).stem
byte_size = 79
numbers_to_create = 30_000
numbers_to_delete = 4_000


class TestRandomisedInsert(TestCase):

# Element: Standard example (see reference... somewhere)

    def test_execute_benchmark(self):


        buffer_tree = create_buffer_tree()
        bpl_tree = create_bplus_tree()

        insert_seq, del_seq = create_insert_and_delete_sequence()
        # insert_seq = read_leaf_block_elements_as_deque_from_filepath(insert_seq_file_path)
        # del_seq = read_leaf_block_elements_as_deque_from_filepath(delete_seq_file_path)

        # write_leaf_block(FIND_INSERT_AGAIN, insert_seq)
        # write_leaf_block(FIND_DELETE_AGAIN, del_seq)


        print(f'Starting with {benchmark_name}')
        # trees = [buffer_tree, bpl_tree]
        trees = [buffer_tree]

        for tree in trees:
            print(f'Starting benchmark for {tree.__class__}')
            tree.start_tracking_handler()

            # TODO Debug stuff
            start_time = time.perf_counter()
            debug_counter = 0

            for element in insert_seq:
                tree.insert_to_tree(element)
                debug_counter += 1
                if debug_counter % 10000 == 0:
                    logger.debug(f'Done with {debug_counter} inserts. Took {time.perf_counter() - start_time}s')

            if type(tree) == BufferTree:
                logger.debug('Done with inserts for buffer tree')

            # TODO Debug block here
            tree.flush_all_buffers()
            logger.debug('Done flushing')
            assert_is_proper_tree(self, tree)
            logger.debug('Is a proper tree, no mistakes made')
            # TODO Debug block above

            debug_counter = 0
            for element in del_seq:
                tree.delete_from_tree(element)
                debug_counter += 1
                if debug_counter % 1000 == 0:
                    logger.debug(f'Done with {debug_counter} deletes.  Took {time.perf_counter() - start_time}s')

            if type(tree) == BufferTree:
                logger.debug(f'Starting flush')
                tree.flush_all_buffers()

            tree.stop_tracking_handler(benchmark_name)

        print(f'Done with {benchmark_name}')


def create_insert_and_delete_sequence() -> (list, list):
    insert_seq, existing_ints_list = create_insert_sequence([])
    del_seq, existing_ints_list = create_delete_sequence(existing_ints_list)
    return insert_seq, del_seq


def create_delete_sequence(existing_ints_list: list):
    # Delete EVERYTHING
    amount_to_delete = len(existing_ints_list)

    random.shuffle(existing_ints_list)

    int_delete_sequence = []
    for _ in range(amount_to_delete):
        int_delete_sequence.append(existing_ints_list.pop(-1))

    string_del_sequence = [create_string_from_int_with_byte_size(i, byte_size) for i in int_delete_sequence]
    return string_del_sequence, existing_ints_list


# def create_insert_sequence(current_ints_list: list):
#     current_ints_set = set(current_ints_list)
#     random_max = 1_000_000_000
#
#     insert_list = []
#     for _ in range(numbers_to_create):
#         random_int = random.randint(1, random_max)
#         current_ints_set.add(random_int)
#         # insert_list.append(create_string_from_int_with_byte_size(random_int, byte_size))
#
#     insert_list = [create_string_from_int_with_byte_size(i, byte_size) for i in current_ints_set]
#     random.shuffle(insert_list)
#
#     current_ints_list = list(current_ints_set)
#     return insert_list, current_ints_list

# TODO This is ascending, not random! Debugging....
def create_insert_sequence(current_ints_list: list):
    current_ints_set = set(current_ints_list)
    random_max = 1_000_000_000

    insert_list = []
    for i in range(numbers_to_create):
        random_int = i
        current_ints_set.add(random_int)
        insert_list.append(create_string_from_int_with_byte_size(i, byte_size))
        # insert_list.append(create_string_from_int_with_byte_size(random_int, byte_size))

    # insert_list = [create_string_from_int_with_byte_size(i, byte_size) for i in current_ints_set]
    random.shuffle(insert_list)

    current_ints_list = list(current_ints_set)
    return insert_list, current_ints_list


def create_buffer_tree():
    buffer_tree = BufferTree(B_buffer=41, M=349)
    # -> (a, b) = (2, 8)
    return buffer_tree


def create_bplus_tree():
    bpl_tree = BPlusTree(order=48, max_leaf_size=50)
    return bpl_tree


if __name__ == '__main__':
    logger.debug('Hello')
    execute_benchmark()

