import unittest
from bplus_tree.new_bplus_tree import *
from current_implementation.create_comparable_string import create_string_from_int_biggest_number
from get_all_leaf_elements import get_all_leaf_elements


class TestDeleteFunctionality(unittest.TestCase):

    def setUp(self):
        clean_up_and_initialize_resource_directories()

    def test_insert_and_delete_tree_even_order_elements_ascending(self):
        tree = BPlusTree(8)

        biggest_int = 500

        elements = [create_string_from_int_biggest_number(i, biggest_int) for i in range(biggest_int)]

        for ele in elements:
            tree.insert_to_tree(ele)

        for ele in elements:
            tree.delete_from_tree(ele)

        self.assertEqual([], get_all_leaf_elements(tree))

    def test_insert_and_delete_tree_odd_order_elements_ascending(self):
        tree = BPlusTree(9)

        biggest_int = 500

        elements = [create_string_from_int_biggest_number(i, biggest_int) for i in range(biggest_int)]

        for ele in elements:
            tree.insert_to_tree(ele)

        for ele in elements:
            tree.delete_from_tree(ele)

        self.assertEqual([], get_all_leaf_elements(tree))

    def test_insert_and_delete_tree_even_order_elements_delete_descending(self):
        tree = BPlusTree(8)

        biggest_int = 500

        elements = [create_string_from_int_biggest_number(i, biggest_int) for i in range(biggest_int)]

        for ele in elements:
            tree.insert_to_tree(ele)

        for ele in reversed(elements):
            tree.delete_from_tree(ele)

        self.assertEqual([], get_all_leaf_elements(tree))

