import unittest
from bplus_tree.bplus_tree import *


class TestStealOrMerge(unittest.TestCase):

    def setUp(self):
        clean_up_and_initialize_resource_directories()

    def test_delete(self):
        split_keys = [1, 2, 3, 4]
        children = ["1", "2", "3", "4", "99"]
        leaf_node = BPlusTreeNode(is_internal_node=False, split_keys=split_keys, children=children)
        leaf_node.leaf_delete_child_for_key(3)

        self.assertEqual([1, 2, 4], leaf_node.split_keys)
        self.assertEqual(["1", "2", "4", "99"], leaf_node.children)

    def test_delete_with_ancestor_swap(self):
        fake_ancestor = BPlusTreeNode(is_internal_node=True, split_keys=[3, 99, 105])
        split_keys = [1, 2, 3, 4]
        children = ["1", "2", "3", "4", "99"]
        leaf_node = BPlusTreeNode(is_internal_node=False, split_keys=split_keys, children=children, parent_id="Non-existing-parent")

        leaf_node.leaf_delete_child_for_key(99, fake_ancestor)

        self.assertEqual([3, 4, 105], fake_ancestor.split_keys)
        self.assertEqual([1, 2, 3], leaf_node.split_keys)
        self.assertEqual(["1", "2", "3", "4"], leaf_node.children)

    def test_steal(self):
        tree = BPlusTree(4)
        # TODO
