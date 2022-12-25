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

        self.total_written_leaf_blocks = 0
        root_node = TreeNode(is_internal_node=False, handles=[], children=[], buffer_block_ids=[])
        self.root_node_id = root_node.node_id
        self.tree_buffer = TreeBuffer(max_size=self.B)
        self.internal_node_emptying_queue = deque()
        self.leaf_node_emptying_queue = DoublyLinkedList()
        self.split_queue = deque()

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
            root = load_node(self.root_node_id)
            root.add_block_to_buffer(self.tree_buffer.get_elements())
            root.last_buffer_size = self.B
            write_node(root)

            self.tree_buffer.clear_elements()

            if root.buffer_is_full():
                # At this point the queues should still be empty, so no checks to whether root is already present are necessary
                if root.is_internal_node():
                    self.internal_node_emptying_queue.append(root.node_id)
                else:
                    self.leaf_node_emptying_queue.append(root.node_id)
                self.clear_all_full_buffers()

    def clear_all_full_buffers(self):
        self.clear_full_internal_buffers()
        self.clear_full_leaf_buffers()
        # TODO Do we need to check here whether some Leaf Node has Dummy Blocks?

    def clear_full_internal_buffers(self):
        while self.internal_node_emptying_queue:
            node_id = self.internal_node_emptying_queue.popleft()
            node = load_node(node_id)
            node.clear_internal_buffer()
            write_node(node)

    def clear_full_leaf_buffers(self):
        while not self.leaf_node_emptying_queue.is_empty():
            node_id = self.leaf_node_emptying_queue.pop_first()
            node = load_node(node_id)

            node.clear_leaf_buffer()

            # TODO Does anything have to be done? Don't think so not sure yet though
            # TODO What about merges? Where will those be handled?

            write_node(node)


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

    def get_new_buffer_block_id(self):
        return generate_new_buffer_block_id(len(self.buffer_block_ids))

    def is_internal_node(self):
        return self.is_intern

    def add_block_to_buffer(self, elements):
        buffer_block_id = self.get_new_buffer_block_id()

        self.buffer_block_ids.append(buffer_block_id)
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

        if self.buffer_is_full():
            if self.is_internal_node():
                # Since we load a specific amount of blocks repeatedly, we might add the same one repeatedly after each other
                if tree.internal_node_emptying_queue and tree.internal_node_emptying_queue[0] != self.node_id:
                    tree.internal_node_emptying_queue.appendleft(self.node_id)
            else:
                if not tree.leaf_node_emptying_queue.is_empty() and tree.leaf_node_emptying_queue.get_last_without_popping() != self.node_id:
                    tree.leaf_node_emptying_queue.append(self.node_id)

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

    def is_root(self):
        return BufferTree.tree_instance.root_node_id == self.node_id

    def clear_internal_buffer(self):
        read_size = get_tree_instance().m // 2

        while self.buffer_block_ids:
            elements = self.read_sort_and_remove_duplicates_from_buffer_files_with_read_size(read_size)
            self.pass_elements_to_children(elements)

        self.last_buffer_size = 0

    def read_sort_and_remove_duplicates_from_buffer_files_with_read_size(self, read_size):
        """ Read_size = How many files to read at once. Also deletes the buffer blocks from external memory and modifies self.buffer_block_ids. """
        blocks_to_read = self.buffer_block_ids[:read_size]
        self.buffer_block_ids = self.buffer_block_ids[read_size:]
        elements = load_buffer_blocks_sort_and_remove_duplicates(self.node_id, blocks_to_read)

        delete_several_buffer_files_with_ids(self.node_id, blocks_to_read)
        return elements

    def clear_leaf_buffer(self):
        # self node is written in callee
        tree = get_tree_instance()

        num_children_before = len(self.children_ids)

        # TODO Do we need to check whether there even are any buffer files? Could we be empty before?
        sorted_ids = self.prepare_buffer_blocks_into_manageable_sorted_files()
        sorted_filepath = external_merge_sort_buffer_elements_many_files(self.node_id, sorted_ids, tree.M)
        self.last_buffer_size = 0

        # TODO Once file is sorted, do the rest of the work

        self.merge_sorted_buffer_with_leaf_blocks(sorted_filepath)

        if len(self.children_ids) > num_children_before:
            handle_child_id_tuples = self.identify_handles_and_split_keys_to_be_inserted(num_children_before)
            # TODO How to do this? doesn't work yet, function doesn't exist
            self.insert_new_children(handle_child_id_tuples=handle_child_id_tuples)

        elif len(self.children_ids) < num_children_before:
            # TODO If node-merging is triggered, check whether neighbor node is in buffer-emptying-queue already
            # TODO Also consider if node is the root node:
            #  If is_internal_node: min-children = 2
            #  Else: min_children = 0 :)
            pass

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
        while tree.split_queue:
            node_instance_to_be_split = tree.split_queue.popleft()
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
            self.is_intern = False
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
                tree.split_queue.append(parent_node)
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
        read_size = get_tree_instance().m

        sorted_ids = []
        while self.buffer_block_ids:
            elements = self.read_sort_and_remove_duplicates_from_buffer_files_with_read_size(read_size)
            sorted_id = get_new_sorted_id()
            append_to_sorted_buffer_elements_file(self.node_id, sorted_id, elements)
            sorted_ids.append(sorted_id)

        return sorted_ids

    def pass_elements_to_children(self, elements):
        if not elements:
            return

        elements = deque(elements)

        child_index = 0
        output_to_child = []

        while child_index < len(self.handles):
            while elements and elements[0].element <= self.handles[child_index]:
                output_to_child.append(elements.popleft())

            if output_to_child:
                child_node_id = self.children_ids[child_index]
                child_node = load_node(child_node_id)
                child_node.add_elements_to_buffer(output_to_child)
                write_node(child_node)

            output_to_child = []
            child_index += 1

        # Handle the rest of the elements for the last child
        output_to_child = list(elements)
        if output_to_child:
            child_node_id = self.children_ids[-1]
            child_node = load_node(child_node_id)
            child_node.add_elements_to_buffer(output_to_child)
            write_node(child_node)

    @staticmethod
    def annihilate_insertions_deletions_with_matching_timestamps(elements):
        """ Eliminates elements of the passed list if the element key exists several times. Only keeps last entry.
            Expects list to be sorted before call."""
        # following list will contain all indices of elements to be deleted in descending order
        if not elements:
            return

        indices_to_del = deque()
        for i in range(len(elements)-1):
            if elements[i].element == elements[i+1].element:
                indices_to_del.appendleft(i)

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
