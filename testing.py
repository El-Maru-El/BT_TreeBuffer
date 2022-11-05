from current_implementation.constants_and_helpers import *
from current_implementation.new_buffer_tree import *


def test_basic_node_stuff():
    new_node = TreeNode(is_internal_node=False)
    write_node(new_node)
    reloaded_node = load_node(new_node.node_timestamp)

    assert(new_node.__dict__ == reloaded_node.__dict__)


def test_actual_node_stuff():
    node_timestamp = get_current_timestamp()
    new_node = TreeNode(is_internal_node=True, handles=['abc', 'def'], children=[get_current_timestamp(), get_current_timestamp(), get_current_timestamp()])
    write_node(new_node)
    reloaded_node = load_node(node_timestamp)

    assert(new_node.__dict__ == reloaded_node.__dict__)
