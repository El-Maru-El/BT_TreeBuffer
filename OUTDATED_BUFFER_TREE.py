from datetime import datetime
from enum import Enum, unique
from itertools import chain
import math


class BufferTree:

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
        self.root = TreeNode(tree=self, is_internal_node=False, parent=None)
        self.buffer_emptying_pq = []
        self.tree_buffer = TreeBuffer(self.B)

    @staticmethod
    def calculate_s(a, b):
        tmp = (b // 2) - a + 1
        return math.ceil(tmp/2)

    @staticmethod
    def calculate_t(a, b, s):
        return (b // 2) - a + s - 1

    def insert_to_tree(self, k):
        self.tree_buffer.new_element(k, Action.INSERT)
        if self.tree_buffer.is_full():
            # TODO This could be done more efficiently, since this Block is first written then immediately read again.
            block = self.tree_buffer.write_block()
            self.root.buffer.add_block(block)
            if self.root.buffer_full():
                self.buffer_emptying_pq.append(self.root)
                self.clear_full_buffers()

    def clear_full_buffers(self):
        # TODO
        while self.buffer_emptying_pq:
            node_to_empty = self.buffer_emptying_pq.pop(0)
            node_to_empty.clear_buffer()


class TreeNode:
    def __init__(self, tree, is_internal_node, parent=None):
        self.tree = tree
        self.is_internal_node = is_internal_node
        self.parent = parent
        # TODO Adapt split_keys to point to a file containing the split-keys
        self.split_keys_filepath = None
        self.loaded_split_keys = []
        self.children = []
        self.buffer = NodeBuffer()

    def clear_internal_buffer(self):
        # TODO
        split_keys = self.load_partitioning_elements()
        read_size = self.tree.m // 2
        i = 0
        while self.buffer.has_blocks():
            blocks_to_read = self.buffer.blocks[i:i * read_size]
            self.buffer.blocks = self.buffer.blocks[i * read_size:]

            elements = list(chain.from_iterable([block.read_block() for block in blocks_to_read]))
            elements.sort(key=lambda e: (e.key, e.timestamp))

            TreeNode.annihilate_insertions_deletions_with_matching_timestamps(elements)
            self.pass_elements_to_children(split_keys, elements)

        for child in self.children:
            if child.buffer_full():
                if child.is_internal_node:
                    self.tree.buffer_emptying_pq.insert(0, child)
                else:
                    self.tree.buffer_emptying_pq.append(child)

    def pass_elements_to_children(self, split_keys, elements):
        # Slightly complicated implementation, but therefore does not use unnecessary memory space
        child_index = 0
        output_to_child = []
        while elements:
            elem = elements.pop(0)
            if child_index < len(split_keys) and elem.key <= split_keys[child_index]:
                output_to_child.append(elem)
            else:
                child_node = self.children[child_index]
                child_node.buffer.add_elements(output_to_child)
                output_to_child = []

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

    def clear_leaf_buffer(self):
        # TODO
        pass

    def clear_buffer(self):
        if self.is_internal_node:
            self.clear_internal_buffer()
        else:
            self.clear_leaf_buffer()

    def load_partitioning_elements(self):
        split_keys = self.split_keys_filepath
        # TODO
        return split_keys

    def buffer_full(self):
        if self.is_root():
            limit = (self.tree.m // 2) - 1
        # Following have the same max. Buffer Size, so we could summarize those later
        elif self.is_internal_node():
            limit = self.tree.m // 2
        else:
            limit = self.tree.m // 2

        return self.buffer.size() > limit

    def is_root(self):
        return self.tree.root == self


class NodeBuffer:
    def __init__(self):
        self.blocks = []

    def add_block(self, block):
        self.blocks.append(block)

    def add_elements(self, elements):
        if not elements:
            return
        # TODO
        pass

    def size(self):
        return len(self.blocks)

    def has_blocks(self):
        return len(self.blocks) > 0


class LeafBlock:
    pass


class BufferBlock:
    def __init__(self, file_path, num_elements):
        self.file_path = file_path
        self.num_elements = num_elements

    def read_block(self):
        file_path = self.file_path
        elements = []
        # TODO read 'em all
        return elements


class TreeBuffer:
    def __init__(self, max_size):
        self.elements = []
        self.max_size = max_size

    def new_element(self, k, action):
        new_elem = Element(k, action)
        self.elements.append(new_elem)

    def is_full(self):
        # Mainly for validating there's nothing wrong.
        if len(self.elements) > self.max_size:
            raise ValueError('Too many elements in Buffer.')

        return len(self.elements) == self.max_size

    def write_block(self):
        elements = self.elements
        fake_path_to_file = datetime.now()
        # TODO Decide file extension
        file_extension = 'csv'

        file_name = f'bufferblock_times'
        # TODO Write them all to memory and return path to file
        return BufferBlock(fake_path_to_file, len(elements))


class Element:
    def __init__(self, k, action):
        self.key = k
        self.timestamp = datetime.now()
        self.action = action


@unique
class Action(str, Enum):
    """ Indication to whether an element is deleted or inserted."""
    INSERT = 'i'
    DELETE = 'd'
    EXISTENT = 'e'
