from current_implementation.new_buffer_tree import *
from current_implementation.create_comparable_string import create_string_from_int
import unittest


class TestNodeBuffer(unittest.TestCase):

    def setUp(self):
        clean_up_and_initialize_resource_directories()

    def test_add_elements_to_empty_node_buffer(self):
        tree = self.create_dummy_tree()

        fake_node = TreeNode(is_internal_node=False)
        node_id = fake_node.node_id

        biggest_int = tree.B_buffer // 2

        starting_buffer_elements = [BufferElement(create_string_from_int(i, biggest_int), Action.INSERT) for i in
                                    range(biggest_int)]

        fake_node.add_elements_to_buffer(elements=starting_buffer_elements)

        self.assertEqual(len(fake_node.buffer_block_ids), 1)

        reloaded_buffer_elements = read_buffer_block_elements(node_id, fake_node.buffer_block_ids[0])
        self.assertEqual(reloaded_buffer_elements, starting_buffer_elements)

    def test_add_elements_to_partially_filled_bufferblock(self):
        tree = self.create_dummy_tree()
        B = tree.B_buffer

        fake_node = TreeNode(is_internal_node=False)
        node_id = fake_node.node_id

        biggest_int = int(1.5 * tree.B_buffer)
        num_first_elements = tree.B_buffer // 2
        starting_elements = [BufferElement(create_string_from_int(i, biggest_int), Action.INSERT) for i in
                             range(num_first_elements)]
        fake_node.add_elements_to_buffer(elements=starting_elements)

        appending_elements = [BufferElement(create_string_from_int(i, biggest_int), Action.INSERT) for i in
                              range(num_first_elements, biggest_int)]
        fake_node.add_elements_to_buffer(elements=appending_elements)

        self.assertEqual(len(fake_node.buffer_block_ids), 2)

        reloaded_buffer_one = read_buffer_block_elements(node_id, fake_node.buffer_block_ids[0])
        reloaded_buffer_two = read_buffer_block_elements(node_id, fake_node.buffer_block_ids[1])

        self.assertNotEqual(fake_node.buffer_block_ids[0], fake_node.buffer_block_ids[1], 'Same buffer ids, wtf?....')
        self.assertEqual(reloaded_buffer_one, starting_elements + appending_elements[:B // 2])
        self.assertEqual(reloaded_buffer_two, appending_elements[B // 2:])
        self.assertEqual(fake_node.last_buffer_size, B // 2)

    def test_perfectly_fill_two_node_buffer_blocks(self):
        tree = self.create_dummy_tree()
        B = tree.B_buffer

        fake_node = TreeNode(is_internal_node=False)
        node_id = fake_node.node_id

        starting_elements = [BufferElement(f'Start_{i}', Action.INSERT) for i in range(B)]
        fake_node.add_elements_to_buffer(elements=starting_elements)

        appending_elements = [BufferElement(f'Append_{i}', Action.INSERT) for i in range(B)]
        fake_node.add_elements_to_buffer(elements=appending_elements)

        self.assertEqual(len(fake_node.buffer_block_ids), 2)
        self.assertEqual(fake_node.last_buffer_size, B)
        reloaded_buffer_one = read_buffer_block_elements(node_id, fake_node.buffer_block_ids[0])
        reloaded_buffer_two = read_buffer_block_elements(node_id, fake_node.buffer_block_ids[1])

        self.assertEqual(reloaded_buffer_one, starting_elements)
        self.assertEqual(reloaded_buffer_two, appending_elements)

    def test_perfectly_fill_node_buffer_block_in_two_steps(self):
        tree = self.create_dummy_tree()
        B = tree.B_buffer

        fake_node = TreeNode(is_internal_node=False)
        node_id = fake_node.node_id

        starting_elements = [BufferElement(f'Start_{i}', Action.INSERT) for i in range(B - 1)]
        fake_node.add_elements_to_buffer(elements=starting_elements)

        last_element = BufferElement(f'Ending_Element', Action.INSERT)
        fake_node.add_elements_to_buffer(elements=[last_element])

        self.assertEqual(len(fake_node.buffer_block_ids), 1)

        reloaded_buffer_elements = read_buffer_block_elements(node_id, fake_node.buffer_block_ids[0])
        self.assertEqual(reloaded_buffer_elements, starting_elements + [last_element])

    def test_slightly_overfill_one_node_buffer_block(self):
        tree = self.create_dummy_tree()
        B = tree.B_buffer

        fake_node = TreeNode(is_internal_node=False)
        node_id = fake_node.node_id

        starting_elements = [BufferElement(f'Start_{i}', Action.INSERT) for i in range(B - 1)]
        fake_node.add_elements_to_buffer(elements=starting_elements)

        appending_elements = [BufferElement(f'Append_{i}', Action.INSERT) for i in range(2)]
        fake_node.add_elements_to_buffer(elements=appending_elements)

        self.assertEqual(len(fake_node.buffer_block_ids), 2)

        reloaded_buffer_one = read_buffer_block_elements(node_id, fake_node.buffer_block_ids[0])
        reloaded_buffer_two = read_buffer_block_elements(node_id, fake_node.buffer_block_ids[1])

        self.assertEqual(reloaded_buffer_one, starting_elements + appending_elements[:1])
        self.assertEqual(reloaded_buffer_two, appending_elements[1:])

    def test_buffer_timestamps(self):
        buffer_elements = [BufferElement('SomeElement', Action.INSERT) for _ in range(100000)]
        for i in range(len(buffer_elements) - 1):
            self.assertLess(buffer_elements[i].timestamp, buffer_elements[i + 1].timestamp,
                            'Buffer timestamps are not smaller than each other')

    def test_writing_and_reading_node_buffer_elements(self):
        node_id = generate_new_node_dir()
        buffer_block_id = 'some_block_id'
        original_buffer_elements = [BufferElement('SomeElement', Action.INSERT) for _ in range(100000)]
        write_buffer_block(node_id, buffer_block_id, original_buffer_elements)
        reloaded_elements = read_buffer_block_elements(node_id, buffer_block_id)
        self.assertEqual(original_buffer_elements, reloaded_elements)

    def test_writing_and_reading_node_buffer_basic(self):
        fake_node = TreeNode(is_internal_node=False)
        elements = [BufferElement(str(i), Action.INSERT) for i in range(10)]
        buffer_block_id = fake_node.get_new_buffer_block_id()
        write_buffer_block(fake_node.node_id, buffer_block_id, elements)
        reloaded_elements = read_buffer_block_elements(fake_node.node_id, buffer_block_id)
        self.assertEqual(elements, reloaded_elements)

    @staticmethod
    def create_dummy_tree():
        M = 2 * 4096
        B = 1024

        return BufferTree(M=M, B_buffer=B)
