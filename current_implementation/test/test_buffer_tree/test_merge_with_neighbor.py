import unittest
from current_implementation.new_buffer_tree import *
from current_implementation.create_comparable_string import create_string_from_int_biggest_number, create_string_from_int_with_byte_size


class BasicTreeTests(unittest.TestCase):

    def setUp(self):
        clean_up_and_initialize_resource_directories()

    def test_merge_with_neighbor_leaf_nodes_left_neighbor_simple(self):
        tree = self.create_dummy_tree()
        byte_size = 2
        num_left_children = 5
        num_right_children = 3

        step_size = 10
        smallest_left_handle_int = 0
        biggest_left_handle_int = smallest_left_handle_int + (num_left_children - 2) * step_size
        smallest_right_handle_int = biggest_left_handle_int + step_size
        biggest_right_handle_int = smallest_right_handle_int + step_size * (num_right_children - 2)

        # To be extended with the corresponding children/split-keys etc later
        parent_node = TreeNode(is_internal_node=True)

        # Total of 5 children for parent node
        # The left merge neighbor (has a + 1 children)
        left_neighbor_handles = [create_string_from_int_with_byte_size(i, byte_size) for i in range(smallest_left_handle_int, biggest_left_handle_int + 1, step_size)]
        left_neighbor_children_ids = [f'l_{i}' for i in range(num_left_children)]
        left_neighbor = TreeNode(is_internal_node=False, handles=left_neighbor_handles, children=left_neighbor_children_ids, parent_id=parent_node.node_id)

        # The right merge neighbor (has a-1 children)
        right_neighbor_handles = [create_string_from_int_with_byte_size(i, byte_size) for i in range(smallest_right_handle_int, biggest_right_handle_int + 1, step_size)]
        right_neighbor_children_ids = [f'r_{i}' for i in range(num_right_children)]
        right_neighbor = TreeNode(is_internal_node=False, handles=right_neighbor_handles, children=right_neighbor_children_ids, parent_id=parent_node.node_id)

        disappearing_handle = create_string_from_int_with_byte_size(biggest_left_handle_int + step_size // 2, byte_size)

        # The parent node
        leaf_node_stubs = [TreeNode(is_internal_node=False).node_id for _ in range(3)]
        parents_children = leaf_node_stubs + [left_neighbor.node_id, right_neighbor.node_id]
        parent_handles = [f'sk_{i}' for i in range(3)] + [disappearing_handle]
        parent_node.children_ids = parents_children
        parent_node.handles = parent_handles

        # Pre-calculate expected results:
        expected_parent_handles = parent_handles[:-1]
        expected_children_ids_of_parent = leaf_node_stubs + [right_neighbor.node_id]

        expected_merge_handles = left_neighbor.handles + [disappearing_handle] + right_neighbor.handles
        expected_merge_children_ids = left_neighbor_children_ids + right_neighbor_children_ids

        right_neighbor.merge_with_neighbor(parent_node, left_neighbor, is_left_neighbor=True)

        # Is parent set correctly after merge
        self.assertEqual(parent_node.handles, expected_parent_handles)
        self.assertEqual(parent_node.children_ids, expected_children_ids_of_parent)

        # Is right neighbor set correctly after merge
        self.assertEqual(right_neighbor.handles, expected_merge_handles)
        self.assertEqual(right_neighbor.children_ids, expected_merge_children_ids)

    def test_merge_with_neighbor_leaf_nodes_right_neighbor_simple(self):
        tree = self.create_dummy_tree()
        byte_size = 2
        num_left_children = 3
        num_right_children = 5

        step_size = 10
        smallest_left_handle_int = 0
        biggest_left_handle_int = smallest_left_handle_int + (num_left_children - 2) * step_size
        smallest_right_handle_int = biggest_left_handle_int + step_size
        biggest_right_handle_int = smallest_right_handle_int + step_size * (num_right_children - 2)

        # To be extended with the corresponding children/split-keys etc later
        parent_node = TreeNode(is_internal_node=True)

        # Total of 5 children for parent node
        # The left merge neighbor (has a + 1 children)
        left_neighbor_handles = [create_string_from_int_with_byte_size(i, byte_size) for i in range(smallest_left_handle_int, biggest_left_handle_int + 1, step_size)]
        left_neighbor_children_ids = [f'l_{i}' for i in range(num_left_children)]
        left_neighbor = TreeNode(is_internal_node=False, handles=left_neighbor_handles, children=left_neighbor_children_ids, parent_id=parent_node.node_id)

        # The right merge neighbor (has a-1 children)
        right_neighbor_handles = [create_string_from_int_with_byte_size(i, byte_size) for i in range(smallest_right_handle_int, biggest_right_handle_int + 1, step_size)]
        right_neighbor_children_ids = [f'r_{i}' for i in range(num_right_children)]
        right_neighbor = TreeNode(is_internal_node=False, handles=right_neighbor_handles, children=right_neighbor_children_ids, parent_id=parent_node.node_id)

        disappearing_handle = create_string_from_int_with_byte_size(biggest_left_handle_int + step_size // 2, byte_size)

        # The parent node
        leaf_node_stubs = [TreeNode(is_internal_node=False).node_id for _ in range(3)]
        parents_children = leaf_node_stubs + [left_neighbor.node_id, right_neighbor.node_id]
        parent_handles = [f'sk_{i}' for i in range(3)] + [disappearing_handle]
        parent_node.children_ids = parents_children
        parent_node.handles = parent_handles

        # Pre-calculate expected results:
        expected_parent_handles = parent_handles[:-1]
        expected_children_ids_of_parent = leaf_node_stubs + [left_neighbor.node_id]

        expected_merge_handles = left_neighbor.handles + [disappearing_handle] + right_neighbor.handles
        expected_merge_children_ids = left_neighbor_children_ids + right_neighbor_children_ids

        left_neighbor.merge_with_neighbor(parent_node, right_neighbor, is_left_neighbor=False)

        # Is parent set correctly after merge
        self.assertEqual(expected_parent_handles, parent_node.handles)
        self.assertEqual(expected_children_ids_of_parent, parent_node.children_ids)

        # Is right neighbor set correctly after merge
        self.assertEqual(expected_merge_handles, left_neighbor.handles)
        self.assertEqual(expected_merge_children_ids, left_neighbor.children_ids)



    @staticmethod
    def create_dummy_tree():
        M = 4 * 4096
        B = 1024
        # m = 16 -> (a, b) = (4, 16)
        # (s, t) = (3, 6)
        return BufferTree(M=M, B_buffer=B)
