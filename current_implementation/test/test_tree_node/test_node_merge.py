import unittest
from current_implementation.new_buffer_tree import *
from current_implementation.create_comparable_string import create_string_from_int_biggest_number


class TestTreeNodeSplit(unittest.TestCase):
    def setUp(self):
        clean_up_and_initialize_resource_directories()

    def test_standard_merge_is_left(self):
        tree = self.create_dummy_tree()

        current_node = self.make_right_node(tree)

        left_node = self.make_left_node(tree)

        root_node = load_node(tree.root_node_id)
        root_node.is_intern = True
        root_node.children_ids = [left_node.node_id, current_node.node_id]
        root_node.handles = ['parent_split_key']

        expected_split_keys = left_node.handles + root_node.handles + current_node.handles[:-1]
        expected_children = left_node.children_ids + current_node.children_ids[:-1]

        current_node.merge_with_neighbor(root_node, left_node, True)
        self.assertEqual(expected_split_keys, current_node.handles)
        self.assertEqual(expected_children, current_node.children_ids)

        self.assertEqual([], root_node.handles)
        self.assertEqual([current_node.node_id], root_node.children_ids)

        self.assertEqual(deque([root_node.node_id]), tree.node_to_steal_or_merge_queue)

    def test_standard_merge_is_right(self):
        tree = self.create_dummy_tree()

        current_node = self.make_left_node(tree)
        right_node = self.make_right_node(tree)

        root_node = load_node(tree.root_node_id)
        root_node.is_intern = True
        root_node.children_ids = [current_node.node_id, right_node.node_id]
        root_node.handles = ['parent_split_key']

        expected_split_keys = current_node.handles + root_node.handles + right_node.handles[:-1]
        expected_children = current_node.children_ids + right_node.children_ids[:-1]

        current_node.merge_with_neighbor(root_node, right_node, False)
        self.assertEqual(expected_split_keys, current_node.handles)
        self.assertEqual(expected_children, current_node.children_ids)

        self.assertEqual([], root_node.handles)
        self.assertEqual([current_node.node_id], root_node.children_ids)

        self.assertEqual(deque([root_node.node_id]), tree.node_to_steal_or_merge_queue)

    @staticmethod
    def make_left_node(tree):
        left_neighbor_handles = [f'l_cur_split_{i}' for i in range(tree.a + tree.t - 1)]
        left_neighbor_children_ids = [f'left_c_{i}' for i in range(tree.a + tree.t)]
        left_node = TreeNode(is_internal_node=False, handles=left_neighbor_handles, children=left_neighbor_children_ids, parent_id=tree.root_node_id)
        return left_node

    @staticmethod
    def make_right_node(tree):
        current_node_handles = [f'z_cur_split_{i}' for i in range(tree.a - 3)]
        current_node_handles.append(DUMMY_STRING)
        current_node_children_ids = [f'curr_c_{i}' for i in range(tree.a - 2)]
        current_node_children_ids.append(DUMMY_STRING)
        current_node = TreeNode(is_internal_node=False, handles=current_node_handles, children=current_node_children_ids, parent_id=tree.root_node_id)
        return current_node

    @staticmethod
    def create_dummy_tree():
        M = 2 * 4096
        B = 512
        # b = m = 16
        # a = 4
        # s = 3
        # t = 6
        # -> a + t + 1 = 11, with under 11 children on neighbor, we merge

        return BufferTree(M=M, B_buffer=B)
