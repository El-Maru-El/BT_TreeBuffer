import unittest
from current_implementation.new_buffer_tree import *


class TestOverwriteParentID(unittest.TestCase):
    def setUp(self):
        clean_up_and_initialize_resource_directories()

    def test_parent_ids_equal_length(self):
        new_parent_id = 'a'
        child_node = TreeNode(is_internal_node=False, parent_id='b')
        write_node(child_node)

        overwrite_parent_id(child_node.node_id, new_parent_id)
        reloaded_node = load_node(child_node.node_id)
        self.assertEqual(new_parent_id, reloaded_node.parent_id)

    def test_parent_ids_decreasing_length(self):

        new_parent_id = 'a'
        child_node = TreeNode(is_internal_node=False, parent_id='bb')
        write_node(child_node)

        overwrite_parent_id(child_node.node_id, new_parent_id)
        reloaded_node = load_node(child_node.node_id)
        self.assertEqual(new_parent_id, reloaded_node.parent_id)

    def test_parent_ids_increasing_length(self):
        new_parent_id = 'aa'
        child_node = TreeNode(is_internal_node=False, parent_id='b')
        write_node(child_node)

        overwrite_parent_id(child_node.node_id, new_parent_id)
        reloaded_node = load_node(child_node.node_id)
        self.assertEqual(new_parent_id, reloaded_node.parent_id)

    def test_overwrite_parent_id_with_none(self):
        child_node = TreeNode(is_internal_node=False, parent_id='a')
        write_node(child_node)

        overwrite_parent_id(child_node.node_id, None)
        reloaded_node = load_node(child_node.node_id)
        self.assertIsNone(reloaded_node.parent_id)
