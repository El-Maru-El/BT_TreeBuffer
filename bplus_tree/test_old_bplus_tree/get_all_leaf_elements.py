from bplus_tree.bplus_tree import *
from bplus_tree.bplus_helpers import get_dummy_infinity_child


def get_all_leaf_elements(tree: BPlusTree):
    if tree.root_node_id is None:
        return []

    elements = []
    root_node = load_node(tree.root_node_id)
    recurse_through_tree(elements, root_node)
    # Cuts off dummy element at the end
    if elements[-1] != get_dummy_infinity_child():
        raise ValueError(f"Last child of elements is not dummy child. But it should be! Found Leaf Elements:\n{elements}")

    return elements[:-1]


def recurse_through_tree(elements, current_node:BPlusTreeNode):
    if current_node.is_internal_node:
        for child_id in current_node.children:
            child_node = load_node(child_id)
            recurse_through_tree(elements, child_node)
    else:
        elements.extend(current_node.children)
