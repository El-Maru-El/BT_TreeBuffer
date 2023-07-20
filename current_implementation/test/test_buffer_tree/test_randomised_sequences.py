import os.path
import unittest
from current_implementation.create_comparable_string import create_string_from_int_with_byte_size
from current_implementation.new_buffer_tree import *
from current_implementation.test.is_proper_tree import assert_is_proper_tree
from current_implementation.constants_and_helpers import BROKEN_LEAVES_DIR
import random

byte_size = 10
numbers_to_create_seq_length = 1_000
numbers_to_del_seq_length = 200
num_of_repetitions = 6
max_random_number = 1_000_000

DEBUG_SAVE_SEQUENCES = False
DEBUG_LOAD_SEQUENCES = False
if DEBUG_LOAD_SEQUENCES and DEBUG_SAVE_SEQUENCES:
    raise ValueError("Wrongly configured the loading/saving of pre-made sequences")


class TestRandomizedSequences(unittest.TestCase):

    def execute_randomised_test(self):
        buffer_tree = self.create_buffer_tree()

        alternating_ins_del_sequences, expected_elements_list = self.create_insert_and_delete_sequences()
        buffer_tree = buffer_tree
        insert_mode = True

        for (idx, sequence) in enumerate(alternating_ins_del_sequences):
            print(f'Executing {idx+1}th sequence. Insert Mode: {insert_mode}')
            if insert_mode:
                for el_idx, element in enumerate(sequence):
                    buffer_tree.insert_to_tree(element)
            else:
                for el_idx, element in enumerate(sequence):
                    buffer_tree.delete_from_tree(element)

            insert_mode = not insert_mode

        buffer_tree.flush_all_buffers()
        assert_is_proper_tree(self, buffer_tree)

    def test_several_randomised_insert_and_del_sequences(self):
        num_tests = 10
        for i in range(num_tests):
            print(f'Execute {i+1}th out of {num_tests} randomised tests')
            self.execute_randomised_test()

    @staticmethod
    def create_insert_and_delete_sequences() -> (list, list):
        if DEBUG_LOAD_SEQUENCES:
            alternating_sequences = TestRandomizedSequences.debug_load_sequences(2 * num_of_repetitions)
            existing_ints_set = TestRandomizedSequences.existent_ints_from_sequence_list(alternating_sequences)
        else:
            existing_ints_set = set()
            alternating_sequences = []
            for i in range(num_of_repetitions):
                insert_seq = TestRandomizedSequences.create_insert_sequence(existing_ints_set)
                del_seq = TestRandomizedSequences.create_delete_sequence(existing_ints_set)
                alternating_sequences.append(insert_seq)
                alternating_sequences.append(del_seq)

        if DEBUG_SAVE_SEQUENCES:
            TestRandomizedSequences.debug_save_sequences(alternating_sequences)

        existing_string_elements_list = TestRandomizedSequences.create_sorted_elements_list_from_int_set(existing_ints_set)
        return alternating_sequences, existing_string_elements_list

    @staticmethod
    def existent_ints_from_sequence_list(sequence_list):
        insert_mode = True
        existing_ints_set = set()
        for sequence in sequence_list:
            if insert_mode:
                [existing_ints_set.add(i) for i in sequence]
            else:
                [existing_ints_set.remove(i) for i in sequence]
            insert_mode = not insert_mode

        return existing_ints_set

    @staticmethod
    def create_sorted_elements_list_from_int_set(existing_ints_set: set) -> list:
        sorted_ints_list = sorted(list(existing_ints_set))
        existing_elements_list = [create_string_from_int_with_byte_size(i, byte_size) for i in sorted_ints_list]
        return existing_elements_list

    @staticmethod
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

    @staticmethod
    def create_insert_sequence(current_ints_set: set):

        insert_list = []
        for _ in range(numbers_to_create_seq_length):
            i = random.randint(1, max_random_number)
            current_ints_set.add(i)
            insert_list.append(create_string_from_int_with_byte_size(i, byte_size))

        return insert_list

    @staticmethod
    def create_buffer_tree():
        buffer_tree = BufferTree(B_buffer=41, M=349)
        # -> (a, b) = (2, 8)
        return buffer_tree

    @staticmethod
    def get_broken_sequence_file_path(idx):
        dir_path = BROKEN_LEAVES_DIR
        this_script_name = Path(__file__).stem
        file_name = f'{this_script_name}_{idx}.txt'
        return os.path.join(dir_path, file_name)

    @staticmethod
    def debug_save_sequences(all_sequences):
        for idx, sequence in enumerate(all_sequences):
            file_path = TestRandomizedSequences.get_broken_sequence_file_path(idx)
            write_leaf_elements_to_file_path(file_path, sequence)

    @staticmethod
    def debug_load_sequences(amount_of_sequences):
        all_sequences = []
        for idx in range(amount_of_sequences):
            file_path = TestRandomizedSequences.get_broken_sequence_file_path(idx)
            sequence = read_leaf_block_elements_as_deque_from_filepath(file_path)
            all_sequences.append(sequence)

        return all_sequences

