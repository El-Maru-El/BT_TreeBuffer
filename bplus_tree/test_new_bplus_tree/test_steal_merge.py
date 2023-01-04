import unittest
from bplus_tree.new_bplus_tree import *


class TestStealOrMerge(unittest.TestCase):

    def setUp(self):
        clean_up_and_initialize_resource_directories()

    def test_delete(self):
        children = ["1", "2", "3", "4", "99"]
        leaf_node = Leaf(children=children)
        leaf_node.leaf_delete_child_for_key("3")

        self.assertEqual(["1", "2", "4", "99"], leaf_node.children)


