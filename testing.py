import collections

from current_implementation.constants_and_helpers import *
from current_implementation.new_buffer_tree import *
import unittest


class TestBasicStructure(unittest.TestCase):

    def tearDown(self):
        delete_all_nodes()

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

    def test_buffer(self):
        fake_node = TreeNode(is_internal_node=False)
        elements = [BufferElement(str(i), Action.INSERT) for i in range(10)]
        buffer_timestamp = get_current_timestamp()
        write_buffer_block(fake_node.node_timestamp, buffer_timestamp, elements)
        reloaded_elements = read_buffer_block_elements(fake_node.node_timestamp, buffer_timestamp)
        self.assertEqual(elements, reloaded_elements)



