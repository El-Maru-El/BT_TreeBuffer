# Not needed: BufferTree: clear_full_internal_buffers - Not needed, just do clear_internal_buffer instead

# Not needed: BufferTree: clear_full_leaf_buffers in BufferTree - Not needed, just do clear_internal_buffer instead

# TODO BufferTree: handle_leaf_nodes_with_dummy_children: Complicated to test....

# TODO TreeNode:   buffer_is_full (I don't think I really have to...)

# TODO TreeNode:    clear_internal_buffer

# TODO TreeNode:    read_sort_and_remove_duplicates_from_buffer_files_with_read_size

# TODO TreeNode:    clear_leaf_buffer
#       under step:     -> prepare_buffer_blocks_into_manageable_sorted_files

# TODO TreeNode:    create_dummy_children

# TODO TreeNode:    insert_new_children                 Idea: Double Split on Leaf Node

# TODO TreeNode:    more tests for split_leaf_node/split_node

# TODO TreeNode:    identify_handles_and_split_keys_to_be_inserted

# TODO TreeNode:    merge_sorted_buffer_with_leaf_blocks        Note: 2 already existing, but more edge cases plz

# TODO TreeNode:    pass_elements_to_children (have 1)      Idea: Don't fill the last block. Also works?

# TODO TreeNode:    get_left_neighbor_id_for_child_id and get_right_neighbor_id_for_child_id

# TODO TreeNode:    read_leaf_block_elements_as_deque

# TODO TreeNode:    delete_dummy_blocks_from_leaf_node_until_too_few_children

# TODO TreeNode:    steal_or_merge
#   -> Subtest:         steal_from_neighbor
#       -> Subtest:         move_dummy_to_the_back_of_lists
#       -> Subtest:         delete_at_most_x_dummies
#   -> Subtest:         merge_with_neighbor (already has two tests, more required?)
#       -> Subtest:     delete_dummys_but_keep_min_children
#


# TODO TreeNode:    move_dummy_to_the_back_of_lists


