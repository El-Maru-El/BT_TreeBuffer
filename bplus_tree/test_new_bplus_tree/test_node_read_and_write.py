import unittest
from bplus_tree.new_bplus_tree import BPlusTree, BPlusTreeNode, load_node, write_node, NodeType
from bplus_tree.bplus_helpers import clean_up_and_initialize_resource_directories


class TestSplit(unittest.TestCase):

    def setUp(self):
        clean_up_and_initialize_resource_directories()

    def test_read_and_write_root_node(self):
        value = '100'
        node = BPlusTree.create_root_leaf(value)

        write_node(node)
        reloaded_node = load_node(node.node_id, is_leaf=True)
        self.assertEqual(node.__dict__, reloaded_node.__dict__)

    def test_read_and_write_any_node(self):
        split_keys = [1, 2, 3]
        children = ['1', '2', '3', '4']
        node = BPlusTreeNode(node_type=NodeType.INTERNAL_NODE, split_keys=split_keys, children=children, parent_id='Papa')

        write_node(node)
        reloaded_node = load_node(node.node_id, is_leaf=False)

        self.assertEqual(node.__dict__, reloaded_node.__dict__)
