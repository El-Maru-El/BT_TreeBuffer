import unittest
from bplus_tree.bplus_tree import *
from current_implementation.create_comparable_string import create_string_from_int
from get_all_leaf_elements import get_all_leaf_elements


class TestALotOfAction(unittest.TestCase):

    def setUp(self):
        clean_up_and_initialize_resource_directories()

    def test_insert_few_elements(self):
        tree = BPlusTree(order=8)
        biggest_int = 7
        input_key_values = [(i, create_string_from_int(i, biggest_int)) for i in range(biggest_int)]
        keys = [k for k, _ in input_key_values]
        values = [v for _, v in input_key_values]
        for k, v in input_key_values:
            tree.insert_to_tree(k, v)

        loaded_root_node = load_node(tree.root_node_id)
        self.assertEqual(8, len(loaded_root_node.children))
        self.assertEqual(values, loaded_root_node.children[:-1])
        self.assertEqual(keys, loaded_root_node.split_keys)

    def test_insert_many_elements_ascending(self):
        tree = BPlusTree(order=500)
        biggest_int = 10000
        input_key_values = [(i, create_string_from_int(i, biggest_int)) for i in range(biggest_int)]
        expected_elements = [v for _, v in input_key_values]

        for k, v in input_key_values:
            tree.insert_to_tree(k, v)

        found_elements = get_all_leaf_elements(tree)

        self.assertEqual(expected_elements, found_elements)

    def test_insert_elements_even_tree_order_arbitrary_element_order(self):
        tree = BPlusTree(100)

        biggest_int = 10000

        upper_ind = lower_ind = biggest_int // 2

        key_values_sorted = [(i, create_string_from_int(i, biggest_int)) for i in range(biggest_int)]
        values_sorted = [v for _, v in key_values_sorted]

        while upper_ind < len(key_values_sorted) or lower_ind >= 0:
            if upper_ind < len(key_values_sorted):
                k, v = key_values_sorted[upper_ind]
                upper_ind += 1
                tree.insert_to_tree(k, v)
            if lower_ind >= 0:
                k, v = key_values_sorted[lower_ind]
                lower_ind -= 1
                tree.insert_to_tree(k, v)

        found_leaf_elements = get_all_leaf_elements(tree)

        self.assertEqual(values_sorted, found_leaf_elements)

    def test_insert_elements_uneven_tree_order_arbitrary_element_order(self):
        tree = BPlusTree(99)

        biggest_int = 10000

        upper_ind = lower_ind = biggest_int // 2

        key_values_sorted = [(i, create_string_from_int(i, biggest_int)) for i in range(biggest_int)]
        values_sorted = [v for _, v in key_values_sorted]

        while upper_ind < len(key_values_sorted) or lower_ind >= 0:
            if upper_ind < len(key_values_sorted):
                k, v = key_values_sorted[upper_ind]
                upper_ind += 1
                tree.insert_to_tree(k, v)
            if lower_ind >= 0:
                k, v = key_values_sorted[lower_ind]
                lower_ind -= 1
                tree.insert_to_tree(k, v)

        found_leaf_elements = get_all_leaf_elements(tree)

        self.assertEqual(values_sorted, found_leaf_elements)

    def test_insert_and_few_deletes_even_tree_order(self):
        tree = BPlusTree(100)

        biggest_int = 10000
        key_values_sorted = [(i, create_string_from_int(i, biggest_int)) for i in range(biggest_int)]
        values_sorted = [v for _, v in key_values_sorted]

        for k, v in key_values_sorted:
            tree.insert_to_tree(k, v)

        ints_to_be_remove = [1, 4, 20, 300, 4000, 5734, 2387, 9748, 4323]
        key_values_to_be_removed = [(i, create_string_from_int(i, biggest_int)) for i in ints_to_be_remove]
        removed_keys = [k for k, _ in key_values_to_be_removed]
        removed_values = [v for _, v in key_values_to_be_removed]

        expected_values = [v for v in values_sorted if v not in removed_values]

        for k in removed_keys:
            tree.delete_from_tree(k)

        found_leaf_elements = get_all_leaf_elements(tree)

        self.assertEqual(expected_values, found_leaf_elements)

        # Now delete a few elements
