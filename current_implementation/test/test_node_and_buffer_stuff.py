from current_implementation.new_buffer_tree import *
from current_implementation.create_comparable_string import create_string_from_int
import unittest


class TestTreeBuffer(unittest.TestCase):

    def setUp(self):
        clean_up_and_initialize_resource_directories()

    def test_perfectly_filled_tree_buffer_one_block(self):
        tree = self.create_dummy_tree()

        biggest_int = tree.B_buffer
        elements_to_add = [create_string_from_int(i, biggest_int) for i in range(biggest_int)]
        for element in elements_to_add:
            tree.insert_to_tree(element)

        root_node = load_node(tree.root_node_id)
        self.assertEqual(len(root_node.buffer_block_ids), 1)

        node_buffer_elements = read_buffer_block_elements(tree.root_node_id, root_node.buffer_block_ids[0])
        node_buffer_elements_just_keys = [ele.element for ele in node_buffer_elements]

        self.assertEqual(node_buffer_elements_just_keys, elements_to_add)
        self.assertEqual([], tree.tree_buffer.elements)

    def test_overfilled_tree_buffer_one_block(self):
        tree = self.create_dummy_tree()

        biggest_int = int(1.5 * tree.B_buffer)
        elements_to_add = [create_string_from_int(i, biggest_int) for i in range(biggest_int)]
        for element in elements_to_add:
            tree.insert_to_tree(element)

        root_node = load_node(tree.root_node_id)
        self.assertEqual(len(root_node.buffer_block_ids), 1)

        node_buffer_elements = read_buffer_block_elements(tree.root_node_id, root_node.buffer_block_ids[0])
        node_buffer_elements_just_keys = [ele.element for ele in node_buffer_elements]

        tree_buffer_elements_just_keys = [ele.element for ele in tree.tree_buffer.elements]

        self.assertEqual(node_buffer_elements_just_keys, elements_to_add[:tree.B_buffer])
        self.assertEqual(tree_buffer_elements_just_keys, elements_to_add[tree.B_buffer:])

    def test_perfectly_filled_tree_buffer_two_blocks(self):
        tree = self.create_dummy_tree()

        elements_to_add = [f'Element_{i}' for i in range(int(2 * tree.B_buffer))]
        for element in elements_to_add:
            tree.insert_to_tree(element)

        root_node = load_node(tree.root_node_id)
        self.assertEqual(len(root_node.buffer_block_ids), 2)
        first_buffer_elements = read_buffer_block_elements(tree.root_node_id, root_node.buffer_block_ids[0])
        second_buffer_elements = read_buffer_block_elements(tree.root_node_id, root_node.buffer_block_ids[1])

        buffer_one_just_keys = [ele.element for ele in first_buffer_elements]
        buffer_two_just_keys = [ele.element for ele in second_buffer_elements]

        self.assertEqual(buffer_one_just_keys, elements_to_add[:tree.B_buffer])
        self.assertEqual(buffer_two_just_keys, elements_to_add[tree.B_buffer:2 * tree.B_buffer])
        self.assertEqual([], tree.tree_buffer.elements)



    @staticmethod
    def create_dummy_tree():
        M = 2 * 4096
        B = 1024

        return BufferTree(M=M, B_buffer=B)
