import collections

from current_implementation.constants_and_helpers import *
from current_implementation.new_buffer_tree import *
import unittest
import time


class TestBasicStructure(unittest.TestCase):

    def setUp(self):
        delete_all_nodes()

    # def tearDown(self):
    #     delete_all_nodes()

    def test_basic_node_stuff(self):
        new_node = TreeNode(is_internal_node=False)
        write_node(new_node)
        reloaded_node = load_node(new_node.node_timestamp)

        self.assertEqual(new_node.__dict__, reloaded_node.__dict__)

    def test_actual_node_stuff(self):
        node_timestamp = get_current_timestamp()
        new_node = TreeNode(is_internal_node=True, handles=['abc', 'def'], children=[get_current_timestamp(), get_current_timestamp(), get_current_timestamp()])
        write_node(new_node)
        reloaded_node = load_node(node_timestamp)

        self.assertEqual(new_node.__dict__, reloaded_node.__dict__)

    def test_basic_buffer(self):
        fake_node = TreeNode(is_internal_node=False)
        elements = [BufferElement(str(i), Action.INSERT) for i in range(10)]
        buffer_timestamp = get_current_timestamp()
        write_buffer_block(fake_node.node_timestamp, buffer_timestamp, elements)
        reloaded_elements = read_buffer_block_elements(fake_node.node_timestamp, buffer_timestamp)
        self.assertEqual(elements, reloaded_elements)

    def test_tree_buffer_one_block(self):
        # -> m = 8 -> it's a (2,8) - Tree
        M = 2 * 4096
        B = 1024

        tree = BufferTree(M=M, B=B)

        elements_to_add = [f'Element_{i}' for i in range(int(1.5 * B))]
        for element in elements_to_add:
            tree.insert_to_tree(element)

        root_node = load_node(tree.root)
        self.assertEqual(len(root_node.buffer_block_timestamps), 1)

        buffer_elements = read_buffer_block_elements(tree.root, root_node.buffer_block_timestamps[0])
        buffer_elements_just_keys = [ele.element for ele in buffer_elements]

        self.assertEqual(buffer_elements_just_keys, elements_to_add[:B])

    def test_tree_buffer_two_blocks(self):
        # -> m = 8 -> it's a (2,8) - Tree
        M = 2 * 4096
        B = 1024

        tree = BufferTree(M=M, B=B)

        elements_to_add = [f'Element_{i}' for i in range(int(2 * B))]
        for element in elements_to_add:
            tree.insert_to_tree(element)

        root_node = load_node(tree.root)
        self.assertEqual(len(root_node.buffer_block_timestamps), 2)
        first_buffer_elements = read_buffer_block_elements(tree.root, root_node.buffer_block_timestamps[0])
        second_buffer_elements = read_buffer_block_elements(tree.root, root_node.buffer_block_timestamps[1])

        buffer_one_just_keys = [ele.element for ele in first_buffer_elements]
        buffer_two_just_keys = [ele.element for ele in second_buffer_elements]

        self.assertEqual(buffer_one_just_keys, elements_to_add[:B])
        self.assertEqual(buffer_two_just_keys, elements_to_add[B:2*B])

    def test_add_elements_to_empty_buffer(self):
        tree = self.create_dummy_tree()
        B = tree.B

        fake_node = TreeNode(is_internal_node=False)
        node_timestamp = fake_node.node_timestamp

        starting_elements = [BufferElement(f'Element_{i}', Action.INSERT) for i in range(B // 3)]

        fake_node.add_elements_to_buffer(parent_path=None, elements=starting_elements)

        self.assertEqual(len(fake_node.buffer_block_timestamps), 1)

        reloaded_buffer_elements = read_buffer_block_elements(node_timestamp, fake_node.buffer_block_timestamps[0])
        self.assertEqual(reloaded_buffer_elements, starting_elements)

    def test_add_elements_to_partially_filled_bufferblock(self):
        tree = self.create_dummy_tree()
        B = tree.B

        fake_node = TreeNode(is_internal_node=False)
        node_timestamp = fake_node.node_timestamp

        starting_elements = [BufferElement(f'Start_{i}', Action.INSERT) for i in range(B // 2)]
        fake_node.add_elements_to_buffer(parent_path=None, elements=starting_elements)

        appending_elements = [BufferElement(f'Append_{i}', Action.INSERT) for i in range(B)]
        fake_node.add_elements_to_buffer(parent_path=None, elements=appending_elements)

        self.assertEqual(len(fake_node.buffer_block_timestamps), 2)

        reloaded_buffer_one = read_buffer_block_elements(node_timestamp, fake_node.buffer_block_timestamps[0])
        reloaded_buffer_two = read_buffer_block_elements(node_timestamp, fake_node.buffer_block_timestamps[1])

        self.assertEqual(reloaded_buffer_one, starting_elements + appending_elements[:B // 2])
        self.assertEqual(reloaded_buffer_two, appending_elements[B // 2:])
        self.assertEqual(fake_node.last_buffer_size, B // 2)

    def test_add_elements_to_full_bufferblock(self):
        tree = self.create_dummy_tree()
        B = tree.B

        fake_node = TreeNode(is_internal_node=False)
        node_timestamp = fake_node.node_timestamp

        starting_elements = [BufferElement(f'Start_{i}', Action.INSERT) for i in range(B)]
        fake_node.add_elements_to_buffer(parent_path=None, elements=starting_elements)

        appending_elements = [BufferElement(f'Append_{i}', Action.INSERT) for i in range(B)]
        fake_node.add_elements_to_buffer(parent_path=None, elements=appending_elements)

        self.assertEqual(len(fake_node.buffer_block_timestamps), 2)
        self.assertEqual(fake_node.last_buffer_size, B)
        reloaded_buffer_one = read_buffer_block_elements(node_timestamp, fake_node.buffer_block_timestamps[0])
        reloaded_buffer_two = read_buffer_block_elements(node_timestamp, fake_node.buffer_block_timestamps[1])

        self.assertEqual(reloaded_buffer_one, starting_elements)
        self.assertEqual(reloaded_buffer_two, appending_elements)

    @staticmethod
    def create_dummy_tree():
        M = 2 * 4096
        B = 1024

        tree = BufferTree(M=M, B=B)
        time.sleep(0.1)
        return tree
