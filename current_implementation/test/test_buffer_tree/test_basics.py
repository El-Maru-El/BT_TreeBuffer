import unittest
from current_implementation.new_buffer_tree import *
from current_implementation.create_comparable_string import create_string_from_int


class BasicTreeTests(unittest.TestCase):

    def setUp(self):
        clean_up_and_initialize_resource_directories()

    def test_calculation_of_tree_members(self):
        first_tree = BufferTree(M=2 * 4096, B_buffer=1024)
        self.assertEqual(2 * 4096, first_tree.M)
        self.assertEqual(1024, first_tree.B_buffer)
        self.assertEqual(8, first_tree.m)
        self.assertEqual(first_tree.m, first_tree.b)
        self.assertEqual(2, first_tree.a)
        self.assertEqual(2, first_tree.s)
        self.assertEqual(3, first_tree.t)

        second_tree = BufferTree(M=100_000, B_buffer=1000)
        self.assertEqual(100_000, second_tree.M)
        self.assertEqual(1000, second_tree.B_buffer)
        self.assertEqual(100, second_tree.m)
        self.assertEqual(second_tree.m, second_tree.b)
        self.assertEqual(25, second_tree.a)
        self.assertEqual(13, second_tree.s)
        self.assertEqual(37, second_tree.t)

    def test_push_block_to_buffer(self):
        tree = self.create_dummy_tree()
        biggest_int = tree.B_buffer // 2

        for i in range(biggest_int):
            tree.insert_to_tree(create_string_from_int(i, biggest_int))

        root = tree.push_internal_buffer_to_root_return_root()

        self.assertEqual(1, len(root.buffer_block_ids))
        self.assertEqual(biggest_int, root.last_buffer_size)

    @staticmethod
    def create_dummy_tree():
        M = 2 * 4096
        B = 1024
        # m = 8

        return BufferTree(M=M, B_buffer=B)
