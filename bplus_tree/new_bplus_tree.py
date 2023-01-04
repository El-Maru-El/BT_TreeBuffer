""" Bplus Tree after description of Comer"""
import math
from itertools import chain
from bplus_tree.bplus_helpers import *
from enum import Enum, unique
from abc import abstractmethod


@unique
class NodeType(str, Enum):
    INTERNAL_NODE = "I"
    LEAF_NODE = "N"
    LEAF = "L"


class AbstractNode:

    def __init__(self, node_type, node_id, children, parent_id):
        if node_id is None:
            node_id = get_new_node_id()

        if children is None:
            children = []

        self.node_id = node_id
        self.children = children
        self.parent_id = parent_id

        # TODO: Everything referencing node_type must be adapted
        self.node_type = NodeType(node_type)

    def leaf_insert_key_value(self, ele):
        if not self.is_leaf():
            raise ValueError(f"Inserting to a leaf node was called on node {self.node_id}, but this node is not a leaf node\nValue: {ele}\nNode data: {self}")

        child_index = self.child_index_for_key(ele)

        # If the element doesn't exist yet, insert it
        if self.children[child_index] != ele:
            self.children.insert(child_index, ele)

    def is_leaf(self):
        return self.node_type == NodeType.LEAF

    def is_internal_node(self):
        return self.node_type == NodeType.INTERNAL_NODE

    def is_leaf_node(self):
        return self.node_type == NodeType.LEAF_NODE

    @abstractmethod
    def split_return_new_neighbor_and_split_key_to_parent(self):
        raise NotImplementedError()

    @abstractmethod
    def child_index_for_key(self, ele):
        raise NotImplementedError()

    def find_fitting_child_for_key(self, ele):
        raise NotImplementedError()

    def split_children_in_half_return_left_half(self):
        num_children_for_left_neighbor = len(self.children) // 2
        children_for_neighbor = self.children[:num_children_for_left_neighbor]
        self.children = self.children[num_children_for_left_neighbor:]
        return children_for_neighbor

    def children_are_leaves(self):
        return self.is_leaf_node()


class BPlusTree:

    tree_instance = None

    def __init__(self, order):
        clean_up_and_initialize_resource_directories()
        self.tree_instance = self
        self.b = order
        self.a = math.ceil(order / 2)

        # TODO Check up in the end: Do we always update it?
        self.root_node_type = NodeType.LEAF

        # TODO Create Dummy Root Leaf
        root_node = self.create_root_leaf()
        self.root_node_id = root_node.node_id

    @staticmethod
    def create_root_leaf():
        # Returns an empty Leaf
        return Leaf()

    def insert_to_tree(self, ele):
        root_node = load_node(self.root_node_id, is_leaf=self.root_node_type == NodeType.LEAF)
        leaf = self.find_leaf_for_element_iteratively(root_node, ele)
        leaf.leaf_insert_key_value(ele)
        if len(leaf.children) > self.b:
            self.iteratively_split_nodes(leaf)
        else:
            write_node(leaf)

    # TODO: Adapt delete
    def delete_from_tree(self, k):

        root_node = load_node(self.root_node_id, is_leaf=self.root_node_type == NodeType.LEAF)
        leaf = self.find_leaf_for_element_iteratively(root_node, k)

        leaf.leaf_delete_child_for_key(k)

        if len(leaf.children) < self.min_amount_of_children_for_node(leaf):
            self.iteratively_steal_or_merge_for_node(leaf)
        else:
            write_node(leaf)

    def iteratively_split_nodes(self, leaf):
        node_to_be_split = leaf

        while node_to_be_split:
            neighbor_node, split_key_for_parent = node_to_be_split.split_return_new_neighbor_and_split_key_to_parent()

            if self.root_node_id == node_to_be_split.node_id:
                # Create new root
                new_root_node_type = self.parent_type_of_node_type(node_to_be_split.node_type)
                parent_node = BPlusTreeNode(node_type=new_root_node_type, split_keys=[split_key_for_parent], children=[neighbor_node.node_id, node_to_be_split.node_id])
                self.root_node_type = new_root_node_type
                self.root_node_id = parent_node.node_id
                neighbor_node.parent_id = parent_node.node_id
                node_to_be_split.parent_id = parent_node.node_id
            else:
                parent_node = load_node(node_to_be_split.parent_id, is_leaf=False)
                child_index = parent_node.child_index_for_key(node_to_be_split.node_id)
                parent_node.split_keys.insert(child_index, split_key_for_parent)
                parent_node.children.insert(child_index, neighbor_node.node_id)

            if len(parent_node.children) > self.b:
                node_to_be_split = parent_node
            else:
                write_node(parent_node)
                node_to_be_split = None

            write_node(neighbor_node)
            write_node(node_to_be_split)

    @staticmethod
    def find_leaf_for_element_iteratively(current_node: AbstractNode, ele):

        while not current_node.is_leaf():
            node_id = current_node.find_fitting_child_for_key(ele)

            current_node = load_node(node_id, current_node.is_leaf_node())

        return current_node

    @staticmethod
    def parent_type_of_node_type(node_type):
        if node_type == NodeType.LEAF:
            return NodeType.LEAF_NODE
        else:
            return NodeType.INTERNAL_NODE

    def min_amount_of_children_for_node(self, node):
        if node.node_id != self.root_node_id:
            # TODO Will this value stay the same, even for Leaf-Blocks?
            return self.a
        # Else: Node is root
        elif node.is_leaf():
            return 1


class BPlusTreeNode(AbstractNode):

    def __init__(self, node_type, node_id=None, split_keys=None, children=None, parent_id=None):
        if split_keys is None:
            split_keys = []
        self.split_keys = split_keys

        super().__init__(node_type, node_id, children, parent_id)

    # Only for debugging:
    def __str__(self):
        return f'{self.node_id}: {self.__dict__}'

    def index_for_child(self, child):
        return self.children.index(child)

    def child_index_for_key(self, ele):
        i = 0
        while i < len(self.split_keys) and ele > self.split_keys[i]:
            i += 1

        return i

    def find_fitting_child_for_key(self, k):
        if len(self.split_keys) != len(self.children) - 1:
            raise ValueError(f"Node {self.node_id} has not been initialised properly, length of split keys and children do not fit\nNode data {self}")

        child_index = self.child_index_for_key(k)
        return self.children[child_index]

    def split_return_new_neighbor_and_split_key_to_parent(self):
        # Writes the parent pointers of the children that were passed to neighbor node
        # Creates a new neighbor node, but does not write it

        index_split_key_to_parent = (len(self.split_keys) - 1) // 2

        split_key_to_parent = self.split_keys[index_split_key_to_parent]
        split_keys_for_neighbor = self.split_keys[:index_split_key_to_parent]
        self.split_keys = self.split_keys[index_split_key_to_parent + 1:]

        children_for_neighbor = self.split_children_in_half_return_left_half()

        new_left_neighbor_node = BPlusTreeNode(node_type=self.node_type, split_keys=split_keys_for_neighbor, children=children_for_neighbor, parent_id=self.parent_id)

        # Since we are not a leaf, all children have to adapt their parent pointer

        for child_id in new_left_neighbor_node.children:
            moved_child_node = load_node(child_id, is_leaf=self.children_are_leaves())
            moved_child_node.parent_id = new_left_neighbor_node.node_id
            write_node(moved_child_node)

        write_node(new_left_neighbor_node)
        return new_left_neighbor_node, split_key_to_parent


class Leaf(AbstractNode):

    def find_fitting_child_for_key(self, ele):
        raise NotImplementedError("Shouldn't need this method on a Leaf Node....")

    def __init__(self, node_id=None, children=None, parent_id=None):
        super().__init__(NodeType.LEAF, node_id, children, parent_id)

    def child_index_for_key(self, ele):
        i = 0
        while i < len(self.children) and ele > self.children[i]:
            i += 1

        return i

    def split_return_new_neighbor_and_split_key_to_parent(self):
        children_for_neighbor = self.split_children_in_half_return_left_half()

        split_key_to_parent = children_for_neighbor[-1]
        new_left_neighbor_node = Leaf(children=children_for_neighbor, parent_id=self.parent_id)

        return new_left_neighbor_node, split_key_to_parent

    def leaf_delete_child_for_key(self, k):
        if k in self.children:
            self.children.remove(k)


def load_node(node_id, is_leaf) -> BPlusTreeNode | Leaf:
    if is_leaf:
        return load_leaf(node_id)
    else:
        return load_node_non_leaf(node_id)


def load_node_non_leaf(node_id) -> BPlusTreeNode:
    if node_id is None:
        raise ValueError("Tried loading node, but node_id was not provided (is None)")

    file_path = get_file_path_for_node_id(node_id)

    with open(file_path, 'r') as f:
        data = f.read().split(SEP)

    is_internal_node = data[0]

    num_handles = int(data[1])
    index = 2
    split_keys = data[index:index + num_handles]
    split_keys = [int(split_key_string) for split_key_string in split_keys]
    index += num_handles

    num_children = int(data[index])
    children = data[index + 1: index + 1 + num_children]
    index += 1 + num_children

    parent_id = data[index]
    if parent_id == 'None':
        parent_id = None
    index += 1

    node_instance = BPlusTreeNode(node_type=NodeType(is_internal_node),
                                  node_id=node_id,
                                  split_keys=split_keys,
                                  children=children,
                                  parent_id=parent_id)

    return node_instance


def load_leaf(node_id) -> Leaf:
    leaf_file_path = get_file_path_for_node_id(node_id)

    # The line splitting [:-1] gets rid of the line break
    with open(leaf_file_path, 'r') as f:
        parent_id = f.readline()[:-1]
        elements = [line[:-1] for line in f]

    if parent_id == 'None':
        parent_id = None

    leaf_instance = Leaf(node_id=node_id, parent_id=parent_id, children=elements)

    return leaf_instance


def write_node(node: AbstractNode):
    if node.is_leaf():
        write_leaf(node)
    elif isinstance(node, BPlusTreeNode):
        write_node_non_leaf(node)
    else:
        raise ValueError("This shouldn't happen.")


def write_leaf(leaf):
    file_path = get_file_path_for_node_id(leaf.node_id)

    with open(file_path, 'w') as f:
        f.write(f'{leaf.parent_id}\n')
        for ele in leaf.children:
            f.write(f'{ele}\n')


def write_node_non_leaf(node: BPlusTreeNode):
    raw_list = [node.node_type.value, len(node.split_keys), *node.split_keys, len(node.children), *node.children, node.parent_id]
    str_list = [str(elem) for elem in raw_list]
    output_string = SEP.join(str_list)

    file_path = get_file_path_for_node_id(node.node_id)

    with open(file_path, 'w') as f:
        f.write(output_string)
