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

    def test_merge_sorted_buffer_with_leaf_blocks(self):
        tree = self.create_dummy_tree()
        biggest_int = tree.B * 4
        old_leaf_ids = [generate_new_leaf_id(), generate_new_leaf_id()]

        # First leaf block:     All even numbers in interval    [0; 2 * B[
        # Second leaf block:    All even numbers in interval    [2 * B, 4 * B[
        # Sorted buffer ele:    All uneven numbers in interval  [0; 4 * B]
        first_leaf_elements = [create_string_from_int(i, biggest_int) for i in range(0, 2 * tree.B, 2)]
        second_leaf_elements = [create_string_from_int(i, biggest_int) for i in range(2 * tree.B, 4 * tree.B, 2)]
        sorted_buffer_elements = [BufferElement(create_string_from_int(i, biggest_int), Action.INSERT) for i in range(1, 4 * tree.B + 1, 2)]

        quick_check_failure_message = 'You did not implement the input Leaf and Buffer Data as intended'
        self.assertEqual(len(first_leaf_elements), tree.B, quick_check_failure_message)
        self.assertEqual(len(second_leaf_elements), tree.B, quick_check_failure_message)
        self.assertEqual(len(sorted_buffer_elements), 2 * tree.B, quick_check_failure_message)

        write_leaf_block(old_leaf_ids[0], first_leaf_elements)
        write_leaf_block(old_leaf_ids[1], second_leaf_elements)
        leaf_node = TreeNode(is_internal_node=False, children=old_leaf_ids, handles=first_leaf_elements[-1])
        sorted_id = get_new_sorted_id()
        append_to_sorted_buffer_elements_file(leaf_node.node_id, sorted_id, sorted_buffer_elements)

        sorted_filepath = get_sorted_file_path_from_ids(leaf_node.node_id, sorted_id)
        leaf_node.merge_sorted_buffer_with_leaf_blocks(sorted_filepath)

        all_elements_before_unsorted = []
        all_elements_before_unsorted.extend(first_leaf_elements)
        all_elements_before_unsorted.extend(second_leaf_elements)
        for buffer_element in sorted_buffer_elements:
            all_elements_before_unsorted.append(buffer_element.element)

        sorted_elements_before_writing = sorted(all_elements_before_unsorted)

        # Is node metadata correct?
        expected_split_keys = [create_string_from_int(i, biggest_int) for i in [tree.B - 1, 2 * tree.B - 1, 3 * tree.B - 1]]
        self.assertEqual(len(leaf_node.children_ids), 4)
        self.assertEqual(expected_split_keys, leaf_node.handles)

        reloaded_leaf_lists = [list(read_leaf_block_elements_as_deque(leaf_id)) for leaf_id in leaf_node.children_ids]
        reloaded_leaf_elements = [element for sublist in reloaded_leaf_lists for element in sublist]

        # Are each of the new Leaf IDs correct?
        self.assertEqual(reloaded_leaf_lists[0], sorted_elements_before_writing[:tree.B])
        self.assertEqual(reloaded_leaf_lists[1], sorted_elements_before_writing[tree.B:2 * tree.B])
        self.assertEqual(reloaded_leaf_lists[2], sorted_elements_before_writing[2 * tree.B:3 * tree.B])
        self.assertEqual(reloaded_leaf_lists[3], sorted_elements_before_writing[3 * tree.B:4 * tree.B])
        self.assertEqual(sorted_elements_before_writing, reloaded_leaf_elements)

        # Have the corresponding files been deleted?
        file_not_deleted_message = 'File should have been deleted'
        for leaf_id in old_leaf_ids:
            self.assertFalse(os.path.exists(get_leaf_file_path_from_id(leaf_id)), file_not_deleted_message)
        self.assertFalse(os.path.exists(get_sorted_file_path_from_ids(leaf_node.node_id, sorted_id)))

    def test_merge_on_empty_root_node(self):
        # TODO
        pass

    @staticmethod
    def create_dummy_tree():
        M = 2 * 4096
        B = 1024

        return BufferTree(M=M, B=B)

    def assert_list_is_incrementing_by_1(self, some_list_of_strings, failure_message):
        for i in range(1, len(some_list_of_strings)):
            self.assertEqual(int(some_list_of_strings[i-1]) + 1, int(some_list_of_strings[i]), failure_message)
