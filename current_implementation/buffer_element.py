from collections import deque
from enum import unique, Enum
from current_implementation.constants_and_helpers import get_current_timestamp, SEP


class BufferElement:
    def __init__(self, element, action, timestamp=None):
        if timestamp is None:
            timestamp = get_current_timestamp()

        self.element = element
        self.timestamp = timestamp
        self.action = Action(action)

    def __eq__(self, other):
        return self.element == other.element and self.action == other.action and self.timestamp == other.timestamp

    def to_output_string(self):
        return f'{self.element}{SEP}{self.timestamp}{SEP}{self.action}\n'

    # Only for debugging
    def __str__(self):
        return f'{self.action}: {self.element} - {self.timestamp}'


@unique
class Action(str, Enum):
    """ Indication to whether an element is deleted or inserted."""
    INSERT = 'i'
    DELETE = 'd'


def get_buffer_elements_from_sorted_filereader_into_deque(file_reader, max_lines):
    """ Reads the next lines from the file_reader and directly parses each line into Buffer Element. Return is collections.deque. """
    lines = deque()
    for line in file_reader:
        if not max_lines:
            break
        lines.append(parse_line_into_buffer_element(line))
        max_lines -= 1

    if not lines:
        return None
    return lines


def parse_line_into_buffer_element(line):
    [element, action_timestamp, action] = line.split(sep=SEP)
    # The line splitting [:-1] on action gets rid of the line break
    return BufferElement(element, action[:-1], action_timestamp)
