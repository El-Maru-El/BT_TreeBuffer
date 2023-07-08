import unittest
from current_implementation.new_buffer_tree import *
from bplus_tree.new_bplus_tree import *
from current_implementation.create_comparable_string import create_string_from_int_biggest_number
""" Those aren't actual new unittests (kinda only what happens in test_big_test.py), but it's good for manually checking out the benchmark output."""


class BigTestsWithTracking(unittest.TestCase):
    def setUp(self):
        clean_up_and_initialize_resource_directories()

    def test_create_files_same_elements_different_trees(self):
        # Creating all the elements:
        benchmark_name = 'test_benchmark_2'
        delete_start_ind = 500
        delete_stop_ind = 300
        biggest_int = 60000
        elements = [create_string_from_int_biggest_number(i, biggest_int) for i in range(biggest_int)]

        # Buffer Tree:
        buffer_tree = self.create_buffer_tree()
        b_plus_tree = self.create_bplus_tree()

        trees = [buffer_tree, b_plus_tree]
        # trees = [b_plus_tree]
        # trees = [buffer_tree]

        for tree in trees:
            tree.start_tracking_handler()
            for element in elements:
                tree.insert_to_tree(element)

            for element in elements[delete_start_ind:delete_stop_ind]:
                tree.delete_from_tree(element)

            if type(tree) == BufferTree:
                tree.flush_all_buffers()

            tree.stop_tracking_handler(benchmark_name)

    @staticmethod
    def create_buffer_tree():
        # M = 2 * 4096
        M = 1200
        B = 100
        # m = 8

        return BufferTree(M=M, B_buffer=B)

    @staticmethod
    def create_bplus_tree():
        order = 50
        max_leaf_size = 100
        return BPlusTree(order=order, max_leaf_size=max_leaf_size)
