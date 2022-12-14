from current_implementation.new_buffer_tree import *
from current_implementation.merge_sort import *
from collections import deque
from current_implementation.create_comparable_string import create_string_from_int
import unittest


class TestBasicStructure(unittest.TestCase):

    def setUp(self) -> None:
        delete_all_nodes()
        self.tree = self.create_dummy_tree()
        self.leaf_node = TreeNode(is_internal_node=False)
        self.max_elem_in_memory = self.tree.M
        # Now a tree is initialised and the directory for a leaf_node is initialised

    def test_compare_buffer_elements(self):
        element = 'Some_text'
        action = Action.INSERT
        timestamp = 'Arbitrary we dont care'
        first = BufferElement(element, action, timestamp)
        second = BufferElement(element, action, timestamp)
        self.assertEqual(first, second, "Buffer Elements are not comparable apparently")

    def test_merge_two_deques_stop_when_one_is_empty_no_duplicates(self):
        left_deque = deque()
        right_deque = deque()

        for i in range(self.max_elem_in_memory):
            new_buffer_element = BufferElement(create_string_from_int(i, self.max_elem_in_memory), Action.INSERT)
            if i % 2 == 0:
                left_deque.append(new_buffer_element)
            else:
                right_deque.append(new_buffer_element)

        self.assert_ascending_buffer_elements(left_deque)
        self.assert_ascending_buffer_elements(right_deque)

        merged_until_one_is_empty = merge_sort_stop_when_one_is_empty(left_deque, right_deque)
        self.assertTrue(not left_deque or not right_deque)
        self.assert_ascending_buffer_elements(merged_until_one_is_empty)

    def test_append_to_empty_sorted_file(self):
        sorted_file_elements = []
        for i in range(self.max_elem_in_memory):
            new_buffer_element = BufferElement(create_string_from_int(i, self.max_elem_in_memory), Action.INSERT)
            sorted_file_elements.append(new_buffer_element)

        sorted_id = get_new_sorted_id()
        append_to_sorted_buffer_elements_file(self.leaf_node.node_id, sorted_id, sorted_file_elements)
        file_path = get_sorted_file_path_from_timestamps(self.leaf_node.node_id, sorted_id)
        reloaded_file_elements = read_buffer_elements_from_file_path(file_path)
        self.assertEqual(sorted_file_elements, reloaded_file_elements)

    def test_external_merge_sort_two_files_no_duplicates(self):
        node_id = self.leaf_node.node_id

        first_file_elements = []
        second_file_elements = []
        combined = []
        for i in range(self.max_elem_in_memory):
            new_buffer_element = BufferElement(create_string_from_int(i, self.max_elem_in_memory), Action.INSERT)
            combined.append(new_buffer_element)
            if i % 2:
                first_file_elements.append(new_buffer_element)
            else:
                second_file_elements.append(new_buffer_element)

        first_sorted_id, second_sorted_id = get_new_sorted_id(), get_new_sorted_id()
        append_to_sorted_buffer_elements_file(node_id, first_sorted_id, first_file_elements)
        append_to_sorted_buffer_elements_file(node_id, second_sorted_id, second_file_elements)
        new_sorted_id = external_merge_sort_buffer_elements_two_files(node_id, first_sorted_id, second_sorted_id, self.max_elem_in_memory)
        sorted_file_path = get_sorted_file_path_from_timestamps(node_id, new_sorted_id)
        reloaded_elements = read_buffer_elements_from_file_path(sorted_file_path)
        self.assertEqual(combined, reloaded_elements)

    def test_external_merge_sort_uneven_amount_of_files(self):
        node_id = self.leaf_node.node_id

        first_file_elements = []
        second_file_elements = []
        third_file_elements = []
        all_elements = []
        first_sorted_id, second_sorted_id, third_sorted_id = get_new_sorted_id(), get_new_sorted_id(), get_new_sorted_id()

        num_first_elements = 2050
        last_second_element = 3000
        last_element = 4000
        for i in range(num_first_elements):
            new_buffer_element = BufferElement(create_string_from_int(i, last_element), Action.INSERT)
            all_elements.append(new_buffer_element)
            first_file_elements.append(new_buffer_element)
        append_to_sorted_buffer_elements_file(node_id, first_sorted_id, first_file_elements)

        for i in range(num_first_elements, last_second_element):
            new_buffer_element = BufferElement(create_string_from_int(i, last_element), Action.INSERT)
            all_elements.append(new_buffer_element)
            second_file_elements.append(new_buffer_element)
        append_to_sorted_buffer_elements_file(node_id, second_sorted_id, second_file_elements)

        for i in range(last_second_element, last_element):
            new_buffer_element = BufferElement(create_string_from_int(i, last_element), Action.INSERT)
            all_elements.append(new_buffer_element)
            third_file_elements.append(new_buffer_element)
        append_to_sorted_buffer_elements_file(node_id, third_sorted_id, third_file_elements)

        new_sorted_file_path = external_merge_sort_buffer_elements_many_files(node_id, [first_sorted_id, second_sorted_id, third_sorted_id], self.max_elem_in_memory)
        reloaded_elements = read_buffer_elements_from_file_path(new_sorted_file_path)
        self.assertEqual(reloaded_elements, all_elements)
    # TODO Write tests with duplicates once BufferElement-timestamps are fixed

    @staticmethod
    def create_dummy_tree():
        M = 2 * 4096
        B = 1024

        return BufferTree(M=M, B=B)

    def assert_lists_equal(self, first_list, second_list):
        self.assertEqual(len(first_list), len(second_list), "Lists are not of equal length")
        counter = 0
        for left_elem, right_elem in zip(first_list, second_list):
            self.assertEqual(left_elem, right_elem, f'Elements {left_elem} and {right_elem} at index {counter} are not the same')

    def assert_ascending_buffer_elements(self, buffer_elements):
        last_element = None
        for buffer_element in buffer_elements:
            if last_element is None:
                continue

            self.assertTrue(buffer_element.element > last_element.element)
            last_element = buffer_element


