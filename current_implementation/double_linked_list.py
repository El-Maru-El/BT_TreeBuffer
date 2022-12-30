# Double Linked List with special look up in O(1) (Designed for node_ids which are strings)
class DoublyLinkedList:
    def __init__(self):
        self.first = None
        self.last = None
        self.num_elements = 0
        self.map = {}

    # Only for debugging:
    def __str__(self):
        if not self.num_elements:
            return f"Doubly Linked List with no elements. Self.first: {self.first}. Self.map: {self.map}"

        output_str = self.first.node_id
        current_list_element = self.first.following
        while current_list_element:
            output_str += f", {current_list_element.node_id}"
            current_list_element = current_list_element.following

        return output_str

    def is_empty(self):
        return self.num_elements == 0

    def append_to_custom_list(self, node_id):
        # Calling function must make sure the node_id isn't in the queue already (if it already is in there, a mistake has been made)
        if node_id in self.map:
            raise ValueError(f"Node {node_id} was already in this queue. Queue contains: {self}")

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

    # Only for debugging
    def __str__(self):
        return f"Node_id: {self.node_id}, previous: {self.prev}, following: {self.following}"

    def __repr__(self):
        return f"Node_id: {self.node_id}, previous: {self.prev}, following: {self.following}"
