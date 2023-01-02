""" A B+ Tree for int-keys and string-values. """
import math
from itertools import chain
from bplus_tree.bplus_helpers import *


class BPlusTree:

    tree_instance = None

    def __init__(self, order):
        clean_up_and_initialize_resource_directories()
        self.tree_instance = self
        self.b = order
        self.a = math.ceil(order / 2)
        self.root_node_id = None

    @staticmethod
    def create_root_node(k, v):
        return BPlusTreeNode(is_internal_node=False, split_keys=[k], children=[v, get_dummy_infinity_child()])

    def insert_to_tree(self, k, v):
        if self.root_node_id is None:
            root_node = self.create_root_node(k, v)
            self.root_node_id = root_node.node_id
            write_node(root_node)
            return

        leaf_node, key_is_above_leaf_node_in_tree, _ = self.find_leaf_node_for_key_iteratively(self.root_node_id, k)
        leaf_node.leaf_insert_key_value(k, v, key_is_above_leaf_node_in_tree)
        if len(leaf_node.children) > self.b:
            self.iteratively_split_nodes(leaf_node)
        else:
            write_node(leaf_node)

    def delete_from_tree(self, k):
        def sanity_check():
            if bool(key_is_above_leaf_node_in_tree) != bool(node_instance_with_exact_split_key):
                raise ValueError("Claiming to have found a split-key in with exact search key, but did not provide both bool and node.\n")
        if self.root_node_id is None:
            # empty tree
            return

        leaf_node, key_is_above_leaf_node_in_tree, node_instance_with_exact_split_key = self.find_leaf_node_for_key_iteratively(self.root_node_id, k)
        sanity_check()

        leaf_node.leaf_delete_child_for_key(k, node_instance_with_exact_split_key)

        if node_instance_with_exact_split_key:
            write_node(node_instance_with_exact_split_key)

        if len(leaf_node.children) < self.min_amount_of_children_for_node_id(leaf_node.node_id):
            self.iteratively_steal_or_merge_for_node(leaf_node)
        else:
            write_node(leaf_node)

    def iteratively_steal_or_merge_for_node(self, leaf_node):
        too_small_node = leaf_node

        while too_small_node:
            if too_small_node.node_id == self.root_node_id:
                self.handle_too_small_root_node(too_small_node)
                too_small_node = None
            else:
                parent_node = load_node(too_small_node.parent_id)
                neighbor_node, parent_split_key_index, is_left_neighbor = parent_node.get_neighbor_of_child_id(too_small_node.node_id)
                if len(neighbor_node.children) > self.a:
                    self.steal_from_neighbor(too_small_node, parent_split_key_index, neighbor_node, parent_node, is_left_neighbor)
                    write_node(neighbor_node)
                else:
                    self.merge_with_neighbor(too_small_node, parent_split_key_index, neighbor_node, parent_node, is_left_neighbor)
                    delete_node_data_from_ext_memory(neighbor_node.node_id)

                write_node(too_small_node)

                if len(parent_node.children) < self.min_amount_of_children_for_node_id(parent_node.node_id):
                    too_small_node = parent_node
                else:
                    write_node(parent_node)
                    too_small_node = None

    def steal_from_neighbor(self, stealing_node, parent_split_key_index, neighbor_node, parent_node, is_left_neighbor):
        def sanity_check():
            error_data = f'\nStealing node: {stealing_node}\nNeighbor node: {neighbor_node}\nParent node: {parent_node}\nParent-split-key-index: {parent_split_key_index}\t is_left_neighbor: {is_left_neighbor}'
            if len(stealing_node.children) != self.a - 1 or len(stealing_node.split_keys) != len(stealing_node.children) - 1:
                raise ValueError(f"Stealing node has incorrect amount of children or split-keys")
            if len(neighbor_node.children) <= self.a or len(neighbor_node.children) != len(neighbor_node.split_keys) + 1:
                raise ValueError(f"Neighbor node to be stolen from is wrong {error_data}")
            if not self.min_amount_of_children_for_node_id(parent_node.node_id) <= len(parent_node.children) <= self.b or len(parent_node.children) != len(parent_node.split_keys) + 1:
                raise ValueError(f"Parent node is wrong {error_data}")

        # Writes stolen childrens parent pointer, nothing else

        sanity_check()

        split_key_from_parent = parent_node.split_keys[parent_split_key_index]

        if is_left_neighbor:
            split_key_to_parent = neighbor_node.split_keys.pop(-1)
            stolen_child = neighbor_node.children.pop(-1)
            stealing_node.children.insert(0, stolen_child)
            stealing_node.split_keys.insert(0, split_key_from_parent)
        else:
            split_key_to_parent = neighbor_node.split_keys.pop(0)
            stolen_child = neighbor_node.children.pop(0)
            stealing_node.children.append(stolen_child)
            stealing_node.split_keys.append(split_key_from_parent)

        parent_node.split_keys[parent_split_key_index] = split_key_to_parent

        if stealing_node.is_internal_node:
            stolen_child_node = load_node(stolen_child)
            stolen_child_node.parent_id = stealing_node.node_id
            write_node(stolen_child_node)

    @staticmethod
    def merge_with_neighbor(too_small_node, parent_split_key_index, neighbor_node, parent_node, is_left_neighbor):
        # Writes stolen childrens parent pointer, nothing else

        split_key_from_parent = parent_node.split_keys[parent_split_key_index]

        if is_left_neighbor:
            left_node = neighbor_node
            right_node = too_small_node
        else:
            left_node = too_small_node
            right_node = neighbor_node

        too_small_node.split_keys = list(chain(left_node.split_keys, [split_key_from_parent], right_node.split_keys))
        too_small_node.children = list(chain(left_node.children, right_node.children))

        if is_left_neighbor:
            neighbor_index_in_parent = parent_split_key_index
        else:
            neighbor_index_in_parent = parent_split_key_index + 1

        del parent_node.children[neighbor_index_in_parent]
        del parent_node.split_keys[parent_split_key_index]

        if too_small_node.is_internal_node:
            for stolen_child_node_id in neighbor_node.children:
                stolen_child_node = load_node(stolen_child_node_id)
                stolen_child_node.parent_id = too_small_node.node_id
                write_node(stolen_child_node)

    @staticmethod
    def find_leaf_node_for_key_iteratively(current_node_id, k):
        current_node = load_node(current_node_id)

        # This exact key could still be _in_ the leaf node
        node_instance_with_exact_split_key = None
        key_is_above_leaf_node_in_tree = False
        while current_node.is_internal_node:
            node_id, equal_to_split_key = current_node.find_fitting_child_for_key(k)
            if equal_to_split_key:
                node_instance_with_exact_split_key = current_node
            key_is_above_leaf_node_in_tree = key_is_above_leaf_node_in_tree or equal_to_split_key
            current_node = load_node(node_id)

        return current_node, key_is_above_leaf_node_in_tree, node_instance_with_exact_split_key

    def iteratively_split_nodes(self, leaf_node):
        node_to_be_split = leaf_node

        while node_to_be_split:
            parent_node = self.split_node_return_parent_node(node_to_be_split)
            write_node(node_to_be_split)
            if len(parent_node.children) > self.b:
                node_to_be_split = parent_node
            else:
                node_to_be_split = None
                write_node(parent_node)

    def split_node_return_parent_node(self, child_node):
        # Writes neighbor node and passed childrens parent pointer
        # Loads parent node
        # Parent and child_node have to be written to ext. memory in calling method

        if len(child_node.split_keys) != self.b or len(child_node.children) != self.b + 1:
            raise ValueError(f"Tried splitting node {child_node.node_id}, but it does not right amount of split-keys or children.\n Node data: {child_node}")

        # child_node has b split-keys
        # Identify and adapt split-keys and children for new neighbor
        index_split_key_to_parent = math.ceil(self.b / 2) - 1
        split_key_to_parent = child_node.split_keys[index_split_key_to_parent]
        split_keys_for_neighbor = child_node.split_keys[:index_split_key_to_parent]
        child_node.split_keys = child_node.split_keys[index_split_key_to_parent + 1:]

        num_children_for_left_neighbor = len(child_node.children) // 2
        children_for_neighbor = child_node.children[:num_children_for_left_neighbor]
        child_node.children = child_node.children[num_children_for_left_neighbor:]

        # Load (or in case of root, create) parent node
        if child_node.node_id == self.root_node_id:
            # Create new root
            parent_node = BPlusTreeNode(is_internal_node=True, children=[child_node.node_id])
            self.root_node_id = parent_node.node_id
            child_node.parent_id = parent_node.node_id
        else:
            parent_node = load_node(child_node.parent_id)

        new_left_neighbor_node = BPlusTreeNode(is_internal_node=child_node.is_internal_node, split_keys=split_keys_for_neighbor, children=children_for_neighbor, parent_id=parent_node.node_id)

        # Add split key and new neighbor id to parent
        child_index_in_parent = parent_node.index_for_child(child_node.node_id)
        parent_node.children.insert(child_index_in_parent, new_left_neighbor_node.node_id)
        parent_node.split_keys.insert(child_index_in_parent, split_key_to_parent)

        # If child_node is an internal node, overwrite moved childrens parent pointer
        if child_node.is_internal_node:
            for node_id in new_left_neighbor_node.children:
                grand_child_node = load_node(node_id)
                grand_child_node.parent_id = new_left_neighbor_node.node_id
                write_node(grand_child_node)

        write_node(new_left_neighbor_node)
        return parent_node

    def min_amount_of_children_for_node_id(self, node_id):
        if node_id == self.root_node_id:
            return 2
        else:
            return self.a

    def handle_too_small_root_node(self, old_root_node):
        if len(old_root_node.children) != 1:
            raise ValueError("Trying to delete root node (internal node), but it does not have exactly 1 child")

        if old_root_node.is_internal_node:
            self.root_node_id = old_root_node.children[0]
            new_root_node = load_node(self.root_node_id)
            new_root_node.parent_id = None
            write_node(new_root_node)
        else:
            self.root_node_id = None

        delete_node_data_from_ext_memory(old_root_node.node_id)


class BPlusTreeNode:
    def __init__(self, is_internal_node, node_id=None, split_keys=None, children=None, parent_id=None):
        if split_keys is None:
            split_keys = []

        if children is None:
            children = []

        if node_id is None:
            node_id = get_new_node_id()

        self.node_id = node_id
        self.is_internal_node = is_internal_node
        self.split_keys = split_keys
        self.children = children
        self.parent_id = parent_id

    # Only for debugging:
    def __str__(self):
        return f'{self.node_id}: {self.__dict__}'

    def find_fitting_child_for_key(self, k):
        """ If self node is internal, returns the child_node_id, else, returns the element.
         Also returns a tuple of that above, as well as an indication whether the key is equal to a split-key in this node. """
        if len(self.split_keys) != len(self.children) - 1:
            raise ValueError(f"Node {self.node_id} has not been initialised properly, length of split keys and children do not fit\nNode data {self}")

        child_index, equals_split_key = self.child_index_for_key(k)
        return self.children[child_index], equals_split_key

    def child_index_for_key(self, k):
        i = 0
        while i < len(self.split_keys) and k > self.split_keys[i]:
            i += 1

        equals_split_key = i < len(self.split_keys) and k == self.split_keys[i]

        return i, equals_split_key

    def leaf_insert_key_value(self, k, v, key_is_above_leaf_node_in_tree):
        def sanity_checks():
            if self.is_internal_node:
                raise ValueError(f"Inserting to a leaf node was called on node {self.node_id}, but this node is not a leaf node\nKey: {k}\nValue: {v}\nNode data: {self}")
            if key_is_above_leaf_node_in_tree and child_index != len(self.children) - 1:
                raise ValueError(f"Key {k} already exists in tree above, but index tells us the child should be positioned elsewhere\n Key: {k}\nValue: {v}\nNode-Data: {self}\nReturned index: {child_index}")

        child_index, equals_split_key_in_self = self.child_index_for_key(k)
        sanity_checks()

        # We are overwriting data for a pre-existing key
        if key_is_above_leaf_node_in_tree or equals_split_key_in_self:
            self.children[child_index] = v
        else:
            self.split_keys.insert(child_index, k)
            self.children.insert(child_index, v)

    def get_neighbor_of_child_id(self, child_id):
        child_index = self.index_for_child(child_id)
        if child_index != 0:
            return load_node(self.children[child_index-1]), child_index - 1, True

        else:
            return load_node(self.children[child_index+1]), child_index, False

    def leaf_delete_child_for_key(self, k, node_with_exact_split_key=None):
        # Does not write anything to ext. memory
        def sanity_check():
            if index != len(self.children) - 1 and node_with_exact_split_key:
                raise ValueError(f"Supposed to delete child for key {k}, which would NOT be last child, but split-key was already found in ancestor node.\nSelf leaf node: {self}\nAncestor node: {node_with_exact_split_key}")
        index, equals_split_key = self.child_index_for_key(k)
        sanity_check()

        if not equals_split_key and not node_with_exact_split_key:
            # No element for this key is in this node, nothing to delete
            return

        # We know an element for the key exists, so we can delete it
        if index == len(self.children) - 1:
            # Swap split-key with ancestor node split-key
            ancestor_split_key_index = node_with_exact_split_key.index_for_exact_split_key(k)
            tmp = node_with_exact_split_key.split_keys[ancestor_split_key_index]
            node_with_exact_split_key.split_keys[ancestor_split_key_index] = self.split_keys[-1]
            self.split_keys[-1] = tmp

        del self.children[index]
        split_key_index = min(index, len(self.split_keys) - 1)
        del self.split_keys[split_key_index]

    def index_for_child(self, child):
        return self.children.index(child)

    def index_for_exact_split_key(self, k):
        return self.split_keys.index(k)


def write_node(node: BPlusTreeNode):
    if node.is_internal_node:
        is_internal_string = TRUE_STRING
    else:
        is_internal_string = FALSE_STRING

    raw_list = [is_internal_string, len(node.split_keys), *node.split_keys, len(node.children), *node.children, node.parent_id]
    str_list = [str(elem) for elem in raw_list]
    output_string = SEP.join(str_list)

    file_path = get_file_path_for_node_id(node.node_id)

    with open(file_path, 'w') as f:
        f.write(output_string)


def load_node(node_id) -> BPlusTreeNode:
    if node_id is None:
        raise ValueError("Tried loading node, but node_id was not provided (is None)")

    file_path = get_file_path_for_node_id(node_id)

    with open(file_path, 'r') as f:
        data = f.read().split(SEP)

    if data[0] == TRUE_STRING:
        is_internal_node = True
    else:
        is_internal_node = False

    index = 2
    num_handles = int(data[1])
    split_keys = data[index:index+num_handles]
    split_keys = [int(split_key_string) for split_key_string in split_keys]
    index += num_handles

    num_children = int(data[index])
    children = data[index+1: index+1+num_children]
    index += 1 + num_children

    parent_id = data[index]
    if parent_id == 'None':
        parent_id = None
    index += 1

    node_instance = BPlusTreeNode(is_internal_node=is_internal_node,
                                  node_id=node_id,
                                  split_keys=split_keys,
                                  children=children,
                                  parent_id=parent_id)

    return node_instance
