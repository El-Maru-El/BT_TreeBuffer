# Double Linked List with special look up in O(1) that only works for ChildParent Tuple

class DoublyLinkedList:
    def __init__(self):
        self.root = None
        self.last = None
        self.num_elements = 0
        self.map = {}

    def is_empty(self):
        return self.num_elements == 0

    def prepend(self, child_parent):
        old_root = self.root

        new_list_elem = ListElement(child_parent, prev=None, following=self.root)
        self.root = new_list_elem

        if old_root:
            old_root.prev = new_list_elem

        self.map[child_parent.child] = new_list_elem
        self.num_elements += 1

    def append(self, child_parent):
        old_last = self.last

        new_list_elem = ListElement(child_parent, prev=self.last, following=None)
        self.last = new_list_elem

        if old_last:
            old_last.following = new_list_elem
        else:
            self.root = new_list_elem

        self.map[child_parent.child] = new_list_elem
        self.num_elements += 1

    def pop_first(self):
        if not self.root:
            raise ValueError("Tried accessing a List Element, but there are none")

        list_elem = self.root
        self.remove_element(list_elem)

        return list_elem.child_parent

    def find_list_element(self, key):
        if key in self.map.keys():
            return self.map[key]
        else:
            return None

    def find_and_delete_element(self, node_timestamp):
        element = self.find_list_element(node_timestamp)
        if element:
            self.remove_element(element)

    def remove_element(self, list_elem):
        if self.root == list_elem:
            self.root = list_elem.following
        else:
            list_elem.prev.following = list_elem.following

        if self.last == list_elem:
            self.last = list_elem.prev
        else:
            list_elem.following.prev = list_elem.prev

        del self.map[list_elem.child_parent.child]
        self.num_elements -= 1


class ListElement:
    def __init__(self, element, prev, following):
        self.child_parent = element
        self.prev = prev
        self.following = following
