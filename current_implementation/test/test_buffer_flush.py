import unittest
from current_implementation.new_buffer_tree import *
from current_implementation.create_comparable_string import create_string_from_int


class BufferFlushTest(unittest.TestCase):
    def setUp(self):
        clean_up_and_initialize_resource_directories()

    def test_a_single_element(self):
        tree = self.create_dummy_tree()
        only_element = create_string_from_int(1, 1)
        tree.insert_to_tree(only_element)
        tree.flush_all_buffers()

        reloaded_root_node = load_node(tree.root_node_id)
        self.assertEqual([], tree.tree_buffer.elements)
        self.assertEqual(1, len(reloaded_root_node.children_ids))
        self.assertFalse(reloaded_root_node.is_internal_node())

        reloaded_leaf_elements = read_leaf_block_elements_as_deque(reloaded_root_node.children_ids[0])
        self.assertEqual(1, len(reloaded_leaf_elements))
        self.assertEqual(only_element, reloaded_leaf_elements[0])

    def test_add_and_delete_single_element(self):
        tree = self.create_dummy_tree()
        only_element = create_string_from_int(1, 1)
        tree.insert_to_tree(only_element)
        tree.delete_from_tree(only_element)
        tree.flush_all_buffers()

        reloaded_root_node = load_node(tree.root_node_id)
        self.assertEqual(0, len(reloaded_root_node.children_ids))

# TODO More tests for flushing buffer would be good (bigger tree structure)

    @staticmethod
    def create_dummy_tree():
        M = 2 * 4096
        B = 1024
        # m = 8

        return BufferTree(M=M, B=B)
