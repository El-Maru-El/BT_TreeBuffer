import unittest
from bplus_tree.old_bplus_tree import BPlusTree, BPlusTreeNode, load_node, write_node
from bplus_tree.bplus_helpers import clean_up_and_initialize_resource_directories


class TestSplit(unittest.TestCase):

    def setUp(self):
        clean_up_and_initialize_resource_directories()

    def test_read_and_write_root_node(self):
        key, value = 100, '100'
        node = BPlusTree.create_root_node(key, value)

        write_node(node)
        reloaded_node = load_node(node.node_id)
        self.assertEqual(node.__dict__, reloaded_node.__dict__)

    def test_read_and_write_any_node(self):
        split_keys = [1, 2, 3]
        children = ['1', '2', '3', '4']
        node = BPlusTreeNode(is_internal_node=False, split_keys=split_keys, children=children, parent_id='Papa')

        write_node(node)
        reloaded_node = load_node(node.node_id)

        self.assertEqual(node.__dict__, reloaded_node.__dict__)
