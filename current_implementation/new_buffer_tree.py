import math
from current_implementation.buffer_element import *
from current_implementation.constants_and_helpers import *
from collections import namedtuple
from current_implementation.constants_and_helpers import append_to_sorted_buffer_elements_file
from current_implementation.double_linked_list import DoublyLinkedList
from current_implementation.merge_sort import external_merge_sort_buffer_elements_many_files
from collections import deque

ChildParent = namedtuple('ChildParent', field_names=['child', 'parent'])


class BufferTree:

    """ Static reference to the tree. Useful for when calculating something for a node requires tree properties."""
    tree_instance = None

    def __init__(self, M, B):
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
        self.root = root_node.node_id
        self.tree_buffer = TreeBuffer(max_size=self.B)
        self.internal_node_emptying_queue = []
        self.leaf_node_emptying_queue = DoublyLinkedList()

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
            root = load_node(self.root)
            root.add_block_to_buffer(self.tree_buffer.get_elements())
            root.last_buffer_size = self.B
            write_node(root)

            self.tree_buffer.clear_elements()

            if root.buffer_is_full():
                if root.is_internal_node():
                    self.internal_node_emptying_queue.append(ChildParent(root.node_id, None))
                else:
                    self.leaf_node_emptying_queue.append(ChildParent(root.node_id, None))
                self.clear_all_full_buffers()

    def clear_all_full_buffers(self):
        self.clear_full_internal_buffers()
        self.clear_full_leaf_buffers()

    def clear_full_internal_buffers(self):
        while self.internal_node_emptying_queue:
            node_id, parent_id = self.internal_node_emptying_queue.pop(0)
            node = load_node(node_id)
            node.clear_internal_buffer()
            write_node(node)

    def clear_full_leaf_buffers(self):
        while not self.leaf_node_emptying_queue.is_empty():
            node_id, parent_id = self.leaf_node_emptying_queue.pop_first()
            node = load_node(node_id)

            requires_deleting = node.clear_leaf_buffer()

            if requires_deleting:
                # TODO
                pass
            else:
                # TODO Does anything have to be done? Don't think so not sure yet though
                pass


class TreeNode:
    def __init__(self, node_id=None, is_internal_node=None, handles=None, children=None, buffer_block_ids=None, last_buffer_size=0, parent_id=None):
        if node_id is None:
            node_id = generate_new_nodes_dir()

        if buffer_block_ids is None:
            buffer_block_ids = []

        if handles is None:
            handles = []

        if children is None:
            children = []

        self.node_id = node_id

        self.handles = handles
        self.children_paths = children
        self.is_intern = is_internal_node
        self.buffer_block_ids = buffer_block_ids
        self.last_buffer_size = last_buffer_size
        self.parent_id = parent_id

    def get_new_buffer_block_id(self):
        return generate_new_buffer_block_id(len(self.buffer_block_ids))

    def is_internal_node(self):
        if self.is_intern is None:
            raise ValueError("Tried accessing field is_internal_node before setting it.")

        return self.is_intern

    def add_block_to_buffer(self, elements):
        buffer_block_id = self.get_new_buffer_block_id()

        self.buffer_block_ids.append(buffer_block_id)
        write_buffer_block(self.node_id, buffer_block_id, elements)

    def add_elements_to_buffer(self, parent_path, elements):
        tree = BufferTree.tree_instance
        # TODO append to that buffer until it is full, partition the other elements to other new buffer-blocks
        if self.buffer_block_ids and self.last_buffer_size < tree.B:
            # TODO Is this done? Think so!
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
            # TODO We need to check first whether the node might already be in the queue. Edit: Do we really need to check that? Is that possible?
            if self.is_internal_node():
                tree.internal_node_emptying_queue.insert(0, ChildParent(self.node_id, parent_path))
            else:
                tree.leaf_node_emptying_queue.append(ChildParent(self.node_id, parent_path))

    def buffer_is_full(self):
        tree = BufferTree.tree_instance
        if self.is_root():
            limit = (tree.m // 2) - 1
        # Following have the same max. Buffer Size, so we could summarize those later
        elif self.is_internal_node():
            limit = tree.m // 2
        else:
            limit = tree.m // 2

        return len(self.buffer_block_ids) > limit

    def is_root(self):
        return BufferTree.tree_instance.root == self.node_id

    def clear_internal_buffer(self):
        read_size = BufferTree.tree_instance.m // 2

        while self.buffer_block_ids:
            elements = self.read_sort_and_remove_duplicates_from_buffer_files_with_read_size(read_size)
            self.pass_elements_to_children(elements)

    def read_sort_and_remove_duplicates_from_buffer_files_with_read_size(self, read_size):
        """ Read_size = How many files to read at once. Also deletes the buffer blocks from external memory and modifies self.buffer_block_ids. """
        blocks_to_read = self.buffer_block_ids[:read_size]
        self.buffer_block_ids = self.buffer_block_ids[read_size:]
        delete_several_buffer_files_with_timestamps(self.node_id, blocks_to_read)

        return load_buffer_blocks_sort_and_remove_duplicates(self.node_id, blocks_to_read)

    def clear_leaf_buffer(self):
        tree = BufferTree.tree_instance

        required_delete_from_outside = False
        num_children_before = len(self.children_paths)

        # TODO Do we need to check whether there even are any buffer files? Could we be empty before?
        sorted_ids = self.prepare_buffer_blocks_into_manageable_sorted_files()
        sorted_filepath = external_merge_sort_buffer_elements_many_files(self.node_id, sorted_ids, tree.M)
        # TODO Once file is sorted, do the rest of the work

        self.merge_sorted_buffer_with_leaf_blocks(sorted_filepath)

        if len(self.children_paths) > num_children_before:
            # TODO
            pass
        elif len(self.children_paths) < num_children_before:
            # TODO
            pass

        return required_delete_from_outside

    def merge_sorted_buffer_with_leaf_blocks(self, sorted_filepath):
        block_size = BufferTree.tree_instance.B

        with open(sorted_filepath, 'r') as sorted_file_reader:
            consumed_child_counter = 0

            old_leaf_block_elements = self.read_leaf_block_elements_as_deque(consumed_child_counter)
            sorted_buffer_elements = get_buffer_elements_from_sorted_filereader_into_deque(sorted_file_reader, block_size)

            new_leaf_block_elements = []
            new_split_keys = []
            new_leaf_ids = []

            while old_leaf_block_elements is not None and sorted_buffer_elements is not None:
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
                    new_leaf_id = generate_new_leaf_id(len(self.children_paths), len(new_leaf_ids))

                    new_split_keys.append(new_leaf_block_elements[-1])
                    new_leaf_ids.append(new_leaf_id)
                    write_leaf_block(self.node_id, new_leaf_id, new_leaf_block_elements)
                    new_leaf_block_elements = []

                if not old_leaf_block_elements:
                    consumed_child_counter += 1
                    old_leaf_block_elements = self.read_leaf_block_elements_as_deque(consumed_child_counter)

                if not sorted_buffer_elements:
                    sorted_buffer_elements = get_buffer_elements_from_sorted_filereader_into_deque(sorted_file_reader, block_size)

            # Now either buffer elements are empty, or old leaf elements are empty
            while old_leaf_block_elements is not None:
                new_leaf_block_elements.append(old_leaf_block_elements.popleft())

                if len(new_leaf_block_elements) == block_size:
                    new_leaf_id = generate_new_leaf_id(len(self.children_paths), len(new_leaf_ids))

                    new_split_keys.append(new_leaf_block_elements[-1])
                    new_leaf_ids.append(new_leaf_id)
                    write_leaf_block(self.node_id, new_leaf_id, new_leaf_block_elements)
                    new_leaf_block_elements = []

                if not old_leaf_block_elements:
                    consumed_child_counter += 1
                    old_leaf_block_elements = self.read_leaf_block_elements_as_deque(consumed_child_counter)

            while sorted_buffer_elements is not None:
                new_leaf_block_elements.append(sorted_buffer_elements.popleft().element)

                if len(new_leaf_block_elements) == block_size:
                    new_leaf_id = generate_new_leaf_id(len(self.children_paths), len(new_leaf_ids))

                    new_split_keys.append(new_leaf_block_elements[-1])
                    new_leaf_ids.append(new_leaf_id)
                    write_leaf_block(self.node_id, new_leaf_id, new_leaf_block_elements)
                    new_leaf_block_elements = []

                if not sorted_buffer_elements:
                    sorted_buffer_elements = get_buffer_elements_from_sorted_filereader_into_deque(sorted_file_reader, block_size)

        delete_filepath(sorted_filepath)
        delete_old_leaves(self.node_id, self.children_paths)
        self.handles = new_split_keys
        self.children_paths = new_leaf_ids

    def prepare_buffer_blocks_into_manageable_sorted_files(self):
        read_size = BufferTree.tree_instance.m

        sorted_ids = []
        while self.buffer_block_ids:
            elements = self.read_sort_and_remove_duplicates_from_buffer_files_with_read_size(read_size)
            sorted_id = get_new_sorted_id()
            append_to_sorted_buffer_elements_file(self.node_id, sorted_id, elements)
            sorted_ids.append(sorted_id)

        return sorted_ids

    def pass_elements_to_children(self, elements):
        # Slightly complicated implementation, but therefore does not use unnecessary memory space

        child_index = 0
        output_to_child = []
        while elements:
            elem = elements.pop(0)
            if child_index < len(self.handles) and elem.key <= self.handles[child_index]:
                output_to_child.append(elem)
            else:
                if output_to_child:

                    child_node_path = self.children_paths[child_index]

                    child_node = load_node(child_node_path)
                    child_node.add_elements_to_buffer(self.node_id, output_to_child)
                    write_node(child_node)

                output_to_child = []
                child_index += 1

    @staticmethod
    def annihilate_insertions_deletions_with_matching_timestamps(elements):
        """ Eliminates elements of the passed list if the element key exists several times. Only keeps last entry.
            Expects list to be sorted before call."""
        # following list will contain all indices of elements to be deleted in descending order
        indices_to_del = []
        for i, elem in enumerate(elements):
            if i + 1 < len(elements) and elements[i+1].key == elem.key:
                indices_to_del.insert(0, i)

        for i in indices_to_del:
            del elements[i]

    def read_leaf_block_elements_as_deque(self, consumed_child_counter):
        if consumed_child_counter == len(self.children_paths):
            return None
        else:
            return read_leaf_block_elements_as_deque(self.node_id, self.children_paths[consumed_child_counter])


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
    file_path = node_information_file_path_from_timestamp(node_id)
    with open(file_path, 'r') as f:
        data = f.read().split(SEP)

    if data[0] == IS_INTERNAL_STR:
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
        is_internal_string = IS_INTERNAL_STR
    else:
        is_internal_string = IS_NOT_INTERNAL_STR

    raw_list = [is_internal_string, len(node.handles), *node.handles, len(node.children_paths), *node.children_paths, len(node.buffer_block_ids), *node.buffer_block_ids, node.last_buffer_size, node.parent_id]
    str_list = [str(elem) for elem in raw_list]

    output_string = SEP.join(str_list)

    file_path = node_information_file_path_from_timestamp(node.node_id)

    with open(file_path, 'w') as f:
        f.write(output_string)


# Buffer Block Structure:
# Each line: Element;Timestamp;Action
def read_buffer_block_elements(node_id, block_timestamp):
    block_filepath = get_buffer_file_path_from_timestamps(node_id, block_timestamp)

    return read_buffer_elements_from_file_path(block_filepath)


def read_buffer_elements_from_file_path(file_path):
    with open(file_path, 'r') as f:
        elements = []
        for line in f:
            elements.append(parse_line_into_buffer_element(line))

    return elements


def write_buffer_block(node_id, buffer_block_id, elements):
    buffer_filepath = get_buffer_file_path_from_timestamps(node_id, buffer_block_id)

    with open(buffer_filepath, 'w') as f:
        elements_as_str = [element.to_output_string() for element in elements]
        f.writelines(elements_as_str)


def append_to_buffer(node_id, buffer_block_id, elements):
    buffer_filepath = get_buffer_file_path_from_timestamps(node_id, buffer_block_id)
    with open(buffer_filepath, 'a') as f:
        elements_as_str = [element.to_output_string() for element in elements]
        f.writelines(elements_as_str)


def load_buffer_blocks_sort_and_remove_duplicates(node_id, buffer_block_ids):
    elements = load_buffer_elements_from_buffer_blocks_with_ids(node_id, buffer_block_ids)
    elements.sort(key=lambda e: (e.key, e.timestamp))
    TreeNode.annihilate_insertions_deletions_with_matching_timestamps(elements)
    return elements


def load_buffer_elements_from_buffer_blocks_with_ids(node_id, buffer_block_ids):
    elements = []
    [elements.extend(read_buffer_block_elements(node_id, block_timestamp)) for block_timestamp in buffer_block_ids]
    return elements


def read_leaf_block_elements_as_deque(node_id, leaf_id):
    leaf_file_path = get_leaf_file_path_from_timestamps(node_id, leaf_id)
    elements = deque()
    with open(leaf_file_path, 'r') as f:
        for line in f:
            # The line splitting [:-1] on action gets rid of the line break
            elements.append(line[:-1])

    return elements


def write_leaf_block(node_id, leaf_id, elements):
    leaf_file_path = get_leaf_file_path_from_timestamps(node_id, leaf_id)

    with open(leaf_file_path, 'w') as f:
        elements_in_correct_format = [f'{element}\n' for element in elements]
        f.writelines(elements_in_correct_format)
