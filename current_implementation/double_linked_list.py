# Double Linked List with special look up in O(1) (Designed for node_ids which are strings)
class DoublyLinkedList:
    def __init__(self):
        self.first = None
        self.last = None
        self.num_elements = 0
        self.map = {}

    def is_empty(self):
        return self.num_elements == 0

    def get_last_without_popping(self):
        return self.last.node_id

    def append_if_not_present_already(self, node_id):
        if not self.find_list_element(node_id):
            self.append(node_id)

    def append(self, node_id):
        # Calling function must make sure the node_id isn't in the queue already
        if node_id in self.map:
            print("This shouldn't happen!!!")
            raise ValueError("Up here.")

        old_last = self.last

        new_list_elem = ListElement(node_id, prev=self.last, following=None)
        self.last = new_list_elem

        if old_last:
            old_last.following = new_list_elem
        else:
            self.first = new_list_elem

        self.map[node_id] = new_list_elem
        self.num_elements += 1

    def pop_first(self):
        if not self.first:
            raise ValueError("Tried accessing a List Element, but there are none")

        list_elem = self.first
        self.remove_element(list_elem)

        return list_elem.node_id

    def find_list_element(self, key):
        if key in self.map.keys():
            return self.map[key]
        else:
            return None

    def find_and_delete_element(self, node_id):
        element = self.find_list_element(node_id)
        if element:
            self.remove_element(element)
            return True
        return False

    def remove_element(self, list_elem):
        if self.first == list_elem:
            self.first = list_elem.following
        else:
            list_elem.prev.following = list_elem.following

        if self.last == list_elem:
            self.last = list_elem.prev
        else:
            list_elem.following.prev = list_elem.prev

        del self.map[list_elem.node_id]
        self.num_elements -= 1


class ListElement:
    def __init__(self, node_id, prev, following):
        self.node_id = node_id
        self.prev = prev
        self.following = following
