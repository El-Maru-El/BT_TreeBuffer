from current_implementation.new_buffer_tree import BufferTree, TreeNode, load_node, read_leaf_block_elements_as_deque


def get_all_leaf_elements_in_sorted_list(buffer_tree: BufferTree) -> list:
    root_node = load_node(buffer_tree.root_node_id)
    existing_elements_list = list()

    traverse_nodes_and_extend_list(root_node, existing_elements_list)

    return existing_elements_list


def traverse_nodes_and_extend_list(node: TreeNode, existing_elements_list):
    if node.is_internal_node():
        for child_id in node.children_ids:
            child_node = load_node(child_id)
            traverse_nodes_and_extend_list(child_node, existing_elements_list)
    else:
        add_all_leaf_elements_to_list(node, existing_elements_list)


def add_all_leaf_elements_to_list(leaf_node: TreeNode, existing_elements_list: list):
    for leaf_id in leaf_node.children_ids:
        leaf_elements = read_leaf_block_elements_as_deque(leaf_id)
        for element in leaf_elements:
            existing_elements_list.append(element)
