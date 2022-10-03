import math
from enum import unique, Enum
from itertools import chain

from current_implementation.constants_and_helpers import *
from collections import namedtuple


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
        self.root = root_node.dir_path
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
            # TODO This could be done more efficiently, since this Block is first written then immediately read again.
            root = load_node(self.tree_buffer)
            root.add_block_to_buffer(self.tree_buffer.get_elements())
            self.tree_buffer.clear_elements()

            if root.buffer_is_full():
                if root.is_internal_node():
                    self.internal_node_emptying_queue.append(ChildParent(root.dir_path, None))
                else:
                    self.leaf_node_emptying_queue.append(ChildParent(root.dir_path, None))
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
    def __init__(self, dir_path=None, is_internal_node=None, handles=None, children=None, buffer_blocks=None):
        if dir_path is None:
            dir_path = generate_new_nodes_dir()

        if buffer_blocks is None:
            buffer_blocks = []

        self.dir_path = dir_path

        self.handles = handles
        self.children_paths = children
        self.is_intern = is_internal_node
        self.buffer_blocks = buffer_blocks

    def get_buffer_dir(self):
        return get_buffer_dir_for_node(self.dir_path)

    def is_internal_node(self):
        if self.is_intern is None:
            raise ValueError("Tried accessing field is_internal_node before setting it.")

        return self.is_intern

    def add_block_to_buffer(self, elements):
        buffer_file_name = generate_buffer_file_name()
        file_path = get_buffer_dir_for_node(self.dir_path)
        self.buffer_blocks.append(buffer_file_name)
        write_buffer_block(file_path, elements)

    def add_elements_to_buffer(self, parent_path, elements):
        # TODO
        tree = BufferTree.tree_instance

        # TODO get last buffer file header (just size)
        # TODO append to that buffer until it is full, partition the other elements to other new buffers

        if self.buffer_is_full():
            if self.is_internal_node():
                tree.internal_node_emptying_queue.insert(0, ChildParent(self.dir_path, parent_path))
            else:
                tree.leaf_node_emptying_queue.append(ChildParent(self.dir_path, parent_path))

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
        return BufferTree.tree_instance.root == self.dir_path

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
        required_delete_from_outside = False
        num_children_before = len(self.children_paths)

        # TODO Sort all buffer files into one big file
        sorted_file = ''






        return required_delete_from_outside

    def chunks_of_data


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
                    child_node.add_elements_to_buffer(self.dir_path, output_to_child)
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
    def __init__(self, element, action):
        self.element = element
        self.timestamp = datetime.now()
        self.action = action


@unique
class Action(str, Enum):
    """ Indication to whether an element is deleted or inserted."""
    INSERT = 'i'
    DELETE = 'd'
    EXISTENT = 'e'


# Node structure ideas:
# is_internal_node, num_handles, handles, num_children, paths_to_children, num_buffer_blocks, paths_to_buffer_blocks

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
