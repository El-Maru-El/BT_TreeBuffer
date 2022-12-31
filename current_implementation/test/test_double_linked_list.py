import unittest
from current_implementation.double_linked_list import DoublyLinkedList


class TestDoubleLinkedList(unittest.TestCase):
    def setUp(self):
        self.linked_list = DoublyLinkedList()
        self.node_id_string = '1234'
        self.node_id_other_string = '5678'
        self.node_id_third = 'another'

    def test_append(self):
        self.linked_list.append_to_custom_list(self.node_id_string)
        self.assertEqual(self.linked_list.num_elements, 1)
        self.assertEqual(self.linked_list.first.node_id, self.node_id_string)
        self.assertEqual(self.linked_list.last.node_id, self.node_id_string)
        self.assertEqual(self.linked_list.first.following, None)
        self.assertEqual(self.linked_list.first.prev, None)

        self.linked_list.append_to_custom_list(self.node_id_other_string)
        self.assertEqual(self.linked_list.num_elements, 2)
        self.assertEqual(self.linked_list.first.node_id, self.node_id_string)
        self.assertEqual(self.linked_list.last.node_id, self.node_id_other_string)
        self.assertEqual(self.linked_list.first.following.node_id, self.node_id_other_string)
        self.assertEqual(self.linked_list.last.prev.node_id, self.node_id_string)

        self.linked_list.append_to_custom_list(self.node_id_third)
        self.assertEqual(self.linked_list.num_elements, 3)
        self.assertEqual(self.linked_list.first.node_id, self.node_id_string)
        self.assertEqual(self.linked_list.first.following.node_id, self.node_id_other_string)
        self.assertEqual(self.linked_list.first.following.following.node_id, self.node_id_third)
        self.assertEqual(self.linked_list.last.node_id, self.node_id_third)

    def test_pop_first(self):
        self.linked_list.append_to_custom_list(self.node_id_string)
        self.linked_list.append_to_custom_list(self.node_id_other_string)

        first = self.linked_list.pop_first()
        self.assertEqual(first, self.node_id_string)
        self.assertEqual(self.linked_list.num_elements, 1)
        self.assertIn(self.node_id_other_string, self.linked_list.map)
        self.assertNotIn(self.node_id_string, self.linked_list.map)

    def test_delete_inbetween(self):
        self.linked_list.append_to_custom_list(self.node_id_string)
        self.linked_list.append_to_custom_list(self.node_id_other_string)
        self.linked_list.append_to_custom_list(self.node_id_third)

        self.linked_list.find_and_delete_element(self.node_id_other_string)
        self.assertEqual(self.linked_list.first.following.node_id, self.node_id_third)
        self.assertEqual(self.linked_list.last.prev, self.linked_list.first)

    def test_delete_last(self):
        self.linked_list.append_to_custom_list(self.node_id_string)
        self.linked_list.append_to_custom_list(self.node_id_other_string)
        self.linked_list.append_to_custom_list(self.node_id_third)

        self.linked_list.find_and_delete_element(self.node_id_third)
        self.assertEqual(self.linked_list.last.node_id, self.node_id_other_string)
        self.assertEqual(self.linked_list.last.following, None)
