class ABTree:
    def __init__(self, a, b):
        self.a = a
        self.b = b
        self.elements = 0
        first_node = Node(is_internal_node=False, parent=None, tree=self)
        first_node.children.append(ABTree.create_inf_dummy_element())
        self.root = first_node

    @staticmethod
    def create_inf_dummy_element():
        return Leaf(float('inf'), None)

    def insert_into_tree(self, key, value):
        self.root.insert(key, value)

    def remove_from_tree(self, key):
        self.root.remove(key)

    def is_empty(self):
        return self.elements == 0


class Node:
    def __init__(self, is_internal_node, parent, tree):
        self.tree = tree
        self.is_internal_node = is_internal_node
        self.parent = parent
        self.keys = []
        self.children = []

    def locate_child_index_for_key(self, key):
        i = 0
        while i < len(self.keys) and key > self.keys[i]:
            i += 1

        return i

    def insert(self, key, value):
        # TODO Use bisect left here
        i = self.locate_child_index_for_key(key)

        if self.is_internal_node:
            self.children[i].insert(key, value)
        else:
            if key == self.children[i].key:
                # TODO Consider the possibility an element with this key already exists
                pass

            new_leaf = Leaf(key, value)
            self.keys.insert(i, key)
            self.children.insert(i, new_leaf)
            self.tree.elements += 1

            if len(self.keys) == self.tree.b:
                self.split_node()

    def split_node(self):
        if self.is_root():
            parent = Node(is_internal_node=True, parent=None, tree=self.tree)
            parent.children.append(self)

            self.parent = parent
            self.tree.root = parent
        else:
            parent = self.parent

        # Identify which keys and children are given to which node
        mid_index = len(self.children) // 2
        left_children = self.children[:mid_index]
        right_children = self.children[mid_index:]

        split_key_index = (len(self.children)-1) // 2
        split_key = self.keys[split_key_index]
        left_keys = self.keys[:split_key_index]
        right_keys = self.keys[split_key_index+1:]

        # Finds where this node is in parents list of children
        new_sibling = Node(is_internal_node=self.is_internal_node, parent=parent, tree=self.tree)
        i = parent.get_index_of_child(self)
        parent.children.insert(i+1, new_sibling)

        self.keys = left_keys
        self.children = left_children
        new_sibling.keys = right_keys
        new_sibling.children = right_children
        parent.keys.insert(i, split_key)

        if len(parent.keys) == self.tree.b:
            parent.split_node()

    def remove(self, key):
        i = self.locate_child_index_for_key(key)

        if self.is_internal_node:
            self.children[i].remove(key)
        else:
            # If key does not exist, return, don't delete anything
            if key != self.children[i].key:
                return

            # If it is the furthest child on the right, swap the handles
            if i == len(self.children) - 1:
                supernode_with_handle = self.find_node_with_handle()
                index_to_handle_in_supernode = supernode_with_handle.keys.index(key)
                self.keys[i] = supernode_with_handle[index_to_handle_in_supernode]
                supernode_with_handle[index_to_handle_in_supernode] = key

            del self.children[i]
            self.keys.remove(key)
            self.tree.elements -= 1

            if self.is_root():
                # Deliberately keep this 1, not 2. That's in case of an empty tree (only dummy-element)
                a = 2
            else:
                a = self.tree.a

            if len(self.children) < a:
                self.handle_too_few_children()

            # TODO

    def handle_too_few_children(self):
        if self.is_root():
            # In case of a completely empty tree, keep it like this
            # (This also means that self.is_internal_node must be False)
            if self.tree.elements == 0:
                return
            else:
                only_child = self.children[0]
                only_child.parent_dir_path = None
                self.tree.root = only_child
        else:
            successfully_stolen = self.try_stealing_from_neighbor()
            if successfully_stolen:
                # TODO
                pass
            else:
                self.merge_with_neighbor()
                # TODO
                pass

            # TODO
        pass

    def merge_with_neighbor(self):
        # All direct neighbors must have deg() == a now
        left_neighbor = self.get_left_neighbor()
        if left_neighbor:
            # TODO
            pass

    def try_stealing_from_neighbor(self):
        # TODO This whole method can be simplified by refactoring with custom indices

        a = self.tree.a

        left_neighbor = self.get_left_neighbor()
        if left_neighbor and left_neighbor.deg() > a:
            stolen_child = left_neighbor.children.pop(-1)
            handle_from_neighbor = left_neighbor.keys.pop(-1)
            self.children.insert(0, stolen_child)
            stolen_child.parent_dir_path = self
            handle_from_parent = self.parent.keys.pop(0)

            self.parent.keys.insert(0, handle_from_neighbor)
            self.keys.insert(0, handle_from_parent)
            return True

        right_neighbor = self.get_right_neighbor()
        if right_neighbor and right_neighbor.deg() > a:
            stolen_child = right_neighbor.children.pop(0)
            handle_from_neighbor = right_neighbor.keys.pop(0)
            self.children.insert(-1, stolen_child)
            stolen_child.parent_dir_path = self
            handle_from_parent = self.parent.keys.pop(-1)

            self.parent.keys.insert(-1, handle_from_neighbor)
            self.keys.insert(-1, handle_from_parent)
            return True

        return False

    def steal_child_from_neighbor(self, neighbor):
        # TODO

        pass

    def get_left_neighbor(self):
        children_of_parent = self.parent.children
        i = children_of_parent.index(self)
        if i > 0:
            return children_of_parent[i-1]
        else:
            return None

    def get_right_neighbor(self):
        children_of_parent = self.parent.children
        i = children_of_parent.index(self)
        if i + 1 < len(children_of_parent):
            return children_of_parent(i+1)
        else:
            return None

    def get_direct_neighbors_for_child(self, child):
        i = self.children.index(child)
        neighbors = []
        if i - 1 >= 0:
            neighbors.append(self.children[i-1])
        if i + 1 < len(self.children):
            neighbors.append(self.children[i+1])

        return neighbors

    def get_index_of_child(self, child):
        return self.children.index(child)

    # The first (grand-...)parent that is not the furthest child on the right must have the handle
    def find_node_with_handle(self):
        if self.is_furthest_right_child():
            return self.parent.find_node_with_handle()
        else:
            return self.parent

    def is_furthest_right_child(self):
        if self.is_root():
            return False
        else:
            return self.parent.children[-1] == self

    def is_root(self):
        return self == self.tree.root

    def deg(self):
        return len(self.children)


class Leaf:
    def __init__(self, key, value):
        self.key = key
        self.value = value
