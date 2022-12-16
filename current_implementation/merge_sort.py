""" Contains the functionality to do an external merge sort on an arbitrary amount of files containing BufferElement.
Assumes that the elements within EACH file passed are sorted and no file contains the same element more than once."""
from current_implementation.constants_and_helpers import *
from current_implementation.buffer_element import get_buffer_elements_from_sorted_filereader_into_deque


def external_merge_sort_buffer_elements_many_files(node_id, sorted_ids, max_elements):
    """ Assumes each file passed is sorted and does not contain duplicates. """
    if not sorted_ids:
        raise ValueError(f"Tried merge sort for node with timestamp {node_id}, but sorted_ids is {sorted_ids}")

    while len(sorted_ids) > 1:
        new_sorted_ids = []
        # Keep merging two files until there is only one left
        for ind, sorted_id in enumerate(sorted_ids):
            if ind % 2 == 0:
                if ind + 1 < len(sorted_ids):
                    new_sorted_id = external_merge_sort_buffer_elements_two_files(node_id, sorted_id, sorted_ids[ind + 1], max_elements)
                    new_sorted_ids.append(new_sorted_id)
                else:
                    new_sorted_ids.append(sorted_id)

        sorted_ids = new_sorted_ids

    sorted_filepath = get_sorted_file_path_from_timestamps(node_id, sorted_ids[0])

    return sorted_filepath


def external_merge_sort_buffer_elements_two_files(node_id, left_sorted_id, right_sorted_id, max_elements):
    read_size_per_file = max_elements // 2
    left_filepath = get_sorted_file_path_from_timestamps(node_id, left_sorted_id)
    right_filepath = get_sorted_file_path_from_timestamps(node_id, right_sorted_id)

    left_filereader = open(left_filepath, 'r')
    right_filereader = open(right_filepath, 'r')

    new_sorted_id = get_new_sorted_id()

    left_buffer_elements = get_buffer_elements_from_sorted_filereader_into_deque(left_filereader, read_size_per_file)
    right_buffer_elements = get_buffer_elements_from_sorted_filereader_into_deque(right_filereader, read_size_per_file)

    # Merge until one file has been completely merged. Every time a buffer of one file runs full, get the next bulk of lines
    while left_buffer_elements is not None and right_buffer_elements is not None:
        output_buffer_elements = merge_sort_stop_when_one_is_empty(left_buffer_elements, right_buffer_elements)

        append_to_sorted_buffer_elements_file(node_id, new_sorted_id, output_buffer_elements)
        if not left_buffer_elements:
            left_buffer_elements = get_buffer_elements_from_sorted_filereader_into_deque(left_filereader, read_size_per_file)
        if not right_buffer_elements:
            right_buffer_elements = get_buffer_elements_from_sorted_filereader_into_deque(right_filereader, read_size_per_file)

    # output_buffer_elements is empty now
    while left_buffer_elements:
        # right_buffer_elements must be empty
        append_to_sorted_buffer_elements_file(node_id, new_sorted_id, left_buffer_elements)
        left_buffer_elements = get_buffer_elements_from_sorted_filereader_into_deque(left_filereader, max_elements)

    while right_buffer_elements:
        # left_buffer_elements must have been empty before the prior loop already
        append_to_sorted_buffer_elements_file(node_id, new_sorted_id, right_buffer_elements)
        right_buffer_elements = get_buffer_elements_from_sorted_filereader_into_deque(right_filereader, max_elements)

    left_filereader.close()
    right_filereader.close()
    delete_sorted_files_with_timestamps(node_id, [left_sorted_id, right_sorted_id])
    return new_sorted_id


def merge_sort_stop_when_one_is_empty(deque_one, deque_two):

    output_buffer_elements = []
    while deque_one and deque_two:
        left_elem = deque_one[0]
        right_elem = deque_two[0]

        if left_elem.element < right_elem.element:
            output_buffer_elements.append(deque_one.popleft())
        elif left_elem.element > right_elem.element:
            output_buffer_elements.append(deque_two.popleft())
        else:
            deque_one.popleft()
            deque_two.popleft()
            if left_elem.timestamp < right_elem.timestamp:
                output_buffer_elements.append(right_elem)
            else:
                output_buffer_elements.append(left_elem)

    return output_buffer_elements






# def internal_merge_of_sorted_lists(file_path_list):
#     """ Assumes all elements of all files fit into main-memory at once!!!"""
#     file_path_deque = deque(file_path_list)
#
#     result = deque()
#     for file_path in file_path_deque:
#         # TODO
#         pass


# def merge_list_of_buffer_elements(list_of_deques_of_buffer_elements) -> list:
#     """ Format of passed iterable: [Iterable<BufferElement>]"""
#     list_of_deques_of_buffer_elements = [deque(sub_list) for sub_list in list_of_deques_of_buffer_elements]
#
#     result = []
#     while any(elements for elements in list_of_deques_of_buffer_elements):
#         smallest_elements = pop_smallest_elements_of_deques_with_smallest_key(list_of_deques_of_buffer_elements)
#         smallest_elements.sort()
#     return result


# def pop_smallest_elements_of_deques_with_smallest_key(list_of_deques_of_buffer_elements):
#     """ Returns the smallest elements of any deque. Also deletes iterables in the original list
#     :param list_of_deques_of_buffer_elements: Format has to be List of deque of BufferElement. """
#     smallest_key = list_of_deques_of_buffer_elements[0][0].element
#     deques_with_smallest_element = []
#     indices = deque()
#     for ind, buffer_element_deque in enumerate(list_of_deques_of_buffer_elements):
#         if buffer_element_deque[0].element < smallest_key:
#             smallest_key = buffer_element_deque[0].element
#             deques_with_smallest_element = [buffer_element_deque]
#             indices = deque([ind])
#         elif buffer_element_deque[0].element == smallest_key:
#             deques_with_smallest_element.append(buffer_element_deque)
#             indices.appendleft(ind)
#
#     smallest_elements = [some_deque.popleft() for some_deque in deques_with_smallest_element]
#     # Identified all indices of empty dequeues in the list and delete them (starting from the back of the list)
#     for ind in indices:
#         if not list_of_deques_of_buffer_elements[ind]:
#             del list_of_deques_of_buffer_elements[ind]
#
#     return smallest_elements


# def external_merge_sort(first_file_path_list, second_file_path_list, lines_that_fit_into_main_memory):
#     first_file_path_deque = deque(first_file_path_list)
#     second_file_path_deque = deque(second_file_path_list)
#
#     for file_path in first_file_path_deque:
#         # TODO
#         pass