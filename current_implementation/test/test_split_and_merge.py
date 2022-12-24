import unittest
from current_implementation.new_buffer_tree import *
from current_implementation.create_comparable_string import create_string_from_int


class TestTreeNodeSplitAndMerge(unittest.TestCase):
    def setUp(self):
        clean_up_and_initialize_resource_directories()

    def test_split_on_root(self):
        tree = self.create_dummy_tree()
        old_root_node = load_node(tree.root_node_id)
        # One more child than b, so we can split it afterwards
        fake_leaf_block_ids = ['c_0', 'c_1', 'c_2', 'c_3', 'c_4', 'c_5', 'c_6', 'c_7', 'c_8']
        fake_split_keys = ['0', '1', '2', '3', '4', '5', '6', '7']
        self.assertEqual(tree.b + 1, len(fake_leaf_block_ids), 'Test input has been initialised incorrectly')
        self.assertEqual(tree.b, len(fake_split_keys), 'Test input has been initialised incorrectly')

        # Trigger split_leaf_node() with correctly initialised root node
        old_root_node.handles = fake_split_keys
        old_root_node.children_ids = fake_leaf_block_ids
        old_root_node.split_leaf_node()

        # Check new root node:
        self.assertNotEqual(old_root_node.node_id, tree.root_node_id)
        new_root_node = load_node(tree.root_node_id)
        self.assertTrue(new_root_node.is_internal_node())
        self.assertEqual(['3'], new_root_node.handles)
        self.assertEqual(2, len(new_root_node.children_ids))
        self.assertEqual(old_root_node.node_id, new_root_node.children_ids[1])

        # Check old root node, which has not been written back to ext. memory yet
        self.assertFalse(old_root_node.is_internal_node())
        self.assertEqual(['c_4', 'c_5', 'c_6', 'c_7', 'c_8'], old_root_node.children_ids)
        self.assertEqual(['4', '5', '6', '7'], old_root_node.handles)
        self.assertEqual(new_root_node.node_id, old_root_node.parent_id)

        # Check new root node, which has been reloaded from ext. memory
        new_left_neighbor = load_node(new_root_node.children_ids[0])
        self.assertFalse(new_left_neighbor.is_internal_node())
        self.assertEqual(['0', '1', '2'], new_left_neighbor.handles)
        self.assertEqual(['c_0', 'c_1', 'c_2', 'c_3'], new_left_neighbor.children_ids)
        self.assertEqual(new_root_node.node_id, new_left_neighbor.parent_id)

        # Check that old root node has NOT been written to ext. memory yet (it's only been written when tree has been initialised)
        fail_message = 'Root has been changed in external memory, but should not have yet'
        reloaded_old_root_node = load_node(old_root_node.node_id)
        self.assertEqual([], reloaded_old_root_node.children_ids)
        self.assertEqual([], reloaded_old_root_node.handles)
        self.assertEqual(None, reloaded_old_root_node.parent_id)

    @staticmethod
    def create_dummy_tree():
        M = 2 * 4096
        B = 1024
        # m = 8

        return BufferTree(M=M, B=B)