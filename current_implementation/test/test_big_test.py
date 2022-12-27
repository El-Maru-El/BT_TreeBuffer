import unittest
from current_implementation.new_buffer_tree import *
from current_implementation.create_comparable_string import create_string_from_int


class JustThrowBigTestsAtTree(unittest.TestCase):
    def setUp(self):
        clean_up_and_initialize_resource_directories()

    def test_write_and_delete_everything(self):
        # Have empty leaf node, increasing elements, insert into tree, creating 8 Leaf Blocks under root node, delete them all again

        tree = self.create_dummy_tree()
        biggest_int = tree.m * tree.B
        for i in range(biggest_int):
            tree.insert_to_tree(create_string_from_int(i, biggest_int))

        root_node_before_delete = load_node(tree.root_node_id)
        self.assertEqual(tree.m, len(root_node_before_delete.children_ids))
        self.assertFalse(root_node_before_delete.has_buffer_elements())
        self.assertEqual(0, root_node_before_delete.last_buffer_size)
        self.assertFalse(root_node_before_delete.is_internal_node())

        for i in range(biggest_int):
            tree.delete_from_tree(create_string_from_int(i, biggest_int))

        root_node_after_delete = load_node(tree.root_node_id)
        self.assertEqual(0, len(root_node_after_delete.children_ids))
        self.assertFalse(root_node_after_delete.has_buffer_elements())
        self.assertFalse(root_node_before_delete.is_internal_node())

    def test_big_big_tree(self):
        tree = self.create_dummy_tree()
        biggest_int = 50 * tree.B * tree.m
        for i in range(biggest_int):
            tree.insert_to_tree(create_string_from_int(i, biggest_int))

        for i in range(biggest_int):
            tree.delete_from_tree(create_string_from_int(i, biggest_int))

    @staticmethod
    def create_dummy_tree():
        M = 2 * 4096
        B = 1024
        # m = 8

        return BufferTree(M=M, B=B)