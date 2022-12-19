# Double Linked List with special look up in O(1) (only works for ChildParent Tuple)
class DoublyLinkedList:
    def __init__(self):
        self.first = None
        self.last = None
        self.num_elements = 0
        self.map = {}

    def is_empty(self):
        return self.num_elements == 0

    def get_last_without_popping(self):
        return self.last.child_parent

    def append(self, child_parent):
        # TODO Check whether the element is already present in here (Can happen if an internal node has emptied itself several times into the same child, which is a Leaf Node)
        old_last = self.last

        new_list_elem = ListElement(child_parent, prev=self.last, following=None)
        self.last = new_list_elem

        if old_last:
            old_last.following = new_list_elem
        else:
            self.first = new_list_elem

        self.map[child_parent.child] = new_list_elem
        self.num_elements += 1

    def pop_first(self):
        if not self.first:
            raise ValueError("Tried accessing a List Element, but there are none")

        list_elem = self.first
        self.remove_element(list_elem)

        return list_elem.child_parent

    def find_list_element(self, key):
        if key in self.map.keys():
            return self.map[key]
        else:
            return None

    def find_and_delete_element(self, node_id):
        element = self.find_list_element(node_id)
        if element:
            self.remove_element(element)

    def remove_element(self, list_elem):
        if self.first == list_elem:
            self.first = list_elem.following
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
