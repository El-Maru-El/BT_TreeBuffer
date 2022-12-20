import unittest
from current_implementation.new_buffer_tree import *
from current_implementation.create_comparable_string import create_string_from_int


class TestTreeNode(unittest.TestCase):

    def setUp(self):
        clean_up_and_initialize_resource_directories()

    def test_annihilate_function(self):
        num_elements = 10
        buffer_elements_to_be_trimmed = [BufferElement(str(i), Action.INSERT) for i in range(num_elements)]
        expected_buffer_elements = buffer_elements_to_be_trimmed.copy()

        # Must be reverse sorted
        overwrite_indices = [len(buffer_elements_to_be_trimmed)-1, 5, 2, 0]
        self.assertGreater(overwrite_indices[0], overwrite_indices[1], 'Mistake in setting up test: overwrite indices should be reverse sorted')

        for ind in overwrite_indices:
            new_buffer_element = BufferElement(str(ind), Action.DELETE)
            buffer_elements_to_be_trimmed.insert(ind+1, new_buffer_element)
            expected_buffer_elements[ind] = new_buffer_element

        elements_trimmed = TreeNode.annihilate_insertions_deletions_with_matching_timestamps(buffer_elements_to_be_trimmed)

        self.assertEqual(elements_trimmed, expected_buffer_elements)

    def test_annihilate_function_on_empty_list(self):
        # Shouldn't be called with an empty list, but whatever
        TreeNode.annihilate_insertions_deletions_with_matching_timestamps([])

    def test_pass_elements_to_children(self):
        tree = self.create_dummy_tree()
        biggest_int = 400
        parent_node = TreeNode(is_internal_node=False)

        children_nodes = [TreeNode(is_internal_node=False, parent_id=parent_node.node_id), TreeNode(is_internal_node=False, parent_id=parent_node.node_id), TreeNode(is_internal_node=False, parent_id=parent_node.node_id)]
        for child_node in children_nodes:
            write_node(child_node)

        split_keys = [create_string_from_int(100, biggest_int), create_string_from_int(200, biggest_int)]
        children_node_ids = [child_node.node_id for child_node in children_nodes]

        parent_node.children_ids = children_node_ids
        parent_node.handles = split_keys

        elements_int = [10, 40, 100, 150, 200, 300, biggest_int]
        elements_str = [create_string_from_int(el_int, biggest_int) for el_int in elements_int]

        buffer_elements = [BufferElement(el_str, Action.INSERT) for el_str in elements_str]
        left_elements = buffer_elements[:3]
        middle_elements = buffer_elements[3:5]
        right_elements = buffer_elements[5:]
        parent_node.pass_elements_to_children(buffer_elements)

        [left_child, middle_child, right_child] = [load_node(node_id) for node_id in children_node_ids]
        self.assertEqual(len(left_child.buffer_block_ids), 1)
        self.assertEqual(len(middle_child.buffer_block_ids), 1)
        self.assertEqual(len(right_child.buffer_block_ids), 1)

        left_reloaded_buffer = read_buffer_block_elements(left_child.node_id, left_child.buffer_block_ids[0])
        middle_reloaded_buffer = read_buffer_block_elements(middle_child.node_id, middle_child.buffer_block_ids[0])
        right_reloaded_buffer = read_buffer_block_elements(right_child.node_id, right_child.buffer_block_ids[0])

        self.assertEqual(left_reloaded_buffer, left_elements)
        self.assertEqual(middle_reloaded_buffer, middle_elements)
        self.assertEqual(right_reloaded_buffer, right_elements)


    @staticmethod
    def create_dummy_tree():
        M = 2 * 4096
        B = 1024

        return BufferTree(M=M, B=B)
