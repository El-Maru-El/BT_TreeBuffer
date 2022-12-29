from current_implementation.new_buffer_tree import *
from unittest import TestCase

already_found_node_ids = set()


def assert_is_proper_tree(test_class: TestCase, tree: BufferTree):
    already_found_node_ids.clear()
    root_node = load_node(tree.root_node_id)
    is_proper_node(test_class, root_node)


def is_proper_node(test_class: TestCase, node: TreeNode):
    test_class.assertFalse(node.node_id in already_found_node_ids)
    tree = get_tree_instance()

    # Is amount of children in [0/2/a --- b]?
    test_class.assertGreaterEqual(len(node.children_ids), node.min_amount_of_children())
    test_class.assertGreaterEqual(tree.b, len(node.children_ids))

    # Is amount of children == amount of split-keys + 1?
    if node.is_root() and not node.is_internal_node() and len(node.children_ids) == 0:
        test_class.assertEqual([], node.handles, f"Root node {node} should not have split-keys when there is only one child left")
    else:
        test_class.assertEqual(len(node.handles) + 1, len(node.children_ids), f"Node {node} should have exactly one more child than split-keys")

    # Is there a parent pointer if we are not root node?
    if node.is_root():
        test_class.assertEqual(None, node.parent_id, f"Node data {node}")
    else:
        test_class.assertIsNotNone(node.parent_id, f"Node data {node}")

    # Are our split-keys in ascending order?
    for ind in range(len(node.handles) - 1):
        test_class.assertLess(node.handles[ind], node.handles[ind+1], f"Split-keys are not in ascending order\nNode data: {node}")

    if node.is_internal_node():
        is_proper_internal_node(test_class, node)
    else:
        is_proper_leaf_node(test_class, node)


def is_proper_internal_node(test_class: TestCase, node: TreeNode):
    loaded_children = [load_node(child_id) for child_id in node.children_ids]

    # Are either all children internal or all children leaf node?
    for index in range(len(loaded_children) - 1):
        left_node = loaded_children[index]
        right_node = loaded_children[index + 1]
        test_class.assertEqual(left_node.is_internal_node(), right_node.is_internal_node(), f"Nodes have different is_intern: left: \n{left_node} \nright: {right_node} \nparent: {node}")

    # Are the split-keys in child always proper according to our own split-keys?
    for ind in range(len(node.handles) - 1):
        left_parent_split_key, right_parent_split_key = node.handles[ind], node.handles[ind + 1]
        child_node = loaded_children[ind + 1]
        test_class.assertGreater(child_node.handles[0], left_parent_split_key, f"Child node {child_node} has split-key(s) too small for parent split-key {left_parent_split_key}\nParent: {node}")
        test_class.assertLessEqual(child_node.handles[-1], right_parent_split_key, f"Child node {child_node} has split-key(s) too big for parent split-key {right_parent_split_key}\nParent: {node}")
    first_child_node, last_child_node = loaded_children[0], loaded_children[-1]
    test_class.assertLessEqual(first_child_node.handles[-1], node.handles[0], f"Child node {first_child_node} has split-key(s) too big for parent split-key {node.handles[0]}\nParent: {node}")
    test_class.assertGreater(last_child_node.handles[0], node.handles[-1], f"Child node {last_child_node} has split-key(s) too small for parent split-key {node.handles[-1]}\nParent: {node}")

    # Do all children point to me as parent?
    for child_node in loaded_children:
        test_class.assertEqual(node.node_id, child_node.parent_id, f"Node {child_node} doesn't point to parent {node}")

    # Are all children proper nodes?
    for child_node in loaded_children:
        is_proper_node(test_class, child_node)


def is_proper_leaf_node(test_class, node: TreeNode):
    for ind in range(len(node.handles) - 1):
        left_split_key, right_split_key = node.handles[ind], node.handles[ind + 1]
        leaf_id = node.children_ids[ind+1]
        try:
            leaf_elements_deque = read_leaf_block_elements_as_deque(leaf_id)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Leaf node {node} has child-leaf with {leaf_id}, file for that does not exist") from e
        test_class.assertGreater(leaf_elements_deque[-1], left_split_key, f"Leaf block {leaf_id} has elements too small for parent split-key {left_split_key}\nParent: {node}")
        test_class.assertLess(leaf_elements_deque[0], right_split_key, f"Leaf block {leaf_id} has elements too big for parent split-key {right_split_key}\nParent: {node}")
        is_proper_leaf_block(test_class, leaf_elements_deque, leaf_id)


def is_proper_leaf_block(test_class, leaf_elements_deque, leaf_id):
    leaf_elements = list(leaf_elements_deque)
    for ind in range(len(leaf_elements) - 1):
        test_class.assertLess(leaf_elements[ind], leaf_elements[ind+1], f"Elements in leaf {leaf_id} are not ascending at index {ind}")
