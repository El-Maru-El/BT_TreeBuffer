from bplus_tree.new_bplus_tree import *
from bplus_tree.bplus_helpers import get_dummy_infinity_child


def get_all_leaf_elements(tree: BPlusTree):
    elements = []
    root_node = load_node(tree.root_node_id, tree.root_node_type == NodeType.LEAF)
    recurse_through_tree(elements, root_node)

    return elements[:-1]


def recurse_through_tree(elements, current_node: BPlusTreeNode):
    if current_node.is_leaf():
        elements.extend()
    else:
        child_is_leaf = current_node.is_leaf_node()
        for child_id in current_node.children:
            child_node = load_node(child_id, child_is_leaf)
            recurse_through_tree(elements, child_node)
