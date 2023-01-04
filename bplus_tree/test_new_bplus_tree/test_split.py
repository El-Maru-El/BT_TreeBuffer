import unittest
from bplus_tree.new_bplus_tree import *
from bplus_tree.bplus_helpers import *
from current_implementation.create_comparable_string import create_string_from_int


class TestSplit(unittest.TestCase):

    def setUp(self):
        clean_up_and_initialize_resource_directories()

    def test_split_node_even_order(self):
        tree = BPlusTree(4)
        children = ["1", "2", "3", "4", "5"]
        parent_split_keys = ["0"]
        expected_parent_split_keys = ["0", "2"]
        expected_new_neighbor_children = children[:2]

        expected_leaf_children = children[2:]

        parent_node = BPlusTreeNode(node_type=NodeType.INTERNAL_NODE, split_keys=parent_split_keys)
        dummy_leaf_node = Leaf(parent_id=parent_node.node_id)
        leaf_node = Leaf(children=children, parent_id=parent_node.node_id)
        parent_node.children = [dummy_leaf_node.node_id, leaf_node.node_id]

        write_node(parent_node)
        write_node(dummy_leaf_node)

        tree.iteratively_split_nodes(leaf_node)

        reloaded_parent_node = load_node(parent_node.node_id, is_leaf=False)
        self.assertEqual(expected_parent_split_keys, reloaded_parent_node.split_keys)
        self.assertEqual(3, len(reloaded_parent_node.children))
        self.assertEqual(dummy_leaf_node.node_id, reloaded_parent_node.children[0])
        self.assertEqual(leaf_node.node_id, reloaded_parent_node.children[2])

        reloaded_leaf_node = load_node(leaf_node.node_id, is_leaf=True)
        self.assertEqual(reloaded_leaf_node.__dict__, leaf_node.__dict__)
        self.assertEqual(expected_leaf_children, reloaded_leaf_node.children)

        reloaded_new_neighbor = load_node(reloaded_parent_node.children[1], is_leaf=True)
        self.assertEqual(expected_new_neighbor_children, reloaded_new_neighbor.children)

    def test_split_node_odd_order(self):
        tree = BPlusTree(5)
        children = ["1", "2", "3", "4", "5", "10"]
        parent_split_keys = ["0"]
        expected_parent_split_keys = ["0", "3"]
        expected_new_neighbor_children = children[:3]

        expected_leaf_children = children[3:]

        parent_node = BPlusTreeNode(node_type=NodeType.LEAF_NODE, split_keys=parent_split_keys)
        dummy_leaf_node = Leaf(parent_id=parent_node.node_id)
        leaf_node = Leaf(children=children, parent_id=parent_node.node_id)
        parent_node.children = [dummy_leaf_node.node_id, leaf_node.node_id]

        write_node(parent_node)
        write_node(dummy_leaf_node)

        tree.iteratively_split_nodes(leaf_node)

        reloaded_parent_node = load_node(parent_node.node_id, is_leaf=False)
        self.assertEqual(expected_parent_split_keys, reloaded_parent_node.split_keys)
        self.assertEqual(3, len(reloaded_parent_node.children))
        self.assertEqual(leaf_node.node_id, reloaded_parent_node.children[2])

        reloaded_leaf_node = load_node(leaf_node.node_id, is_leaf=True)
        self.assertEqual(reloaded_leaf_node.__dict__, leaf_node.__dict__)
        self.assertEqual(expected_leaf_children, reloaded_leaf_node.children)

        reloaded_new_neighbor = load_node(reloaded_parent_node.children[1], is_leaf=True)
        self.assertEqual(expected_new_neighbor_children, reloaded_new_neighbor.children)

    def test_split_on_root(self):
        order = 4
        tree = BPlusTree(order=order)
        biggest_int = 5
        # Since we have one Dummy Child, it will split here
        elements = [create_string_from_int(i, biggest_int) for i in range(biggest_int)]
        for ele in elements:
            tree.insert_to_tree(ele)

        root_node = load_node(tree.root_node_id, is_leaf=False)
        self.assertEqual([elements[1]], root_node.split_keys)
        self.assertEqual(2, len(root_node.children))
        self.assertTrue(root_node.is_leaf_node())

        left_child = load_node(root_node.children[0], is_leaf=True)
        right_child = load_node(root_node.children[1], is_leaf=True)

        self.assertEqual(['0', '1'], left_child.children)
        self.assertEqual(root_node.node_id, left_child.parent_id)
        self.assertTrue(left_child.is_leaf())

        self.assertEqual(['2', '3', '4'], right_child.children)
        self.assertEqual(root_node.node_id, right_child.parent_id)
        self.assertTrue(right_child.is_leaf())

