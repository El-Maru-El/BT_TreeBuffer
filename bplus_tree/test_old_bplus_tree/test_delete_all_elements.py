import unittest
from bplus_tree.bplus_tree import *
from current_implementation.create_comparable_string import create_string_from_int_biggest_number


class TestDeleteFunctionality(unittest.TestCase):

    def setUp(self):
        clean_up_and_initialize_resource_directories()

    def test_insert_and_delete_tree_even_order_elements_ascending(self):
        tree = BPlusTree(8)

        biggest_int = 500

        key_value_pairs = [(i, create_string_from_int_biggest_number(i, biggest_int)) for i in range(biggest_int)]

        for k, v in key_value_pairs:
            tree.insert_to_tree(k, v)

        for key_to_be_deleted, _ in key_value_pairs:
            tree.delete_from_tree(key_to_be_deleted)

        self.assertIsNone(tree.root_node_id)

    def test_insert_and_delete_tree_odd_order_elements_ascending(self):
        tree = BPlusTree(9)

        biggest_int = 500

        key_value_pairs = [(i, create_string_from_int_biggest_number(i, biggest_int)) for i in range(biggest_int)]

        for k, v in key_value_pairs:
            tree.insert_to_tree(k, v)

        for key_to_be_deleted, _ in key_value_pairs:
            tree.delete_from_tree(key_to_be_deleted)

        self.assertIsNone(tree.root_node_id)

    def test_insert_and_delete_tree_even_order_elements_delete_descending(self):
        tree = BPlusTree(8)

        biggest_int = 500

        key_value_pairs = [(i, create_string_from_int_biggest_number(i, biggest_int)) for i in range(biggest_int)]

        for k, v in key_value_pairs:
            tree.insert_to_tree(k, v)

        for key_to_be_deleted, _ in reversed(key_value_pairs):
            tree.delete_from_tree(key_to_be_deleted)

        self.assertIsNone(tree.root_node_id)

