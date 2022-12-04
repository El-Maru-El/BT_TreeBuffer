import unittest
from current_implementation.new_buffer_tree import ChildParent
from current_implementation.double_linked_list import DoublyLinkedList


class TestBasicStructure(unittest.TestCase):
    def setUp(self):
        self.linked_list = DoublyLinkedList()
        self.child_parent_string = ChildParent('1234', None)
        self.child_parent_int = ChildParent(1234, None)
        self.child_parent_third = ChildParent('another', None)

    def test_append(self):
        self.linked_list.append(self.child_parent_string)
        self.assertEqual(self.linked_list.num_elements, 1)
        self.assertEqual(self.linked_list.root.child_parent, self.child_parent_string)
        self.assertEqual(self.linked_list.last.child_parent, self.child_parent_string)
        self.assertEqual(self.linked_list.root.following, None)
        self.assertEqual(self.linked_list.root.prev, None)

        self.linked_list.append(self.child_parent_int)
        self.assertEqual(self.linked_list.num_elements, 2)
        self.assertEqual(self.linked_list.root.child_parent, self.child_parent_string)
        self.assertEqual(self.linked_list.last.child_parent, self.child_parent_int)
        self.assertEqual(self.linked_list.root.following.child_parent, self.child_parent_int)
        self.assertEqual(self.linked_list.last.prev.child_parent, self.child_parent_string)

        self.linked_list.append(self.child_parent_third)
        self.assertEqual(self.linked_list.num_elements, 3)
        self.assertEqual(self.linked_list.root.child_parent, self.child_parent_string)
        self.assertEqual(self.linked_list.root.following.child_parent, self.child_parent_int)
        self.assertEqual(self.linked_list.root.following.following.child_parent, self.child_parent_third)
        self.assertEqual(self.linked_list.last.child_parent, self.child_parent_third)

    def test_pop_first(self):
        self.linked_list.append(self.child_parent_string)
        self.linked_list.append(self.child_parent_int)

        first = self.linked_list.pop_first()
        self.assertEqual(first, self.child_parent_string)
        self.assertEqual(self.linked_list.num_elements, 1)
        self.assertIn(self.child_parent_int.child, self.linked_list.map)
        self.assertNotIn(self.child_parent_string.child, self.linked_list.map)

    def test_delete_inbetween(self):
        self.linked_list.append(self.child_parent_string)
        self.linked_list.append(self.child_parent_int)
        self.linked_list.append(self.child_parent_third)

        self.linked_list.find_and_delete_element(self.child_parent_int.child)
        self.assertEqual(self.linked_list.root.following.child_parent, self.child_parent_third)
        self.assertEqual(self.linked_list.last.prev, self.linked_list.root)

    def test_delete_last(self):
        self.linked_list.append(self.child_parent_string)
        self.linked_list.append(self.child_parent_int)
        self.linked_list.append(self.child_parent_third)

        self.linked_list.find_and_delete_element(self.child_parent_third.child)
        self.assertEqual(self.linked_list.last.child_parent, self.child_parent_int)
        self.assertEqual(self.linked_list.last.following, None)
