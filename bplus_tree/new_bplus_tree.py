""" Bplus Tree after description of Comer"""
import math
from itertools import chain
from bplus_tree.bplus_helpers import *
from abc import abstractmethod
from benchmarking.TreeTrackingHandler import *


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

        self.node_type = NodeType(node_type)

    def leaf_insert_key_value(self, ele):
        if not self.is_leaf():
            raise ValueError(f"Inserting to a leaf node was called on node {self.node_id}, but this node is not a leaf node\nValue: {ele}\nNode data: {self}")

        child_index = self.child_index_according_to_split_keys(ele)

        # If the element doesn't exist yet, insert it
        if child_index == len(self.children) or self.children[child_index] != ele:
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
    def child_index_according_to_split_keys(self, ele):
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

    @abstractmethod
    def steal_from_neighbor(self, parent_split_key_index, neighbor_node, parent_node, is_left_neighbor):
        raise NotImplementedError()

    @abstractmethod
    def merge_with_neighbor(self, parent_split_key_index, neighbor_node, parent_node, is_left_neighbor):
        raise NotImplementedError()


class BPlusTree:

    tree_instance = None

    def __init__(self, order, max_leaf_size=None):
        clean_up_and_initialize_resource_directories()

        BPlusTree.tree_instance = self
        self.b = order
        self.a = math.ceil(order / 2)

        # if no max_leaf_size is provided, it assumes the same amount of records for a leaf as a node is allowed to have children
        if max_leaf_size is None:
            max_leaf_size = self.b
        min_leaf_size = math.ceil(max_leaf_size / 2)

        self.min_leaf_size = min_leaf_size
        self.max_leaf_size = max_leaf_size

        # Starts as disabled, must be enabled. If disabled and calls are made to the tracking Handler, the tracking Handler won't do anything
        self.tracking_handler = TreeTrackingHandler()
        self.root_node_type = NodeType.LEAF

        root_node = self.create_root_leaf()
        write_node(root_node)
        self.root_node_id = root_node.node_id

    # Must be called from outside this script
    def start_tracking_handler(self):
        self.tracking_handler.start_tracking()

    def stop_tracking_handler(self, benchmark_name=None):
        self.tracking_handler.stop_tracking(is_buffer_tree=False, benchmark_name=benchmark_name)

    @staticmethod
    def create_root_leaf():
        # Returns an empty Leaf
        return Leaf()

    def insert_to_tree(self, ele):
        self.tracking_handler.enter_insert_to_tree_mode()

        root_node = load_node(self.root_node_id, is_leaf=self.root_node_type == NodeType.LEAF)
        leaf = self.find_leaf_for_element_iteratively(root_node, ele)
        leaf.leaf_insert_key_value(ele)
        if len(leaf.children) > self.b:
            self.iteratively_split_nodes(leaf)
        else:
            write_node(leaf)

        self.tracking_handler.exit_insert_to_tree_mode()

    def load_root(self):
        return load_node(self.root_node_id, is_leaf=self.root_node_type == NodeType.LEAF)

    def delete_from_tree(self, k):
        self.tracking_handler.enter_delete_from_tree_mode()

        root_node = self.load_root()
        leaf = self.find_leaf_for_element_iteratively(root_node, k)

        leaf.leaf_delete_child_for_key(k)

        if len(leaf.children) < self.min_amount_of_children_for_node(leaf):
            self.iteratively_steal_or_merge_for_node(leaf)
        else:
            write_node(leaf)

        self.tracking_handler.exit_delete_from_tree_mode()

    def iteratively_split_nodes(self, leaf):
        self.tracking_handler.enter_split_mode()

        node_to_be_split = leaf

        while node_to_be_split:
            neighbor_node, split_key_for_parent = node_to_be_split.split_return_new_neighbor_and_split_key_to_parent()

            if self.root_node_id == node_to_be_split.node_id:
                # Create new root, if previous root has gotten too big
                new_root_node_type = self.parent_type_of_node_type(node_to_be_split.node_type)
                parent_node = BPlusTreeNode(node_type=new_root_node_type, split_keys=[split_key_for_parent], children=[neighbor_node.node_id, node_to_be_split.node_id])
                self.root_node_type = new_root_node_type
                self.root_node_id = parent_node.node_id
                neighbor_node.parent_id = parent_node.node_id
                node_to_be_split.parent_id = parent_node.node_id
            else:
                parent_node = load_node(node_to_be_split.parent_id, is_leaf=False)
                child_index = parent_node.index_for_child(node_to_be_split.node_id)
                parent_node.split_keys.insert(child_index, split_key_for_parent)
                parent_node.children.insert(child_index, neighbor_node.node_id)

            write_node(node_to_be_split)

            if len(parent_node.children) > self.b:
                node_to_be_split = parent_node
            else:
                write_node(parent_node)
                node_to_be_split = None

            write_node(neighbor_node)

        self.tracking_handler.exit_split_mode()

    def find_leaf_for_element_iteratively(self, current_node: AbstractNode, ele):
        self.tracking_handler.enter_find_leaf_mode()

        while not current_node.is_leaf():
            node_id = current_node.find_fitting_child_for_key(ele)

            current_node = load_node(node_id, current_node.is_leaf_node())

        self.tracking_handler.exit_find_leaf_mode()

        return current_node

    @staticmethod
    def parent_type_of_node_type(node_type):
        if node_type == NodeType.LEAF:
            return NodeType.LEAF_NODE
        else:
            return NodeType.INTERNAL_NODE

    def min_amount_of_children_for_node(self, node):
        if node.is_leaf():
            if node.node_id == self.root_node_id:
                return 0
            else:
                return self.min_leaf_size
        else:
            if node.node_id == self.root_node_id:
                return 2
            else:
                return self.a

    def iteratively_steal_or_merge_for_node(self, leaf):
        def sanity_check():
            if (too_small_node.node_id == self.root_node_id) != (too_small_node.parent_id is None):
                raise ValueError(f"Inconsistency: tree root node: {self.root_node_id}, node {too_small_node}: It is root <-> Node has no parent")

        self.tracking_handler.enter_rebalance_mode()

        too_small_node = leaf

        while too_small_node:
            sanity_check()
            if too_small_node.node_id == self.root_node_id:
                self.handle_too_small_root_node(too_small_node)
                too_small_node = None
            else:
                parent_node = load_node_non_leaf(too_small_node.parent_id)
                neighbor_node, parent_split_key_index, is_left_neighbor = parent_node.get_neighbor_of_child_id(too_small_node.node_id)
                if len(neighbor_node.children) > self.min_amount_of_children_for_node(neighbor_node):
                    too_small_node.steal_from_neighbor(parent_split_key_index, neighbor_node, parent_node, is_left_neighbor)
                    write_node(neighbor_node)
                else:
                    too_small_node.merge_with_neighbor(parent_split_key_index, neighbor_node, parent_node, is_left_neighbor)
                    delete_node_data_from_ext_memory(neighbor_node.node_id)

                write_node(too_small_node)

                if len(parent_node.children) < self.min_amount_of_children_for_node(parent_node):
                    too_small_node = parent_node
                else:
                    write_node(parent_node)
                    too_small_node = None

        self.tracking_handler.exit_rebalance_mode()

    def handle_too_small_root_node(self, old_root_node):
        if len(old_root_node.children) != 1 or old_root_node.is_leaf():
            raise ValueError(f"Trying to handle root {old_root_node}. It does not have exactly one child or is a Leaf Node")

        self.root_node_id = old_root_node.children[0]
        new_root_node = load_node(old_root_node.children[0], is_leaf=old_root_node.is_leaf_node())
        self.root_node_type = new_root_node.node_type
        new_root_node.parent_id = None
        write_node(new_root_node)
        delete_node_data_from_ext_memory(old_root_node.node_id)


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

    def child_index_according_to_split_keys(self, ele):
        i = 0
        while i < len(self.split_keys) and ele > self.split_keys[i]:
            i += 1

        return i

    def find_fitting_child_for_key(self, k):
        if len(self.split_keys) != len(self.children) - 1:
            raise ValueError(f"Node {self.node_id} has not been initialised properly, length of split keys and children do not fit\nNode data {self}")

        child_index = self.child_index_according_to_split_keys(k)
        return self.children[child_index]

    def split_return_new_neighbor_and_split_key_to_parent(self):
        # Writes the parent pointers of the children that were passed to neighbor node
        # Creates a new neighbor node, but does not write it or any other nodes (except described above)

        index_split_key_to_parent = (len(self.split_keys) - 1) // 2

        split_key_to_parent = self.split_keys[index_split_key_to_parent]
        split_keys_for_neighbor = self.split_keys[:index_split_key_to_parent]
        self.split_keys = self.split_keys[index_split_key_to_parent + 1:]

        children_for_neighbor = self.split_children_in_half_return_left_half()

        new_left_neighbor_node = BPlusTreeNode(node_type=self.node_type, split_keys=split_keys_for_neighbor, children=children_for_neighbor, parent_id=self.parent_id)

        # Since we are not a leaf, all children have to adapt their parent pointer

        for child_id in new_left_neighbor_node.children:
            overwrite_parent_id(child_id, new_left_neighbor_node.node_id, is_leaf=self.children_are_leaves())

        write_node(new_left_neighbor_node)
        return new_left_neighbor_node, split_key_to_parent

    def get_neighbor_of_child_id(self, child_id):
        child_index = self.index_for_child(child_id)
        if child_index != 0:
            return load_node(self.children[child_index-1], is_leaf=self.is_leaf_node()), child_index - 1, True

        else:
            return load_node(self.children[child_index+1], is_leaf=self.is_leaf_node()), child_index, False

    def steal_from_neighbor(self, parent_split_key_index, neighbor_node, parent_node, is_left_neighbor):
        # Writes stolen childrens parent pointer, nothing else

        get_tracking_handler_instance().enter_steal_from_neighbor_mode()

        split_key_from_parent = parent_node.split_keys[parent_split_key_index]

        if is_left_neighbor:
            split_key_to_parent = neighbor_node.split_keys.pop(-1)
            stolen_child = neighbor_node.children.pop(-1)
            self.children.insert(0, stolen_child)
            self.split_keys.insert(0, split_key_from_parent)
        else:
            split_key_to_parent = neighbor_node.split_keys.pop(0)
            stolen_child = neighbor_node.children.pop(0)
            self.children.append(stolen_child)
            self.split_keys.append(split_key_from_parent)

        parent_node.split_keys[parent_split_key_index] = split_key_to_parent

        overwrite_parent_id(stolen_child, self.node_id, self.children_are_leaves())

        get_tracking_handler_instance().exit_steal_from_neighbor_mode()

    def merge_with_neighbor(self, parent_split_key_index, neighbor_node, parent_node, is_left_neighbor):
        # Writes stolen childrens parent pointer, nothing else

        get_tracking_handler_instance().enter_merge_with_neighbor_mode()

        split_key_from_parent = parent_node.split_keys[parent_split_key_index]

        if is_left_neighbor:
            left_node = neighbor_node
            right_node = self
        else:
            left_node = self
            right_node = neighbor_node

        self.split_keys = list(chain(left_node.split_keys, [split_key_from_parent], right_node.split_keys))
        self.children = list(chain(left_node.children, right_node.children))

        if is_left_neighbor:
            neighbor_index_in_parent = parent_split_key_index
        else:
            neighbor_index_in_parent = parent_split_key_index + 1

        del parent_node.children[neighbor_index_in_parent]
        del parent_node.split_keys[parent_split_key_index]

        for stolen_child_node_id in neighbor_node.children:
            overwrite_parent_id(stolen_child_node_id, self.node_id, is_leaf=self.children_are_leaves())

        get_tracking_handler_instance().exit_merge_with_neighbor_mode()


class Leaf(AbstractNode):

    def merge_with_neighbor(self, parent_split_key_index, neighbor_node, parent_node, is_left_neighbor):

        get_tracking_handler_instance().enter_merge_with_neighbor_mode()

        if is_left_neighbor:
            left_node = neighbor_node
            right_node = self
        else:
            left_node = self
            right_node = neighbor_node

        self.children = list(chain(left_node.children, right_node.children))

        if is_left_neighbor:
            neighbor_index_in_parent = parent_split_key_index
        else:
            neighbor_index_in_parent = parent_split_key_index + 1

        del parent_node.children[neighbor_index_in_parent]
        del parent_node.split_keys[parent_split_key_index]

        get_tracking_handler_instance().exit_merge_with_neighbor_mode()

    def steal_from_neighbor(self, parent_split_key_index, neighbor_node, parent_node, is_left_neighbor):

        get_tracking_handler_instance().enter_steal_from_neighbor_mode()

        if is_left_neighbor:
            stolen_element = neighbor_node.children.pop(-1)
            self.children.insert(0, stolen_element)
            split_key_to_parent = neighbor_node.children[-1]
        else:
            stolen_element = neighbor_node.children.pop(0)
            self.children.append(stolen_element)
            split_key_to_parent = stolen_element

        parent_node.split_keys[parent_split_key_index] = split_key_to_parent

        get_tracking_handler_instance().exit_steal_from_neighbor_mode()

    def find_fitting_child_for_key(self, ele):
        raise NotImplementedError("Shouldn't need this method on a Leaf Node....")

    def __init__(self, node_id=None, children=None, parent_id=None):
        super().__init__(NodeType.LEAF, node_id, children, parent_id)

    def child_index_according_to_split_keys(self, ele):
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

    # Tracking happens in sub-call

    if is_leaf:
        return load_leaf(node_id)
    else:
        return load_node_non_leaf(node_id)


def load_node_non_leaf(node_id) -> BPlusTreeNode:

    get_tracking_handler_instance().enter_node_read_sub_mode()

    if node_id is None:
        raise ValueError("Tried loading node, but node_id was not provided (is None)")

    file_path = get_file_path_for_node_id(node_id)

    with open(file_path, 'r') as f:
        data = f.read().split('\n')

    first_line = data[0].split(SEP)
    parent_id = data[1]

    node_type = NodeType(first_line[0])

    num_handles = int(first_line[1])
    index = 2
    split_keys = first_line[index:index + num_handles]
    index += num_handles

    num_children = int(first_line[index])
    children = first_line[index + 1: index + 1 + num_children]
    index += 1 + num_children

    if parent_id == 'None':
        parent_id = None

    node_instance = BPlusTreeNode(node_type=node_type,
                                  node_id=node_id,
                                  split_keys=split_keys,
                                  children=children,
                                  parent_id=parent_id)

    get_tracking_handler_instance().exit_node_read_sub_mode(1)

    return node_instance


def load_leaf(node_id) -> Leaf:

    get_tracking_handler_instance().enter_leaf_element_read_sub_mode()

    leaf_file_path = get_file_path_for_node_id(node_id)

    # The line splitting [:-1] gets rid of the line break
    with open(leaf_file_path, 'r') as f:
        elements = [line[:-1] for line in f]
        parent_id = elements.pop(-1)

    if parent_id == 'None':
        parent_id = None

    leaf_instance = Leaf(node_id=node_id, parent_id=parent_id, children=elements)

    get_tracking_handler_instance().exit_leaf_element_read_sub_mode(len(leaf_instance.children))

    return leaf_instance


def overwrite_parent_id(child_id, new_parent_id, is_leaf):
    get_tracking_handler_instance().enter_overwrite_parent_id_sub_mode()

    child = load_node(child_id, is_leaf)
    child.parent_id = new_parent_id
    write_node(child)

    get_tracking_handler_instance().exit_overwrite_parent_id_sub_mode(1)


def write_node(node: AbstractNode):
    if node.is_leaf():
        write_leaf(node)
    elif isinstance(node, BPlusTreeNode):
        write_node_non_leaf(node)
    else:
        raise ValueError("This shouldn't happen.")


def write_leaf(leaf):
    get_tracking_handler_instance().enter_leaf_element_write_sub_mode()

    file_path = get_file_path_for_node_id(leaf.node_id)

    with open(file_path, 'w') as f:
        for ele in leaf.children:
            f.write(f'{ele}\n')
        f.write(f'{leaf.parent_id}\n')

    get_tracking_handler_instance().exit_leaf_element_write_sub_mode(len(leaf.children))


def write_node_non_leaf(node: BPlusTreeNode):
    get_tracking_handler_instance().enter_node_write_sub_mode()

    first_line_raw = [node.node_type.value, len(node.split_keys), *node.split_keys, len(node.children), *node.children]
    first_line_str = [str(elem) for elem in first_line_raw]

    first_line_output_string = SEP.join(first_line_str)

    file_path = get_file_path_for_node_id(node.node_id)

    with open(file_path, 'w') as f:
        f.write(first_line_output_string)
        f.write('\n')
        f.write(f'{node.parent_id}\n')

    get_tracking_handler_instance().exit_node_write_sub_mode(1)


def get_tree_instance() -> BPlusTree:
    return BPlusTree.tree_instance


def get_tracking_handler_instance() -> TreeTrackingHandler:
    # Kinda fails for some unit tests where no tree, but only nodes are created... So let's return a dummy TrackingHandler, without a tree, tracker isn't enabled anyways
    tree = get_tree_instance()
    if tree is None:
        return TreeTrackingHandler()
    else:
        return get_tree_instance().tracking_handler
