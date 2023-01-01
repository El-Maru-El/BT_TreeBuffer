import unittest
from bplus_tree.my_own_bplus_tree import BPlusTree, BPlusTreeNode, write_node, load_node


class TestSplit(unittest.TestCase):

    def test_split_node_even_order(self):
        tree = BPlusTree(4)
        split_keys = [1, 2, 3, 4]
        children = ["1", "2", "3", "4", "5"]
        parent_split_keys = [0]
        expected_parent_split_keys = parent_split_keys + [split_keys[1]]
        expected_new_neighbor_split_keys = split_keys[:1]
        expected_new_neighbor_children = children[:2]

        expected_leaf_split_keys = split_keys[2:]
        expected_leaf_children = children[2:]

        parent_node = BPlusTreeNode(is_internal_node=True, split_keys=parent_split_keys)
        dummy_leaf_node = BPlusTreeNode(is_internal_node=False, parent_id=parent_node.node_id)
        leaf_node = BPlusTreeNode(is_internal_node=False, split_keys=split_keys, children=children, parent_id=parent_node.node_id)
        parent_node.children = [dummy_leaf_node.node_id, leaf_node.node_id]

        write_node(parent_node)
        write_node(dummy_leaf_node)

        tree.iteratively_split_nodes(leaf_node)

        reloaded_parent_node = load_node(parent_node.node_id)
        self.assertEqual(expected_parent_split_keys, reloaded_parent_node.split_keys)
        self.assertEqual(3, len(reloaded_parent_node.children))
        self.assertEqual(dummy_leaf_node.node_id, reloaded_parent_node.children[0])
        self.assertEqual(leaf_node.node_id, reloaded_parent_node.children[2])

        reloaded_leaf_node = load_node(leaf_node.node_id)
        self.assertEqual(reloaded_leaf_node.__dict__, leaf_node.__dict__)
        self.assertEqual(expected_leaf_split_keys, reloaded_leaf_node.split_keys)
        self.assertEqual(expected_leaf_children, reloaded_leaf_node.children)

        reloaded_new_neighbor = load_node(reloaded_parent_node.children[1])
        self.assertEqual(expected_new_neighbor_split_keys, reloaded_new_neighbor.split_keys)
        self.assertEqual(expected_new_neighbor_children, reloaded_new_neighbor.children)

    def test_split_node_odd_order(self):
        tree = BPlusTree(5)
        split_keys = [1, 2, 3, 4, 5]
        children = ["1", "2", "3", "4", "5", "10"]
        parent_split_keys = [0]
        expected_parent_split_keys = parent_split_keys + [split_keys[2]]
        expected_new_neighbor_split_keys = split_keys[:2]
        expected_new_neighbor_children = children[:3]

        expected_leaf_split_keys = split_keys[3:]
        expected_leaf_children = children[3:]

        parent_node = BPlusTreeNode(is_internal_node=True, split_keys=parent_split_keys)
        dummy_leaf_node = BPlusTreeNode(is_internal_node=False, parent_id=parent_node.node_id)
        leaf_node = BPlusTreeNode(is_internal_node=False, split_keys=split_keys, children=children, parent_id=parent_node.node_id)
        parent_node.children = [dummy_leaf_node.node_id, leaf_node.node_id]

        write_node(parent_node)
        write_node(dummy_leaf_node)

        tree.iteratively_split_nodes(leaf_node)

        reloaded_parent_node = load_node(parent_node.node_id)
        self.assertEqual(expected_parent_split_keys, reloaded_parent_node.split_keys)
        self.assertEqual(3, len(reloaded_parent_node.children))
        self.assertEqual(leaf_node.node_id, reloaded_parent_node.children[2])

        reloaded_leaf_node = load_node(leaf_node.node_id)
        self.assertEqual(reloaded_leaf_node.__dict__, leaf_node.__dict__)
        self.assertEqual(expected_leaf_split_keys, reloaded_leaf_node.split_keys)
        self.assertEqual(expected_leaf_children, reloaded_leaf_node.children)

        reloaded_new_neighbor = load_node(reloaded_parent_node.children[1])
        self.assertEqual(expected_new_neighbor_split_keys, reloaded_new_neighbor.split_keys)
        self.assertEqual(expected_new_neighbor_children, reloaded_new_neighbor.children)
