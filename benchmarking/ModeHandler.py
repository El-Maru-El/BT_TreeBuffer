from enum import Enum, unique
from collections import namedtuple
import time


@unique
class TrackingMode(str, Enum):
    # For what are the IO-Calls required?
    INSERT = 'insert_to_tree'
    DELETE = 'delete_from_tree'

    FLUSH_ALL_BUFFERS = "flush_buffers"

    TREE_BUFFER_FULL = "internal_buffer_to_root_buffer"

    INTERNAL_BUFFER_EMPTYING = "internal_buffer_emptying"
    LEAF_BUFFER_EMPTYING = "leaf_buffer_emptying"

    NODE_SPLITTING = "node_split"

    BUFFER_SORTING = "buffer_external_merge_sort"
    COMBINE_BUFFER_AND_LEAFS = "merge_sorted_buffer_with_leaf_blocks"

    # TODO Rebalance as super category? If so, include node splitting underneath it?
    NODE_MERGE = "node_merge"
    NODE_STEAL = "node_steal"

    # What IO Calls are there?
    NODE_READ = "node_read"
    NODE_WRITE = "node_write"

    BUFFER_READ = "read_buffer"
    BUFFER_WRITE = "buffer_write"

    # BPlusTree Specific:
    INTERNAL_READ

    LEAF_READ = "read_leaf"
    LEAF_WRITE = "write_leaf"



# ModeTime tuple Field names:
MODE = "mode"
TIME = "time"
NODE_READ = "node_read"
NODE_WRITE = "node_write"
BUFFER_READ = "read_buffer"
BUFFER_WRITE = "buffer_write"


ModeTime = namedtuple("ModeTime", ["mode", "time", "node_read", "node_write"])


class ModeHandler:

    def __init__(self):
        self.mode_timestamp_stack = []

    def enter_mode(self, mode: TrackingMode):
        mode_time_tuple = ModeTime(TrackingMode(mode), time.perf_counter())
        self.mode_timestamp_stack.append(mode_time_tuple)

    def exit_mode(self, mode: TrackingMode):
        if not self.mode_timestamp_stack or self.mode_timestamp_stack[-1].mode != TrackingMode(mode):
        # TODO What to check? We shouldn't enter the same mode several times at once
            pass



