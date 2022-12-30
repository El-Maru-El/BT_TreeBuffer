import itertools
import math
from current_implementation.buffer_element import *
from current_implementation.constants_and_helpers import *
from current_implementation.double_linked_list import DoublyLinkedList
from current_implementation.merge_sort import external_merge_sort_buffer_elements_many_files
from collections import deque


class BufferTree:

    """ Static reference to the tree. Useful for when calculating something for a node requires tree properties."""
    tree_instance = None

    def __init__(self, M, B):
        clean_up_and_initialize_resource_directories()
        self.M = M
        self.B = B
        m = M // B
        if m % 4 != 0:
            raise ValueError('m = lowerbound(M/B) is not dividable by four. '
                             'This is required to calculate a and b for the underlying a-b-tree Structure.')
        self.m = m
        self.b = m
        self.a = m // 4
        self.s = BufferTree.calculate_s(self.a, self.b)
        self.t = BufferTree.calculate_t(self.a, self.b, self.s)

        root_node = TreeNode(is_internal_node=False, handles=[], children=[], buffer_block_ids=[])
        self.root_node_id = root_node.node_id
        self.tree_buffer = TreeBuffer(max_size=self.B)
        self.internal_node_buffer_emptying_queue = deque()
        self.leaf_node_buffer_emptying_queue = DoublyLinkedList()
        self.node_to_split_queue = deque()
        # No leaf node can be in this buffer emptying queue twice at the same time, since _all_ full Buffers get deleted before any steal/merges are performed. BUT: In case of merging with a neighbor node, the neighboring node has to be deleted from this list (if present in it)
        self.leaf_nodes_with_dummy_children = DoublyLinkedList()
        self.node_to_steal_or_merge_queue = deque()

        BufferTree.tree_instance = self
        write_node(root_node)

    @staticmethod
    def calculate_s(a, b):
        tmp = (b // 2) - a + 1
        return math.ceil(tmp/2)

    @staticmethod
    def calculate_t(a, b, s):
        return (b // 2) - a + s - 1

    def insert_to_tree(self, ele):
        self.tree_buffer.insert_new_element(ele, Action.INSERT)
        self.check_tree_buffer()

    def delete_from_tree(self, ele):
        self.tree_buffer.insert_new_element(ele, Action.DELETE)
        self.check_tree_buffer()

    def check_tree_buffer(self):
        if self.tree_buffer.is_full():
            # TODO This could be done more efficiently, since this Block is first written then immediately read again if buffer is full
            root = self.push_internal_buffer_to_root_return_root()

            if root.buffer_is_full():
                # At this point the queues should still be empty, so no checks to whether root is already present are necessary
                if root.is_internal_node():
                    self.internal_node_buffer_emptying_queue.append(root.node_id)
                else:
                    self.leaf_node_buffer_emptying_queue.append_to_custom_list(root.node_id)
                self.clear_all_buffers_and_rebalance()

    def push_internal_buffer_to_root_return_root(self):
        root = load_node(self.root_node_id)
        root.add_block_to_buffer(self.tree_buffer.get_elements())
        write_node(root)
        self.tree_buffer.clear_elements()

        return root

    def flush_all_buffers(self):
        root = self.push_internal_buffer_to_root_return_root()
        root.add_self_to_buffer_emptying_queue()
        self.clear_all_buffers_and_rebalance(enforce_buffer_emptying_enabled=True)

    def clear_all_buffers_and_rebalance(self, enforce_buffer_emptying_enabled=False):
        self.clear_all_buffers_only(enforce_buffer_emptying_enabled)
        self.handle_leaf_nodes_with_dummy_children()

    def clear_all_buffers_only(self, enforce_buffer_emptying_enabled=False):
        self.clear_full_internal_buffers(enforce_buffer_emptying_enabled)
        self.clear_full_leaf_buffers()

    def clear_full_internal_buffers(self, enforce_buffer_emptying_enabled):
        while self.internal_node_buffer_emptying_queue:
            node_id = self.internal_node_buffer_emptying_queue.popleft()
            node = load_node(node_id)
            node.clear_internal_buffer(enforce_buffer_emptying_enabled)
            write_node(node)

    def clear_full_leaf_buffers(self):
        while not self.leaf_node_buffer_emptying_queue.is_empty():
            node_id = self.leaf_node_buffer_emptying_queue.pop_first()
            node = load_node(node_id)

            node.clear_leaf_buffer()

            write_node(node)

    def handle_leaf_nodes_with_dummy_children(self):
        def load_parent_neighbor_left(node: TreeNode):
            loaded_parent_node = load_node(node.parent_id)
            is_left = True
            some_neighbor_id = loaded_parent_node.get_left_neighbor_id_for_child_id(node.node_id)
            if not some_neighbor_id:
                is_left = False
                some_neighbor_id = loaded_parent_node.get_right_neighbor_id_for_child_id(node.node_id)
            loaded_neighbor = load_node(some_neighbor_id)
            return loaded_parent_node, loaded_neighbor, is_left

        # If there are nodes with too few children -> Handle those first
        # If there are leaf nodes with dummy children -> Delete dummy until it has too few children
        while not self.leaf_nodes_with_dummy_children.is_empty() or self.node_to_steal_or_merge_queue:
            if len(self.node_to_steal_or_merge_queue) > 1:
                raise ValueError(f'Steal or merge queue has more than 1 element, this should not happen: queue is {self.node_to_steal_or_merge_queue}')
            if self.node_to_steal_or_merge_queue:
                node_id = self.node_to_steal_or_merge_queue[0]
                loaded_node = load_node(node_id)
                if not loaded_node.is_root():
                    parent_node, neighbor_node, is_left_neighbor = load_parent_neighbor_left(loaded_node)
                    if neighbor_node.has_buffer_elements():
                        neighbor_node.add_self_to_buffer_emptying_queue()

                        # No need to write any nodes (we didn't change anything yet), just empty all buffers and go to next iteration
                        self.clear_all_buffers_only()
                        continue
                    else:
                        # Neighbor already has an empty buffer, so we can execute steal or merge and decrease the queue!
                        self.node_to_steal_or_merge_queue.popleft()
                        loaded_node.steal_or_merge(parent_node, neighbor_node, is_left_neighbor)
                else:
                    self.node_to_steal_or_merge_queue.popleft()
                    loaded_node.root_node_is_too_small()
            else:
                # No more steal/merges to perform, so delete another dummy child
                leaf_node_id = self.leaf_nodes_with_dummy_children.pop_first()
                leaf_node = load_node(leaf_node_id)
                leaf_node.delete_dummy_blocks_from_leaf_node_until_too_few_children()
                write_node(leaf_node)


class TreeNode:
    def __init__(self, is_internal_node, node_id=None, handles=None, children=None, buffer_block_ids=None, last_buffer_size=0, parent_id=None):

        if node_id is None:
            node_id = generate_new_node_dir()

        if buffer_block_ids is None:
            buffer_block_ids = []

        if handles is None:
            handles = []

        if children is None:
            children = []

        self.node_id = node_id

        self.handles = handles
        self.children_ids = children
        self.is_intern = is_internal_node
        self.buffer_block_ids = buffer_block_ids
        self.last_buffer_size = last_buffer_size
        self.parent_id = parent_id

    # Only for debugging purposes
    def __str__(self):
        node_dict = self.__dict__
        return f'{self.node_id}: {node_dict}'

    # Only for debugging purposes
    def __repr__(self):
        return self.__str__()

    def get_new_buffer_block_id(self):
        return generate_new_buffer_block_id(len(self.buffer_block_ids))

    def is_internal_node(self):
        return self.is_intern

    def add_block_to_buffer(self, elements):
        # Does not write itself back to ext. memory, but does write the buffer blocks to ext. memory
        buffer_block_id = self.get_new_buffer_block_id()

        self.buffer_block_ids.append(buffer_block_id)
        self.last_buffer_size = len(elements)
        write_buffer_block(self.node_id, buffer_block_id, elements)

    def add_elements_to_buffer(self, elements):
        tree = get_tree_instance()
        if self.buffer_block_ids and self.last_buffer_size < tree.B:
            elements_to_add = min(len(elements), tree.B - self.last_buffer_size)
            append_to_buffer(self.node_id, self.buffer_block_ids[-1], elements[:elements_to_add])
            self.last_buffer_size += elements_to_add
            start_index = elements_to_add
        else:
            start_index = 0

        while start_index < len(elements):
            elements_to_add = min(len(elements) - start_index, tree.B)
            buffer_block_id = self.get_new_buffer_block_id()
            write_buffer_block(self.node_id, buffer_block_id, elements[start_index:start_index + elements_to_add])
            self.buffer_block_ids.append(buffer_block_id)

            start_index += elements_to_add
            self.last_buffer_size = elements_to_add

        return self.buffer_is_full()

    def buffer_is_full(self):
        tree = get_tree_instance()
        if self.is_root():
            limit = (tree.m // 2) - 1
        # Following have the same max. Buffer Size, so we could summarize those later
        elif self.is_internal_node():
            limit = tree.m // 2
        else:
            limit = tree.m // 2

        return len(self.buffer_block_ids) > limit

    def has_buffer_elements(self):
        return len(self.buffer_block_ids) > 0

    def is_root(self):
        return get_tree_instance().root_node_id == self.node_id

    def clear_internal_buffer(self, enforce_buffer_emptying_enabled):
        def determine_if_all_children_are_internal_nodes():
            first_child = load_node(self.children_ids[0])
            return first_child.is_internal_node()

        def add_children_ids_to_buffer_emptying_queue(children_ids, are_internal_nodes):
            tree = get_tree_instance()
            if are_internal_nodes is None:
                are_internal_nodes = determine_if_all_children_are_internal_nodes()
            for some_child_id in children_ids:
                if are_internal_nodes:
                    tree.internal_node_buffer_emptying_queue.appendleft(some_child_id)
                else:
                    tree.leaf_node_buffer_emptying_queue.append_to_custom_list(some_child_id)

        if not self.is_internal_node():
            raise ValueError(f"Tried clearing internal buffer on node {self.node_id}, but this node is a leaf node.\n:Children-Ids: {self.children_ids}\nParent-id: {self.parent_id}")

        read_size = get_tree_instance().m // 2

        children_ids_with_full_buffers = set()
        all_children_are_internal_nodes = None

        while self.buffer_block_ids:
            elements = self.read_sort_and_remove_duplicates_from_buffer_files_with_read_size(read_size)
            new_full_children_ids, all_children_are_internal_nodes = self.pass_elements_to_children(elements)
            children_ids_with_full_buffers.update(new_full_children_ids)

        if enforce_buffer_emptying_enabled:
            add_children_ids_to_buffer_emptying_queue(self.children_ids, all_children_are_internal_nodes)
        else:
            add_children_ids_to_buffer_emptying_queue(children_ids_with_full_buffers, all_children_are_internal_nodes)

        self.last_buffer_size = 0

    def read_sort_and_remove_duplicates_from_buffer_files_with_read_size(self, read_size):
        """ Read_size = How many files to read at once. Also deletes the buffer blocks from external memory and modifies self.buffer_block_ids. """
        blocks_to_read = self.buffer_block_ids[:read_size]
        self.buffer_block_ids = self.buffer_block_ids[read_size:]
        elements = load_buffer_blocks_sort_and_remove_duplicates(self.node_id, blocks_to_read)

        delete_several_buffer_files_with_ids(self.node_id, blocks_to_read)
        return elements

    def clear_leaf_buffer(self):
        if self.is_internal_node():
            raise ValueError(f"Called clearing leaf buffer for node {self.node_id}, but this node is an internal node.\nChildren-Ids: {self.children_ids}\nParent-Id: {self.parent_id}")

        # self node is written in callee
        tree = get_tree_instance()

        num_children_before = len(self.children_ids)

        # In case we have an empty buffer, sorted_ids will be []
        sorted_ids = self.prepare_buffer_blocks_into_manageable_sorted_files()
        sorted_filepath = external_merge_sort_buffer_elements_many_files(self.node_id, sorted_ids, tree.M)
        self.last_buffer_size = 0

        self.merge_sorted_buffer_with_leaf_blocks(sorted_filepath)

        if len(self.children_ids) > num_children_before:
            handle_child_id_tuples = self.identify_handles_and_split_keys_to_be_inserted(num_children_before)
            self.insert_new_children(handle_child_id_tuples=handle_child_id_tuples)

        elif len(self.children_ids) < num_children_before:
            if len(self.children_ids) < self.min_amount_of_children():
                self.create_dummy_children()
                tree.leaf_nodes_with_dummy_children.append_to_custom_list(self.node_id)

            # Else: We should be good otherwise, we don't have to re-balance since we still have a(or 0 if root) <= num_children <= b

    def create_dummy_children(self):
        if len(self.handles) + 1 != len(self.children_ids) and not len(self.children_ids) == 0:
            raise ValueError(f"Trying to append dummy elements to node {self.node_id}, but amount of split-keys + 1 != amount of children, even though there is more than zero children \nNode data: {self}")
        # Self node has less than a children, so create dummy children ids and split keys until self node has exactly a children
        tree = get_tree_instance()
        while(len(self.handles)) < tree.a - 1:
            self.handles.append(DUMMY_STRING)
        while(len(self.children_ids)) < tree.a:
            self.children_ids.append(DUMMY_STRING)

        # So in general: handles[i] == DUMMY <-> children_ids[i + 1] == DUMMY
        # EXCEPTION: children_ids[0] == DUMMY is a special case

    def insert_new_children(self, handle_child_id_tuples):
        # self node is written in callee

        tree = get_tree_instance()
        for split_key, child_id in handle_child_id_tuples:
            self.handles.append(split_key)
            self.children_ids.append(child_id)
            if len(self.children_ids) > tree.b:
                self.split_leaf_node()

    def split_leaf_node(self):
        # self node is written in callee

        self.split_node()
        tree = get_tree_instance()
        while tree.node_to_split_queue:
            node_instance_to_be_split = tree.node_to_split_queue.popleft()
            node_instance_to_be_split.split_node()
            write_node(node_instance_to_be_split)

    def split_node(self, loaded_child_node=None):
        # self node is written somewhere in callee
        tree = get_tree_instance()
        if len(self.handles) != tree.b or len(self.children_ids) != tree.b + 1:
            raise ValueError(f"Tried splitting node {self.node_id}, but: b = {tree.b}, num handles = {len(self.handles)}, num children = {len(self.children_ids)}")

        tree = get_tree_instance()
        if self.is_root():
            # Create new root
            parent_node = TreeNode(is_internal_node=True, children=[self.node_id])
            self.parent_id = parent_node.node_id
            tree.root_node_id = parent_node.node_id
        else:
            parent_node = load_node(self.parent_id)

        # Since b % 4 == 0, we know:
        #   len(self.children_ids) = b + 1 = odd
        #   -> len(self.handles) = b = even

        num_children_for_left_neighbor = tree.b // 2
        # Since the most-right split-key of the left half of self.handles goes to parent:
        num_handles_for_left_neighbor = (tree.b // 2) - 1

        handle_for_parent = self.handles[tree.b // 2 - 1]

        handles_for_left_neighbor = self.handles[:num_handles_for_left_neighbor]
        self.handles = self.handles[1 + num_handles_for_left_neighbor:]

        children_ids_for_left_neighbor = self.children_ids[:num_children_for_left_neighbor]
        self.children_ids = self.children_ids[num_children_for_left_neighbor:]

        new_left_neighbor_node = TreeNode(is_internal_node=self.is_internal_node(), handles=handles_for_left_neighbor, children=children_ids_for_left_neighbor, parent_id=self.parent_id)

        index_in_parent = parent_node.index_for_child_id(self.node_id)
        parent_node.children_ids.insert(index_in_parent, new_left_neighbor_node.node_id)
        parent_node.handles.insert(index_in_parent, handle_for_parent)

        write_node(new_left_neighbor_node)

        if self.is_internal_node():
            write_node(self)

        if len(parent_node.children_ids) > tree.b:
            if not self.is_internal_node():
                parent_node.split_node(loaded_child_node=self)
            else:
                tree.node_to_split_queue.append(parent_node)
        else:
            # Parent didn't split, so we write it back to ext. memory ourselves:
            write_node(parent_node)

        # If we are not a Leaf Node, update the parent-reference of all children
        if self.is_internal_node():
            for passed_child_id in children_ids_for_left_neighbor:

                # The child is the Leaf-Node that called us to split, so it has a running instance that wants to be updated
                if loaded_child_node and loaded_child_node.node_id == passed_child_id:
                    loaded_child_node.parent_id = new_left_neighbor_node.node_id
                else:
                    passed_child_node = load_node(passed_child_id)
                    passed_child_node.parent_id = new_left_neighbor_node.node_id
                    write_node(passed_child_node)

    def index_for_child_id(self, find_id):
        return self.children_ids.index(find_id)

    def identify_handles_and_split_keys_to_be_inserted(self, num_children_before):
        if num_children_before > 0:
            # num_to_be_inserted will always be > 0, so the list trimming will work find
            num_to_be_inserted = len(self.children_ids) - num_children_before
            split_keys_to_be_inserted = self.handles[-num_to_be_inserted:]
            self.handles = self.handles[:num_children_before - 1]
            children_to_be_inserted = self.children_ids[-num_to_be_inserted:]
            self.children_ids = self.children_ids[:num_children_before]
        else:
            # len(self.children_ids) - num_children_before == 0
            split_keys_to_be_inserted = self.handles
            self.handles = []
            children_to_be_inserted = self.children_ids[1:]
            self.children_ids = self.children_ids[:1]

        if len(split_keys_to_be_inserted) != len(children_to_be_inserted):
            raise ValueError("Something was implemented incorrectly in this method, split-keys and children-ids to be inserted are of different length")

        return list(zip(split_keys_to_be_inserted, children_to_be_inserted))

    def merge_sorted_buffer_with_leaf_blocks(self, sorted_filepath):
        def new_leaf():
            new_leaf_id = generate_new_leaf_id()
            new_split_keys.append(new_leaf_block_elements[-1])
            new_leaf_ids.append(new_leaf_id)
            write_leaf_block(new_leaf_id, new_leaf_block_elements)
            del new_leaf_block_elements[:]

        block_size = get_tree_instance().B

        with open(sorted_filepath, 'r') as sorted_file_reader:
            consumed_child_counter = 0

            old_leaf_block_elements = self.read_leaf_block_elements_as_deque(consumed_child_counter)
            sorted_buffer_elements = get_buffer_elements_from_sorted_filereader_into_deque(sorted_file_reader, block_size)

            new_leaf_block_elements = []
            new_split_keys = []
            new_leaf_ids = []

            while old_leaf_block_elements is not None and sorted_buffer_elements is not None:
                while old_leaf_block_elements and sorted_buffer_elements:

                    leaf_element = old_leaf_block_elements[0]
                    buffer_element = sorted_buffer_elements[0]

                    if leaf_element < buffer_element.element:
                        new_leaf_block_elements.append(old_leaf_block_elements.popleft())
                    elif leaf_element > buffer_element.element:
                        if buffer_element.action == Action.INSERT:
                            new_leaf_block_elements.append(sorted_buffer_elements.popleft().element)
                        # Else it's a "delete" and element should not be appended
                    else:
                        old_leaf_block_elements.popleft()
                        sorted_buffer_elements.popleft()
                        if buffer_element.action == Action.INSERT:
                            new_leaf_block_elements.append(buffer_element.element)
                        # Else it's a "delete" and element should not be appended

                    if len(new_leaf_block_elements) == block_size:
                        new_leaf()

                if not old_leaf_block_elements:
                    consumed_child_counter += 1
                    old_leaf_block_elements = self.read_leaf_block_elements_as_deque(consumed_child_counter)

                if not sorted_buffer_elements:
                    sorted_buffer_elements = get_buffer_elements_from_sorted_filereader_into_deque(sorted_file_reader, block_size)

            if old_leaf_block_elements:
                while old_leaf_block_elements is not None:
                    new_leaf_block_elements.append(old_leaf_block_elements.popleft())

                    if len(new_leaf_block_elements) == block_size:
                        new_leaf()

                    if not old_leaf_block_elements:
                        consumed_child_counter += 1
                        old_leaf_block_elements = self.read_leaf_block_elements_as_deque(consumed_child_counter)

            if sorted_buffer_elements:
                while sorted_buffer_elements is not None:
                    buffer_element = sorted_buffer_elements.popleft()
                    if buffer_element.action == Action.INSERT:
                        new_leaf_block_elements.append(buffer_element.element)

                    if len(new_leaf_block_elements) == block_size:
                        new_leaf()

                    if not sorted_buffer_elements:
                        sorted_buffer_elements = get_buffer_elements_from_sorted_filereader_into_deque(sorted_file_reader, block_size)

            if new_leaf_block_elements:
                new_leaf()

        delete_filepath(sorted_filepath)
        delete_old_leaves(self.children_ids)
        # The last split-key is not necessary, so delete it (since len(split_keys) == len(children) - 1 unless len(children==0)
        if new_split_keys:
            del new_split_keys[-1]
        self.handles = new_split_keys
        self.children_ids = new_leaf_ids

    def prepare_buffer_blocks_into_manageable_sorted_files(self):
        # TODO Read size should be changed here: What else is internal memory right now that takes space? Self.handles could be up to B elements. What else?
        read_size = get_tree_instance().m

        sorted_ids = []
        while self.buffer_block_ids:
            elements = self.read_sort_and_remove_duplicates_from_buffer_files_with_read_size(read_size)
            sorted_id = get_new_sorted_id()
            append_to_sorted_buffer_elements_file(self.node_id, sorted_id, elements)
            sorted_ids.append(sorted_id)

        return sorted_ids

    def pass_elements_to_children(self, elements):
        # Returns the set of ids of those children nodes, where the buffer is full now
        # Also returns a bool, indicating where the children are internal nodes. If no elements were passed (and therefore no children loaded to check), returns None in its place
        if not elements:
            return set(), None
        elements = deque(elements)

        child_index = 0
        output_to_child = []

        children_are_internal_nodes = None

        children_with_full_buffers = set()
        while child_index < len(self.handles):
            while elements and elements[0].element <= self.handles[child_index]:
                output_to_child.append(elements.popleft())

            if output_to_child:
                child_node_id = self.children_ids[child_index]
                child_node = load_node(child_node_id)
                children_are_internal_nodes = child_node.is_internal_node()
                child_buffer_is_full = child_node.add_elements_to_buffer(output_to_child)
                if child_buffer_is_full:
                    children_with_full_buffers.add(child_node.node_id)
                write_node(child_node)

            output_to_child = []
            child_index += 1

        # Handle the rest of the elements for the last child
        output_to_child = list(elements)
        if output_to_child:
            child_node_id = self.children_ids[-1]
            child_node = load_node(child_node_id)
            children_are_internal_nodes = child_node.is_internal_node()
            child_buffer_is_full = child_node.add_elements_to_buffer(output_to_child)
            if child_buffer_is_full:
                children_with_full_buffers.add(child_node.node_id)
            write_node(child_node)

        return children_with_full_buffers, children_are_internal_nodes

    def get_left_neighbor_id_for_child_id(self, child_id):
        child_index = self.children_ids.index(child_id)
        if child_index == 0:
            return None
        else:
            return self.children_ids[child_index - 1]

    def get_right_neighbor_id_for_child_id(self, child_id):
        child_index = self.children_ids.index(child_id)
        if child_index == self.children_ids[-1]:
            return None
        else:
            return self.children_ids[child_index + 1]

    @staticmethod
    def annihilate_insertions_deletions_with_matching_timestamps(elements):
        """ Eliminates elements of the passed list if the element key exists several times. Only keeps last entry.
            Expects list to be sorted before call."""
        # following list will contain all indices of elements to be deleted in descending order
        if not elements:
            return

        new_list = []
        for i in range(len(elements)-1):
            if elements[i].element != elements[i + 1].element:
                new_list.append(elements[i])
        new_list.append(elements[-1])

        del elements[:]
        return new_list

    def read_leaf_block_elements_as_deque(self, consumed_child_counter):
        if consumed_child_counter == len(self.children_ids):
            return None
        else:
            return read_leaf_block_elements_as_deque(self.children_ids[consumed_child_counter])

    def delete_dummy_blocks_from_leaf_node_until_too_few_children(self):
        # Does not write any nodes to ext memory, happens in calling method
        if self.is_internal_node():
            raise ValueError("Deleting all dummy blocks node was called for a node which is not marked as a non internal node!")
        if self.children_ids[-1] != DUMMY_STRING or (self.handles and self.handles[-1] != DUMMY_STRING):
            raise ValueError(f"Was called on node {self.node_id}, but last elements are not Dummy:\nChildren:{self.children_ids}\nHandles:{self.handles}")

        # We already know that we are a Leaf Node, otherwise this function could not be called
        tree = get_tree_instance()

        while self.children_ids and self.children_ids[-1] == DUMMY_STRING:
            # If self node is root and has only 1 child -> no split-key to be deleted
            if not (self.is_root() and len(self.children_ids) == 1):
                del self.handles[-1]

            del self.children_ids[-1]

            # if we have too few children -> Node has to steal/merge -> Add to queue (Only one element ever is in queue at the same time)
            if len(self.children_ids) < self.min_amount_of_children():
                tree.node_to_steal_or_merge_queue.append(self.node_id)
                return

    def min_amount_of_children(self):
        tree = get_tree_instance()
        if not self.is_root():
            # Self is not root
            return tree.a
        elif self.is_internal_node():
            # Self is root but not a leaf node
            return 2
        else:
            # Self is root AND a leaf node
            return 0

    # Don't call this for root, root needs to be handled separately
    def steal_or_merge(self, parent_node, neighbor_node, is_left_neighbor):
        # Parent, neighbor and self node are written in this call. Also the children that have changed parent are written

        tree = get_tree_instance()
        if len(self.children_ids) + 1 != self.min_amount_of_children() or len(self.handles) + 2 != self.min_amount_of_children():
            raise ValueError(f'Steal_or_merge was called on node {self.node_id}, and has too few children or split_keys!\n{len(self.children_ids)} children: {self.children_ids}\n{len(self.handles)} handles: {self.handles}')

        if len(neighbor_node.children_ids) < tree.a + tree.t + 1:
            # Merge neighbor could have dummy children
            self.merge_with_neighbor(parent_node, neighbor_node, is_left_neighbor)
            # Neighbor node could have been in the leaf_nodes_with_dummy_children queue -> Delete from there, if present
            tree.leaf_nodes_with_dummy_children.find_and_delete_element(neighbor_node.node_id)

            # Delete neighbor
            delete_node_from_ext_memory(neighbor_node.node_id)

        else:
            # Steal neighbor can't have dummy children, we take care of that with invariant
            self.steal_from_neighbor(parent_node, neighbor_node, is_left_neighbor)

            # Write neighbor
            write_node(neighbor_node)

        # If we still have DUMMY children left-over, we need another run of all of this
        if self.children_ids[-1] == DUMMY_STRING:
            if not len(self.children_ids) == self.min_amount_of_children():
                raise ValueError(f"Node {self.node_id} has DUMMY children left after steal or merge, but has a different amount of children than it is supposed to\nNode data {self},\nmin amount of children: {self.min_amount_of_children()}")
            tree.leaf_nodes_with_dummy_children.append_to_custom_list(self.node_id)

        write_node(self)
        write_node(parent_node)

    # Don't call this for root, root needs to be handled separately
    def merge_with_neighbor(self, parent_node, neighbor_node, is_left_neighbor):
        # Our invariant makes sure there aren't any DUMMY children in neighbor node
        # Only writes childrens new parent pointer

        tree = get_tree_instance()
        child_index_in_parent = parent_node.index_for_child_id(self.node_id)
        split_key_index_in_parent = child_index_in_parent - 1 * is_left_neighbor
        split_key_from_parent = parent_node.handles[split_key_index_in_parent]

        # Overwrite the parent-pointer of all the children to be stolen (invariant makes sure there are no DUMMY children)
        if neighbor_node.is_internal_node():
            for child_id in neighbor_node.children_ids:
                stolen_child = load_node(child_id)
                stolen_child.parent_id = self.node_id
                write_node(stolen_child)

        if is_left_neighbor:
            left_node = neighbor_node
            right_node = self
        else:
            left_node = self
            right_node = neighbor_node

        # If left node has dummy children, take them away and append them to right child
        while left_node.handles and left_node.handles[-1] == DUMMY_STRING:
            del left_node.handles[-1]
            del left_node.children_ids[-1]
            right_node.handles.append(DUMMY_STRING)
            right_node.children_ids.append(DUMMY_STRING)

        # <-> Special edge case: All left node children were dummys!
        all_left_node_children_ids_were_dummys = left_node.children_ids[-1] == DUMMY_STRING
        if all_left_node_children_ids_were_dummys:
            del left_node.children_ids[-1]
            right_node.children_ids.append(DUMMY_STRING)

        new_children_ids_list = list(itertools.chain(left_node.children_ids, right_node.children_ids))

        if all_left_node_children_ids_were_dummys:
            new_split_keys_list = list(itertools.chain(right_node.handles, [DUMMY_STRING]))
        else:
            new_split_keys_list = list(itertools.chain(left_node.handles, [split_key_from_parent], right_node.handles))

        # Change self node (could have already partially happened if self is left node)
        self.handles = new_split_keys_list
        self.children_ids = new_children_ids_list
        self.delete_dummys_but_keep_min_children()

        # Change parent node
        index_for_neighbor_id = parent_node.index_for_child_id(neighbor_node.node_id)
        del parent_node.handles[split_key_index_in_parent]
        # Not 100% whether this would make sense, too tired
        # index_for_neighbor_id = child_index_in_parent - is_left_neighbor * 1 + (not is_left_neighbor) * 1
        del parent_node.children_ids[index_for_neighbor_id]

        # If parent requires splitting now, put parent into split-queue
        if len(parent_node.children_ids) < parent_node.min_amount_of_children():
            tree.node_to_steal_or_merge_queue.appendleft(parent_node.node_id)

        # Neighbor node will be deleted in super method anyway, no need to change the neighbor node instance

    def steal_from_neighbor(self, parent_node, neighbor_node, is_left_neighbor):
        # Only writes the stolen children's parent pointer
        tree = get_tree_instance()
        num_children_to_steal = tree.s

        if len(neighbor_node.children_ids) < tree.a + tree.s:
            raise ValueError(f"Node {self.node_id} wants to steal {num_children_to_steal} from neighbor {neighbor_node.node_id}, but neighbor has only len{neighbor_node.children_ids} children.\nThose children are: {neighbor_node.children_ids}")

        if neighbor_node.children_ids[-1] == DUMMY_STRING:
            raise ValueError(f"Invariant for nodes with enough children to be stolen from has not been taken care of: \nNeighbor node to be stolen from: {neighbor_node}\nNode with too few children: {self}\nParent node: {parent_node}")

        child_index_in_parent = parent_node.index_for_child_id(self.node_id)
        split_key_index_in_parent = child_index_in_parent - 1 * is_left_neighbor
        split_key_from_parent = parent_node.handles[split_key_index_in_parent]

        # Which children and split-keys to steal, and overwrite neighbor node already
        if is_left_neighbor:
            stolen_split_key_to_parent = neighbor_node.handles[-num_children_to_steal]
            stolen_split_keys_to_self = neighbor_node.handles[-num_children_to_steal + 1:]
            stolen_children = neighbor_node.children_ids[-num_children_to_steal:]
            neighbor_node.handles = neighbor_node.handles[:-num_children_to_steal]
            neighbor_node.children_ids = self.children_ids[:-num_children_to_steal]
        else:
            stolen_split_key_to_parent = neighbor_node.handles[num_children_to_steal]
            stolen_split_keys_to_self = neighbor_node.handles[:num_children_to_steal - 1]
            stolen_children = neighbor_node.children_ids[:num_children_to_steal]
            neighbor_node.handles = neighbor_node.handles[num_children_to_steal:]
            neighbor_node.children_ids = neighbor_node.children_ids[num_children_to_steal:]

        # Delete dummy children if we have some. Delete at most s - 1 dummies, since we have a - 1 + s children after merge and want at least a children in the end
        max_amount_of_dummies_to_delete = tree.s - 1
        self.delete_at_most_x_dummies(max_amount_of_dummies_to_delete)

        # We are right sibling node and ALL our children are DUMMY -> split-key stolen from parent must be overridden to DUMMY
        # If we are left sibling node and ALL our children DUMMY, they need to be appended at the END of the new children -> parent split key must be DUMMY as well, bc we had one more DUMMY child and than DUMMY split-key
        if self.children_ids[0] == DUMMY_STRING:
            split_key_from_parent = DUMMY_STRING

        if not is_left_neighbor:
            # Self is left sibling node
            # Move all zusammengehörige DUMMY-Split-keys and children to the very end
            self.move_dummy_to_the_back_of_lists(stolen_split_keys_to_self, stolen_children)
            # If we still have a DUMMY child, then split-key from parent must be adapted to DUMMY as well
            if self.children_ids[0] == DUMMY_STRING:
                split_key_from_parent = DUMMY_STRING
                del self.children_ids[0]
                stolen_children.append(DUMMY_STRING)
            self.handles = list(itertools.chain(self.handles, [split_key_from_parent], stolen_split_keys_to_self))
            self.children_ids = list(itertools.chain(self.children_ids, stolen_children))
        else:
            # Self is right sibling node
            if self.children_ids[0] == DUMMY_STRING:
                split_key_from_parent = DUMMY_STRING
            self.handles = list(itertools.chain(stolen_split_keys_to_self, [split_key_from_parent], self.handles))
            self.children_ids = list(itertools.chain(stolen_children, self.children_ids))

        # Adapt parent
        parent_node.handles[split_key_index_in_parent] = stolen_split_key_to_parent

        # Adapt stolen children's parent pointer (and make sure we're not trying to overwrite DUMMY childrens parent pointer)
        if self.is_internal_node():
            for stolen_node_id in stolen_children:
                if stolen_node_id != DUMMY_STRING:
                    stolen_child_node = load_node(stolen_node_id)
                    stolen_child_node.parent_id = self.node_id
                    write_node(stolen_child_node)

        # If we still have dummy children, calling method has to take care of that

    def move_dummy_to_the_back_of_lists(self, stolen_split_keys, stolen_children):
        # Will remove all DUMMY children and split-keys and move them to the back of the stolen lists
        #  It will not move self.children_ids[0] though, since there is no DUMMY split-key for that one in self node, and that needs to be handled in a special way
        def validity_check():
            if self.children_ids[-1] != self.handles[-1]:
                raise ValueError(f"Trying to move all Dummy children and split-keys from node {self.node_id} to stolen split keys and stolen children, but split-keys and children are mismatched after {deletions} moves:"
                                 f"Children_ids: {self.children_ids}\nSplit-keys: {self.handles}\nStolen-split-keys: {stolen_split_keys}\nStolen_children: {stolen_children}")

        deletions = 0
        while self.handles and DUMMY_STRING in [self.children_ids[-1], self.handles[-1]]:
            validity_check()
            del self.handles[-1]
            del self.children_ids[-1]
            stolen_split_keys.append(DUMMY_STRING)
            stolen_children.append(DUMMY_STRING)
            deletions += 1

    # Don't call this for root, root needs to be handled separately
    def delete_dummys_but_keep_min_children(self):
        def validity_check():
            if self.children_ids[-1] != self.handles[-1]:
                raise ValueError(f"Trying to delete Dummy children in node {self} children, but children-ids and split-keys are mismatched")

        while len(self.children_ids) > self.min_amount_of_children() and self.children_ids[-1] == DUMMY_STRING:
            validity_check()
            del self.handles[-1]
            del self.children_ids[-1]

    def delete_at_most_x_dummies(self, x):
        def validity_check():
            if self.children_ids[-1] != self.handles[-1]:
                raise ValueError(f"Trying to delete {x} children from node {self.node_id}, at most {counter} deletions to go, when encountering mismatch in DUMMY pointers:\n"
                                 f"Children_ids: {self.children_ids}\nSplit-Keys: {self.handles}")

        counter = x

        if x <= 0:
            raise ValueError(f"Trying to delete {x} dummy children from node {self.node_id}, x should be > 0")

        while counter and DUMMY_STRING in [self.children_ids[-1], self.handles[-1]]:
            validity_check()
            del self.children_ids[-1]
            del self.handles[-1]
            counter -= 1

    def root_node_is_too_small(self):
        # Deletes itself, meaning: From memory, tells child it does not have a parent anymore, changes root pointer in tree
        tree = get_tree_instance()
        if not self.is_root():
            raise ValueError(f"Trying to delete root node {self.node_id}, but this node is not root, root should be: {tree.root_node_id}")
        if not self.is_internal_node():
            raise ValueError(f"Root node {self.node_id} has been marked for deletion, but is a Leaf Node. How could this happen?")
        if len(self.children_ids) != 1:
            raise ValueError(f"Root node {self.node_id} has been marked for deletion, but does not have exactly one child.\nChildren ids: {self.children_ids}")

        loaded_child_node = load_node(self.children_ids[0])
        loaded_child_node.parent_id = None
        write_node(loaded_child_node)

        tree.root_node_id = self.children_ids[0]
        delete_node_from_ext_memory(self.node_id)

    def add_self_to_buffer_emptying_queue(self):
        # This function assumes that the node is not in the leaf queue already
        tree = get_tree_instance()
        if self.is_internal_node():
            tree.internal_node_buffer_emptying_queue.appendleft(self.node_id)
        else:
            tree.leaf_node_buffer_emptying_queue.append_to_custom_list(self.node_id)


class TreeBuffer:
    def __init__(self, max_size):
        self.elements = []
        self.max_size = max_size

    def insert_new_element(self, k, action):
        new_elem = BufferElement(k, action)
        self.elements.append(new_elem)

    def is_full(self):
        # Mainly for validating there's nothing wrong.
        if len(self.elements) > self.max_size:
            raise ValueError('Too many elements in Buffer.')

        return len(self.elements) == self.max_size

    def get_elements(self):
        return self.elements

    def clear_elements(self):
        self.elements = []


class NodeBufferBlock:
    def __init__(self, elements=None, number_elements=None):
        if elements is None:
            elements = []

        if number_elements is None:
            number_elements = len(elements)

        self.elements = elements
        self.number_elements = number_elements


# Node structure ideas:
# is_internal_node, num_handles, *handles, num_children, *paths_to_children, num_buffer_blocks, *paths_to_buffer_blocks, size_of_last_buffer_block, parent_id
def load_node(node_id) -> TreeNode:
    if node_id is None:
        raise ValueError("Tried loading node, but node_id was not provided (is None)")

    file_path = node_information_file_path_from_id(node_id)
    with open(file_path, 'r') as f:
        data = f.read().split(SEP)

    if data[0] == TRUE_STRING:
        is_internal_node = True
    else:
        is_internal_node = False

    index = 2
    num_handles = int(data[1])
    handles = data[index:index+num_handles]
    index += num_handles

    num_children = int(data[index])
    children_timestamps = data[index+1: index+1+num_children]
    index += 1 + num_children

    num_buffer_blocks = int(data[index])
    buffer_block_ids = data[index+1: index+1+num_buffer_blocks]
    index += 1 + num_buffer_blocks

    last_buffer_size = int(data[index])
    index += 1

    parent_id = data[index]
    if parent_id == 'None':
        parent_id = None
    index += 1

    node_instance = TreeNode(
        node_id=node_id,
        is_internal_node=is_internal_node,
        handles=handles,
        children=children_timestamps,
        buffer_block_ids=buffer_block_ids,
        last_buffer_size=last_buffer_size,
        parent_id=parent_id
    )
    return node_instance


def write_node(node: TreeNode):
    if node.is_internal_node():
        is_internal_string = TRUE_STRING
    else:
        is_internal_string = FALSE_STRING

    raw_list = [is_internal_string, len(node.handles), *node.handles, len(node.children_ids), *node.children_ids, len(node.buffer_block_ids), *node.buffer_block_ids, node.last_buffer_size, node.parent_id]
    str_list = [str(elem) for elem in raw_list]

    output_string = SEP.join(str_list)

    file_path = node_information_file_path_from_id(node.node_id)

    with open(file_path, 'w') as f:
        f.write(output_string)


# Buffer Block Structure:
# Each line: Element;Timestamp;Action
def read_buffer_block_elements(node_id, buffer_block_id):
    block_filepath = get_buffer_file_path_from_ids(node_id, buffer_block_id)

    return read_buffer_elements_from_file_path(block_filepath)


def read_buffer_elements_from_file_path(file_path):
    with open(file_path, 'r') as f:
        elements = []
        for line in f:
            elements.append(parse_line_into_buffer_element(line))

    return elements


def write_buffer_block(node_id, buffer_block_id, elements):
    buffer_filepath = get_buffer_file_path_from_ids(node_id, buffer_block_id)

    with open(buffer_filepath, 'w') as f:
        elements_as_str = [element.to_output_string() for element in elements]
        f.writelines(elements_as_str)


def append_to_buffer(node_id, buffer_block_id, elements):
    buffer_filepath = get_buffer_file_path_from_ids(node_id, buffer_block_id)
    with open(buffer_filepath, 'a') as f:
        elements_as_str = [element.to_output_string() for element in elements]
        f.writelines(elements_as_str)


def load_buffer_blocks_sort_and_remove_duplicates(node_id, buffer_block_ids):
    elements = load_buffer_elements_from_buffer_blocks_with_ids(node_id, buffer_block_ids)
    elements.sort(key=lambda e: (e.element, e.timestamp))
    elements_trimmed = TreeNode.annihilate_insertions_deletions_with_matching_timestamps(elements)
    return elements_trimmed


def load_buffer_elements_from_buffer_blocks_with_ids(node_id, buffer_block_ids) -> list:
    elements = []
    [elements.extend(read_buffer_block_elements(node_id, block_timestamp)) for block_timestamp in buffer_block_ids]
    return elements


def read_leaf_block_elements_as_deque(leaf_id):
    leaf_file_path = get_leaf_file_path_from_id(leaf_id)
    elements = deque()
    with open(leaf_file_path, 'r') as f:
        for line in f:
            # The line splitting [:-1] on action gets rid of the line break
            elements.append(line[:-1])

    return elements


def write_leaf_block(leaf_id, elements):
    leaf_file_path = get_leaf_file_path_from_id(leaf_id)

    with open(leaf_file_path, 'w') as f:
        elements_in_correct_format = [f'{element}\n' for element in elements]
        f.writelines(elements_in_correct_format)


def get_tree_instance() -> BufferTree:
    return BufferTree.tree_instance
