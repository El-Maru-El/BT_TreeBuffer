import unittest
from current_implementation.new_buffer_tree import *
from current_implementation.create_comparable_string import create_string_from_int_biggest_number
from current_implementation.test.is_proper_tree import assert_is_proper_tree
""" Those aren't actual new unittests (kinda only what happens in test_big_test.py), but it's good for manually checking out the benchmark output."""


class BigTestsWithTracking(unittest.TestCase):
    def setUp(self):
        clean_up_and_initialize_resource_directories()

    def test_write_and_delete_everything(self):
        # Have empty leaf node, increasing elements, insert into tree, creating 8 Leaf Blocks under root node, delete them all again
        # Inserting and deleting (each) exactly tree.m * tree.B = M elements leads to root buffers being emptied exactly twice for each insertions and deletions -> empty tree at the end
        tree = self.create_dummy_tree()
        tree.start_tracking_handler()
        biggest_int = tree.m * tree.B_buffer
        for i in range(biggest_int):
            tree.insert_to_tree(create_string_from_int_biggest_number(i, biggest_int))

        assert_is_proper_tree(self, tree)

        root_node_before_delete = load_node(tree.root_node_id)
        self.assertEqual(tree.m, len(root_node_before_delete.children_ids))
        self.assertFalse(root_node_before_delete.has_buffer_elements())
        self.assertEqual(0, root_node_before_delete.last_buffer_size)
        self.assertFalse(root_node_before_delete.is_internal_node())

        for i in range(biggest_int):
            tree.delete_from_tree(create_string_from_int_biggest_number(i, biggest_int))

        root_node_after_delete = load_node(tree.root_node_id)
        self.assertEqual(0, len(root_node_after_delete.children_ids))
        self.assertFalse(root_node_after_delete.has_buffer_elements())
        self.assertFalse(root_node_before_delete.is_internal_node())
        tree.stop_tracking_handler()

    def test_big_big_tree(self):
        tree = self.create_dummy_tree()
        biggest_int = 20 * tree.B_buffer * tree.m

        elements = [create_string_from_int_biggest_number(i, biggest_int) for i in range(biggest_int)]

        tree.start_tracking_handler()
        for element in elements:
            tree.insert_to_tree(element)

        assert_is_proper_tree(self, tree)

        for element in elements:
            tree.delete_from_tree(element)

        tree.flush_all_buffers()
        root_node = load_node(tree.root_node_id)
        self.assertEqual(0, len(root_node.children_ids))
        self.assertEqual(0, len(root_node.handles))
        self.assertFalse(root_node.is_internal_node())
        tree.stop_tracking_handler()

    # @unittest.skip("Kinda takes long when I make inbetween checks")
    def test_big_big_big_big_big_tree(self):
        tree = self.create_dummy_tree()
        biggest_int = 200 * tree.B_buffer * tree.m

        elements = [create_string_from_int_biggest_number(i, biggest_int) for i in range(biggest_int)]

        tree.start_tracking_handler()
        for element in elements:
            tree.insert_to_tree(element)

        for element in elements[tree.B_buffer * 10:tree.B_buffer * 45]:
            tree.delete_from_tree(element)

        tree.flush_all_buffers()
        tree.stop_tracking_handler()

    @staticmethod
    def create_dummy_tree():
        M = 2 * 4096
        B = 1024
        # m = 8

        return BufferTree(M=M, B_buffer=B)

