import unittest
from current_implementation.new_buffer_tree import *


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

