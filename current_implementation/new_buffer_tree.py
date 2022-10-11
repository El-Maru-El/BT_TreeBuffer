import math
from enum import unique, Enum
from itertools import chain

from current_implementation.constants_and_helpers import *
from collections import namedtuple
import csv

ChildParent = namedtuple('ChildParent', field_names=['child', 'parent'])


class BufferTree:

    """ Static reference to the tree. Useful for when calculating something for a node requires tree properties."""
    tree_instance = None

    def __init__(self, N, M, B):
        self.N = N
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
        root_node = TreeNode(is_internal_node=False, handles=[], children=[], buffer_blocks=[])
        self.root = root_node.node_timestamp
        self.tree_buffer = TreeBuffer(max_size=self.B)
        self.internal_node_emptying_queue = []
        self.leaf_node_emptying_queue = []

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
        if self.tree_buffer.is_full():
            # TODO This could be done more efficiently, since this Block is first written then immediately read again if buffer is full
            root = load_node(self.tree_buffer)
            root.add_block_to_buffer(self.tree_buffer.get_elements())
            root.last_buffer_size = self.b

            self.tree_buffer.clear_elements()

            if root.buffer_is_full():
                if root.is_internal_node():
                    self.internal_node_emptying_queue.append(ChildParent(root.node_timestamp, None))
                else:
                    self.leaf_node_emptying_queue.append(ChildParent(root.node_timestamp, None))
                self.clear_all_full_buffers()

    def clear_all_full_buffers(self):
        self.clear_full_internal_buffers()
        self.clear_full_leaf_buffers()

    def clear_full_internal_buffers(self):
        while self.internal_node_emptying_queue:
            node_path, parent_path = self.internal_node_emptying_queue.pop(0)
            node = load_node(node_path, parent_path)
            node.clear_internal_buffer()
            write_node(node)

    def clear_full_leaf_buffers(self):
        while self.leaf_node_emptying_queue:
            node_path, parent_path = self.leaf_node_emptying_queue.pop(0)
            node = load_node(node_path, parent_path)

            requires_deleting = node.clear_leaf_buffer()

            if requires_deleting:
                # TODO
                pass
            else:
                # TODO Does anything have to be done? Don't think so not sure yet though
                pass


class TreeNode:
    def __init__(self, node_timestamp=None, is_internal_node=None, handles=None, children=None, buffer_blocks=None, last_buffer_size=0):
        if node_timestamp is None:
            node_timestamp = generate_new_nodes_dir()

        if buffer_blocks is None:
            buffer_blocks = []

        self.node_timestamp = node_timestamp

        self.handles = handles
        self.children_paths = children
        self.is_intern = is_internal_node
        self.buffer_blocks = buffer_blocks
        self.last_buffer_size = last_buffer_size

    def is_internal_node(self):
        if self.is_intern is None:
            raise ValueError("Tried accessing field is_internal_node before setting it.")

        return self.is_intern

    def add_block_to_buffer(self, elements):
        buffer_timestamp = get_current_timestamp()
        file_path = get_buffer_file_path_from_timestamps(self.node_timestamp, buffer_timestamp)

        self.buffer_blocks.append(buffer_timestamp)
        write_buffer_block(file_path, elements)

    def add_elements_to_buffer(self, parent_path, elements):
        # TODO
        tree = BufferTree.tree_instance

        # TODO get last buffer file header (just size)
        # TODO append to that buffer until it is full, partition the other elements to other new buffers

        if self.buffer_is_full():
            # TODO We need to check first whether the node might already be in the queue
            if self.is_internal_node():
                tree.internal_node_emptying_queue.insert(0, ChildParent(self.node_timestamp, parent_path))
            else:
                tree.leaf_node_emptying_queue.append(ChildParent(self.node_timestamp, parent_path))

    def buffer_is_full(self):
        tree = BufferTree.tree_instance
        if self.is_root():
            limit = (tree.m // 2) - 1
        # Following have the same max. Buffer Size, so we could summarize those later
        elif self.is_internal_node():
            limit = tree.m // 2
        else:
            limit = tree.m // 2

        return len(self.buffer_blocks) > limit

    def is_root(self):
        return BufferTree.tree_instance.root == self.node_timestamp

    def clear_internal_buffer(self):
        read_size = BufferTree.tree_instance.m

        while self.buffer_blocks:
            blocks_to_read = self.buffer_blocks[:read_size]
            self.buffer_blocks = self.buffer_blocks[read_size:]

            elements = list(chain.from_iterable([read_buffer_block(block_path).elements for block_path in blocks_to_read]))
            elements.sort(key=lambda e: (e.key, e.timestamp))

            TreeNode.annihilate_insertions_deletions_with_matching_timestamps(elements)
            self.pass_elements_to_children(elements)
            # TODO Delete not anymore needed buffer block files
            # Delete block-files from blocks_to_read
        pass

    def clear_leaf_buffer(self):
        tree = BufferTree.tree_instance

        required_delete_from_outside = False
        num_children_before = len(self.children_paths)

        sorted_file = ''
        # TODO Sort all buffer files into one big file

        with open(sorted_file, 'r') as file:
            new_leaf_block = []

            self.get_leaf_elements_as_list()


            line = file.readline()


            while True:

                if not line:
                    # TODO
                    pass
                buffer_element = buffer_element_from_sorted_file_line(line)

        return required_delete_from_outside

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
                    child_node.add_elements_to_buffer(self.node_timestamp, output_to_child)
                    write_node(child_node)

                output_to_child = []
                child_index += 1

    def get_leaf_elements_as_list(self):
        leaf_elements = []
        for child in self.children_paths:
            child_path = get_leaf_file_path_from_timestamps(self.node_timestamp, child)

        pass

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


class BufferElement:
    def __init__(self, element, action, timestamp=None, with_time=True):
        if with_time and timestamp is None:
            timestamp = get_current_timestamp()

        self.element = element
        self.timestamp = timestamp
        self.action = action


@unique
class Action(str, Enum):
    """ Indication to whether an element is deleted or inserted."""
    INSERT = 'i'
    DELETE = 'd'
    EXISTENT = 'e'


# Node structure ideas:
# is_internal_node, num_handles, handles, num_children, *paths_to_children, num_buffer_blocks, *paths_to_buffer_blocks, size_of_last_buffer_block

def load_node(node_dir_path, parent_path=None) -> TreeNode:
    # TODO
    pass


def write_node(node: TreeNode):
    # TODO
    pass


def read_buffer_block(block_path) -> NodeBufferBlock:
    buffer_block = NodeBufferBlock()
    # TODO
    return buffer_block


def write_buffer_block(file_path, elements):
    # TODO
    pass


# https://stackoverflow.com/questions/17444679/reading-a-huge-csv-file
def chunks_of_data(data, chunk_size):
    # TODO len(data) doesn't work on data from a csv reader. Need a slightly different approach if we want to read x lines

    for i in range(0, chunk_size):
        yield data[i: i+chunk_size]


def buffer_element_from_sorted_file_line(line):
    # TODO
    ele = 'ele'
    action = 'insert'

    return BufferElement(ele, action, with_time=False)
