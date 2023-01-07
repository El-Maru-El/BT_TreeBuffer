import unittest
from current_implementation.new_buffer_tree import *
from bplus_tree.new_bplus_tree import *
from current_implementation.create_comparable_string import create_string_from_int
from current_implementation.test.is_proper_tree import assert_is_proper_tree
""" Those aren't actual new unittests (kinda only what happens in test_big_test.py), but it's good for manually checking out the benchmark output."""


class BigTestsWithTracking(unittest.TestCase):
    def setUp(self):
        clean_up_and_initialize_resource_directories()

    def test_big_big_big_big_big_tree(self):
        tree = self.create_dummy_tree()
        biggest_int = 200 * tree.B * tree.m

        elements = [create_string_from_int(i, biggest_int) for i in range(biggest_int)]

        tree.start_tracking_handler()
        for element in elements:
            tree.insert_to_tree(element)

        for element in elements[tree.B * 10:tree.B * 45]:
            tree.delete_from_tree(element)

        tree.flush_all_buffers()
        tree.stop_tracking_handler('big_big_big_test_benchmark')

    @staticmethod
    def create_dummy_tree():
        M = 2 * 4096
        B = 1024
        # m = 8

        return BufferTree(M=M, B=B)
