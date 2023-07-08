from current_implementation.new_buffer_tree import *
from current_implementation.create_comparable_string import create_string_from_int_biggest_number
import unittest


class TestNodeBufferEmptying(unittest.TestCase):

    def setUp(self):
        clean_up_and_initialize_resource_directories()

    def test_empty_node_with_empty_buffer(self):
        tree = self.create_dummy_tree()
        root_node = load_node(tree.root_node_id)
        fake_children_nodes = [TreeNode(is_internal_node=True, parent_id=root_node.node_id), TreeNode(is_internal_node=True, parent_id=root_node.node_id)]

        write_node(fake_children_nodes[0]), write_node(fake_children_nodes[1])
        children_node_ids = fake_children_nodes[0].node_id, fake_children_nodes[1].node_id
        root_node.is_intern = True
        root_node.children_ids = children_node_ids
        root_node.handles = ['Fake-Split-Key']
        root_node.clear_internal_buffer(enforce_buffer_emptying_enabled=False)

        self.assertEqual([], root_node.buffer_block_ids)
        self.assertEqual([], load_node(children_node_ids[0]).buffer_block_ids)
        self.assertEqual([], load_node(children_node_ids[1]).buffer_block_ids)
        self.assertEqual(0, len(tree.internal_node_buffer_emptying_queue))

        root_node.clear_internal_buffer(enforce_buffer_emptying_enabled=True)

        self.assertEqual([], root_node.buffer_block_ids)
        self.assertEqual([], load_node(children_node_ids[0]).buffer_block_ids)
        self.assertEqual([], load_node(children_node_ids[1]).buffer_block_ids)
        self.assertTrue(children_node_ids[0] in tree.internal_node_buffer_emptying_queue)
        self.assertTrue(children_node_ids[1] in tree.internal_node_buffer_emptying_queue)

    def test_partially_filled_buffer(self):
        tree = self.create_dummy_tree()
        biggest_int = tree.B_buffer
        first_split_key_int, second_split_key_int, third_split_key = 100, 200, 300
        split_keys = [create_string_from_int_biggest_number(first_split_key_int, biggest_int), create_string_from_int_biggest_number(second_split_key_int, biggest_int), create_string_from_int_biggest_number(third_split_key, biggest_int)]
        fake_children_nodes = [TreeNode(is_internal_node=True, parent_id=tree.root_node_id), TreeNode(is_internal_node=True, parent_id=tree.root_node_id),
                               TreeNode(is_internal_node=True, parent_id=tree.root_node_id), TreeNode(is_internal_node=True, parent_id=tree.root_node_id)]
        for child_node in fake_children_nodes:
            write_node(child_node)

        children_node_ids = [node.node_id for node in fake_children_nodes]
        elements_int = [30, 300, 220, 40, 250]

        buffer_elements = [BufferElement(create_string_from_int_biggest_number(i, biggest_int), Action.INSERT) for i in elements_int]
        sorted_buffer_elements = sorted(buffer_elements, key=lambda x: x.element)

        root_node = load_node(tree.root_node_id)
        root_node.is_intern = True
        root_node.children_ids = children_node_ids
        root_node.handles = split_keys
        root_node.add_elements_to_buffer(buffer_elements)

        root_node.clear_internal_buffer(enforce_buffer_emptying_enabled=False)
        reloaded_children_nodes = [load_node(node_id) for node_id in children_node_ids]

        self.assertEqual(1, len(reloaded_children_nodes[0].buffer_block_ids))
        self.assertEqual(0, len(reloaded_children_nodes[1].buffer_block_ids))
        self.assertEqual(1, len(reloaded_children_nodes[2].buffer_block_ids))
        self.assertEqual(0, len(reloaded_children_nodes[3].buffer_block_ids))
        reloaded_buffer_first_child = read_buffer_block_elements(children_node_ids[0], reloaded_children_nodes[0].buffer_block_ids[0])
        self.assertEqual(sorted_buffer_elements[:2], reloaded_buffer_first_child)
        reloaded_buffer_third_child = read_buffer_block_elements(children_node_ids[2], reloaded_children_nodes[2].buffer_block_ids[0])
        self.assertEqual(sorted_buffer_elements[2:], reloaded_buffer_third_child)

    def test_overfull_internal_buffer_leading_to_full_internal_child_node(self):
        tree = self.create_dummy_tree()
        biggest_int = tree.m * tree.B_buffer
        buffer_elements = deque([BufferElement(create_string_from_int_biggest_number(i, biggest_int), Action.INSERT) for i in reversed(range(biggest_int))])

        buffer_elements_sorted = sorted(buffer_elements, key=lambda x: x.element)

        parent_node = TreeNode(is_internal_node=True, handles=[create_string_from_int_biggest_number(biggest_int + 1, biggest_int)])
        elements_in_block = []
        while buffer_elements:
            elements_in_block.append(buffer_elements.popleft())
            if len(elements_in_block) == tree.B_buffer:
                parent_node.add_elements_to_buffer(elements_in_block)

        if elements_in_block:
            parent_node.add_elements_to_buffer(elements_in_block)

        children_nodes = [TreeNode(is_internal_node=True, parent_id=parent_node.node_id) for _ in range(2)]
        for child_node in children_nodes:
            write_node(child_node)
        parent_node.children_ids = [child_node.node_id for child_node in children_nodes]

        parent_node.clear_internal_buffer(enforce_buffer_emptying_enabled=False)
        reloaded_left_child, reloaded_right_child = load_node(children_nodes[0].node_id), load_node(children_nodes[1].node_id)

        self.assertEqual(0, len(reloaded_right_child.buffer_block_ids))
        self.assertEqual(tree.m, len(reloaded_left_child.buffer_block_ids))
        reloaded_buffer_elements = reloaded_left_child.read_sort_and_remove_duplicates_from_buffer_files_with_read_size(tree.m)
        self.assertEqual(buffer_elements_sorted, reloaded_buffer_elements)

    @staticmethod
    def create_dummy_tree():
        M = 2 * 4096
        B = 1024

        return BufferTree(M=M, B_buffer=B)
