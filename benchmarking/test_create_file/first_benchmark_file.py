import unittest
from current_implementation.new_buffer_tree import *
from bplus_tree.new_bplus_tree import *
from current_implementation.create_comparable_string import create_string_from_int
""" Those aren't actual new unittests (kinda only what happens in test_big_test.py), but it's good for manually checking out the benchmark output."""


class BigTestsWithTracking(unittest.TestCase):
    def setUp(self):
        clean_up_and_initialize_resource_directories()

    def def_create_buffer_tree_benchmark(self, benchmark_name):

        tree = self.create_buffer_tree()
        biggest_int = 200 * tree.B_buffer * tree.m

        elements = [create_string_from_int(i, biggest_int) for i in range(biggest_int)]

        tree.start_tracking_handler()
        for element in elements:
            tree.insert_to_tree(element)

        for element in elements[tree.B_buffer * 10:tree.B_buffer * 45]:
            tree.delete_from_tree(element)

        tree.flush_all_buffers()
        tree.stop_tracking_handler(benchmark_name)

    def test_create_files_same_elements_different_trees(self):
        # Creating all the elements:
        benchmark_name = 'big_big_big_test_benchmark'
        delete_start_ind = 10240
        delete_stop_ind = 46080
        biggest_int = 1638400
        elements = [create_string_from_int(i, biggest_int) for i in range(biggest_int)]

        # Buffer Tree:
        buffer_tree = self.create_buffer_tree()
        b_plus_tree = self.create_bplus_tree()

        trees = [buffer_tree, b_plus_tree]

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
        M = 2 * 4096
        B = 1024
        # m = 8

        return BufferTree(M=M, B_buffer=B)

    @staticmethod
    def create_bplus_tree():
        order = 8
        min_leaf_size = 512
        max_leaf_size = 1024
        return BPlusTree(order=order, min_leaf_size=min_leaf_size, max_leaf_size=max_leaf_size)