from current_implementation.new_buffer_tree import *
import unittest


class TestNodeBasicStructure(unittest.TestCase):

    def setUp(self):
        clean_up_and_initialize_resource_directories()

    def test_basic_node_writing_and_reading(self):
        new_node = TreeNode(is_internal_node=False)
        write_node(new_node)
        reloaded_node = load_node(new_node.node_id)

        self.assertEqual(new_node.__dict__, reloaded_node.__dict__)

    def test_advanced_node_writing_and_reading(self):
        new_node = TreeNode(is_internal_node=True, handles=['abc', 'def'],
                            children=[get_new_node_id(), get_new_node_id(), get_new_node_id()])
        node_id = new_node.node_id
        write_node(new_node)
        reloaded_node = load_node(node_id)

        self.assertEqual(new_node.__dict__, reloaded_node.__dict__)
