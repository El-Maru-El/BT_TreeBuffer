from enum import Enum, unique
from datetime import datetime
import time
from collections import defaultdict
from dataclasses import dataclass, field
import os
from pathlib import Path
import benchmarking


MODE_STRING = "mode"
BENCHMARKING_DIR = os.path.dirname(benchmarking.__file__)
OUTPUT_DIR = os.path.join(BENCHMARKING_DIR, "benchmarks")
SEPARATION_LINE = "#" * 90


@unique
class TrackingModeEnum(str, Enum):
    # For both trees:
    NODE_SPLITTING = "node_split"
    DEFAULT = 'The_complete_tree'
    ROOT_DELETION = 'root_deletion'

    NODE_MERGE = "node_merge"
    NODE_STEAL = "node_steal"

    REBALANCING = "rebalance"
    OVERWRITE_PARENT = 'overwrite_parent_pointer'

    # For buffer tree only:
    TREE_BUFFER_FULL = "internal_buffer_to_root_buffer"
    EXTERNAL_MERGE_SORT_BUFFER = 'sort_external_buffer_elements'
    MERGE_BUFFER_WITH_LEAF = 'merge_sort_buffer_with_leafs'

    FLUSH_ALL_BUFFERS = "flush_buffers"

    INTERNAL_BUFFER_EMPTYING = "internal_buffer_emptying"
    LEAF_BUFFER_EMPTYING = "leaf_buffer_emptying"

    # BPlus Tree Specific modes
    INSERT = 'insert_to_tree'
    DELETE = 'delete_from_tree'
    FIND_LEAF = 'find_leaf'

    # Sub-modes for IOCalls writing and reading
    NODE_READ = "IO_node_read"
    NODE_WRITE = "IO_node_write"

    BUFFER_ELEMENT_READ = "IO_buffer_elem_read"
    BUFFER_ELEMENT_WRITE = "IO_buffer_elem_write"

    LEAF_ELEMENT_READ = "IO_leaf_elem_read"
    LEAF_ELEMENT_WRITE = "IO_leaf_elem_write"


@dataclass
class IOCallsTracker:
    """ Measures the amount of IO call for each type of IO call made"""
    io_calls: dict = field(default_factory=lambda: defaultdict(int))

    def add_from_other_tracker(self, other: "IOCallsTracker"):
        for io_operation, num_io_calls in other.io_calls:
            self.io_calls[io_operation] += num_io_calls


@dataclass
class ModeTracker:
    # If we are working with the output dicts, the mode is the key, so no need to put it into the object again as well necessarily to identify mode later
    mode: TrackingModeEnum = None
    # Time can be entry-time, exit-time or complete time
    tracking_time: float = 0.0
    io_calls: defaultdict = field(default_factory=lambda: defaultdict(int))

    def add_io_calls_from_other_tracker(self, other: "ModeTracker"):
        for io_call, counter in other.io_calls.items():
            self.io_calls[io_call] += counter

    def add_io_calls_via_io_call_enum(self, io_call: "TrackingModeEnum", counter):
        self.io_calls[io_call] += counter

    def add_time_only(self, other_time: float):
        self.tracking_time += other_time

    def add_io_calls_and_time(self, other: "ModeTracker"):
        self.add_io_calls_from_other_tracker(other)
        self.add_time_only(other.tracking_time)

    def _io_calls_string(self):
        strings = []
        for mode in sorted(self.io_calls.keys()):
            strings.append(f'\t{mode.value}: {self.io_calls[mode]}')
        return "\t".join(strings)

    def __str__(self):
        return f"{self.mode.value} ->\tTime: {str(self.tracking_time).replace('.', ',')}s\t{self._io_calls_string()}"


class TreeTrackingHandler:

    def __init__(self):
        self.mode_tracker_stack = []
        self.nested_benchmarks = {}
        self.total_benchmarks = defaultdict(ModeTracker)
        self.current_dict_list_path = []
        self.enabled = False

    def _enter_mode(self, mode: TrackingModeEnum):
        def sanity_check():
            if self.mode_tracker_stack and self.mode_tracker_stack[-1].mode == mode:
                raise ValueError(f"Trying to enter mode {mode} twice in a row without leaving inbetween, this should not happen")

        if not self.enabled:
            return
        sanity_check()
        tracker = ModeTracker(TrackingModeEnum(mode), time.perf_counter())
        self.mode_tracker_stack.append(tracker)
        new_last_dict = self._get_or_generate_default_nested_dict_for_mode(mode)
        self.current_dict_list_path.append(new_last_dict)

    def _exit_mode(self, mode: TrackingModeEnum):
        def sanity_check():
            if not self.mode_tracker_stack:
                raise ValueError(f"Trying to exit mode {mode}, but there is no node on stack")
            if self.mode_tracker_stack[-1].mode != TrackingModeEnum(mode):
                raise ValueError(f"Trying to exit mode {mode}, but last pushed mode is {self.mode_tracker_stack[-1].mode}")
        if not self.enabled:
            return
        sanity_check()

        stop = time.perf_counter()

        # Find/Create the dict in which the current mode is being tracked
        nested_output_dict = self.current_dict_list_path.pop(-1)

        # Now pop the last off the stack and add its information to the output:
        last_mode_tracker = self.mode_tracker_stack.pop(-1)
        time_in_mode = stop - last_mode_tracker.tracking_time

        nested_output_dict[MODE_STRING].add_io_calls_from_other_tracker(last_mode_tracker)
        nested_output_dict[MODE_STRING].add_time_only(time_in_mode)
        self.total_benchmarks[last_mode_tracker.mode].add_io_calls_from_other_tracker(last_mode_tracker)
        self.total_benchmarks[last_mode_tracker.mode].add_time_only(time_in_mode)

        # Update the IO Calls of encapsulating mode
        if self.mode_tracker_stack:
            self.mode_tracker_stack[-1].add_io_calls_from_other_tracker(last_mode_tracker)

    def start_tracking(self):
        if self.enabled:
            raise ValueError("Tried starting benchmarking tracker, but it's already enabled!")
        self.enabled = True
        self._enter_mode(TrackingModeEnum.DEFAULT)

    def stop_tracking(self, is_buffer_tree, benchmark_name=None):
        # Don't turn enabled off, it shouldn't be turned back on anyways
        if not self.enabled:
            raise ValueError("Tried exiting benchmarking tracker, but it's never been enabled????")
        self._exit_mode(TrackingModeEnum.DEFAULT)
        self._generate_output(is_buffer_tree, benchmark_name)

    def _add_io_calls(self, io_call: "TrackingModeEnum", counter):
        if not self.enabled:
            return
        if self.mode_tracker_stack[-1].mode != io_call:
            raise ValueError(f"Trying to add {counter} as counter to mode {io_call}, but no sub-mode was entered for it")

        self.mode_tracker_stack[-1].add_io_calls_via_io_call_enum(TrackingModeEnum(io_call), counter)

    def _get_or_generate_default_nested_dict_for_mode(self, mode: TrackingModeEnum):
        # We might be just starting, so could be empty still
        if self.current_dict_list_path:
            current_mode_dict_in_nested_dict = self.current_dict_list_path[-1]
        else:
            current_mode_dict_in_nested_dict = self.nested_benchmarks

        if mode not in current_mode_dict_in_nested_dict:
            current_mode_dict_in_nested_dict[mode] = {MODE_STRING: ModeTracker(mode)}

        return current_mode_dict_in_nested_dict[mode]

    def _generate_output(self, is_buffer_tree, benchmark_name):
        total_benchmark_strings = ["Total benchmarks:"]
        sorted_by_mode_alphabetically = sorted(list(self.total_benchmarks.keys()))
        for mode in sorted_by_mode_alphabetically:
            mode_tracker = self.total_benchmarks[mode]
            mode_tracker.mode = mode
            total_benchmark_strings.append(mode_tracker.__str__())
        total_benchmark_strings.append(SEPARATION_LINE)
        total_benchmark_strings.append(SEPARATION_LINE)

        nested_benchmark_strings = self._nested_benchmarks_as_string_list()
        if benchmark_name:
            file_path = get_timestamped_benchmark_file_path(is_buffer_tree, benchmark_name)
            self.create_out_put_file(file_path, total_benchmark_strings, nested_benchmark_strings)
        else:
            # Just print everything to console
            for sub_string in total_benchmark_strings:
                print(sub_string)

            for sub_string in nested_benchmark_strings:
                print(sub_string)

    @staticmethod
    def create_out_put_file(file_path, total_benchmark_strings, nested_benchmark_strings):
        directory = Path(os.path.dirname(file_path))
        directory.mkdir(parents=True, exist_ok=True)

        with open(file_path, 'w') as f:
            for sub_string in total_benchmark_strings:
                f.write(f'{sub_string}\n')

            for sub_string in nested_benchmark_strings:
                f.write(f'{sub_string}\n')

    def _nested_benchmarks_as_string_list(self):
        if len(self.nested_benchmarks.keys()) != 1:
            raise ValueError("Trying to generate output, but nested benchmarks dict has been set incorrectly?")
        string_list = ["Nested benchmark strings:"]

        self.dfs_recurse_through_nested_dicts(self.nested_benchmarks[TrackingModeEnum.DEFAULT], string_list, 0)
        return string_list

    @staticmethod
    def dfs_recurse_through_nested_dicts(nested_dict, string_list, depth_counter):
        tab_prefix = '\t' * depth_counter
        string_list.append(f'{tab_prefix}{nested_dict[MODE_STRING]}')
        for sub_mode, next_dict in nested_dict.items():
            if sub_mode != MODE_STRING:
                TreeTrackingHandler.dfs_recurse_through_nested_dicts(next_dict, string_list, depth_counter + 1)

    # Methods for entering and leaving main modes
    def enter_split_mode(self):
        self._enter_mode(TrackingModeEnum.NODE_SPLITTING)

    def exit_split_mode(self):
        self._exit_mode(TrackingModeEnum.NODE_SPLITTING)

    def enter_steal_from_neighbor_mode(self):
        self._enter_mode(TrackingModeEnum.NODE_STEAL)

    def exit_steal_from_neighbor_mode(self):
        self._exit_mode(TrackingModeEnum.NODE_STEAL)

    def enter_merge_with_neighbor_mode(self):
        self._enter_mode(TrackingModeEnum.NODE_MERGE)

    def exit_merge_with_neighbor_mode(self):
        self._exit_mode(TrackingModeEnum.NODE_MERGE)

    def enter_initial_buffer_emptying_mode(self):
        self._enter_mode(TrackingModeEnum.TREE_BUFFER_FULL)

    def exit_initial_buffer_emptying_mode(self):
        self._exit_mode(TrackingModeEnum.TREE_BUFFER_FULL)

    def enter_buffer_flush_mode(self):
        self._enter_mode(TrackingModeEnum.FLUSH_ALL_BUFFERS)

    def exit_buffer_flush_mode(self):
        self._exit_mode(TrackingModeEnum.FLUSH_ALL_BUFFERS)

    def enter_internal_buffer_emptying_mode(self):
        self._enter_mode(TrackingModeEnum.INTERNAL_BUFFER_EMPTYING)

    def exit_internal_buffer_emptying_mode(self):
        self._exit_mode(TrackingModeEnum.INTERNAL_BUFFER_EMPTYING)

    def enter_leaf_buffer_emptying_mode(self):
        self._enter_mode(TrackingModeEnum.LEAF_BUFFER_EMPTYING)

    def exit_leaf_buffer_emptying_mode(self):
        self._exit_mode(TrackingModeEnum.LEAF_BUFFER_EMPTYING)

    def enter_rebalance_mode(self):
        self._enter_mode(TrackingModeEnum.REBALANCING)

    def exit_rebalance_mode(self):
        self._exit_mode(TrackingModeEnum.REBALANCING)

    def enter_root_node_deletion_mode(self):
        self._enter_mode(TrackingModeEnum.ROOT_DELETION)

    def exit_root_node_deletion_mode(self):
        self._exit_mode(TrackingModeEnum.ROOT_DELETION)

    def enter_external_merge_sort_on_buffer_mode(self):
        self._enter_mode(TrackingModeEnum.EXTERNAL_MERGE_SORT_BUFFER)

    def exit_external_merge_sort_on_buffer_mode(self):
        self._exit_mode(TrackingModeEnum.EXTERNAL_MERGE_SORT_BUFFER)

    def enter_merge_leaf_with_buffer_mode(self):
        self._enter_mode(TrackingModeEnum.MERGE_BUFFER_WITH_LEAF)

    def exit_merge_leaf_with_buffer_mode(self):
        self._exit_mode(TrackingModeEnum.MERGE_BUFFER_WITH_LEAF)

    # BPlus Tree specific main modes
    def enter_insert_to_tree_mode(self):
        self._enter_mode(TrackingModeEnum.INSERT)

    def exit_insert_to_tree_mode(self):
        self._exit_mode(TrackingModeEnum.INSERT)

    def enter_delete_from_tree_mode(self):
        self._enter_mode(TrackingModeEnum.DELETE)

    def exit_delete_from_tree_mode(self):
        self._exit_mode(TrackingModeEnum.DELETE)

    def enter_find_leaf_mode(self):
        self._enter_mode(TrackingModeEnum.FIND_LEAF)

    def exit_find_leaf_mode(self):
        self._exit_mode(TrackingModeEnum.FIND_LEAF)

    # Methods for entering/exiting sub-mode for IO calls and counting them:
    def _exit_sub_mode(self, mode, counter):
        self._add_io_calls(mode, counter)
        self._exit_mode(mode)

    def enter_node_read_sub_mode(self):
        self._enter_mode(TrackingModeEnum.NODE_READ)

    def exit_node_read_sub_mode(self, counter):
        self._exit_sub_mode(TrackingModeEnum.NODE_READ, counter)

    def enter_node_write_sub_mode(self):
        self._enter_mode(TrackingModeEnum.NODE_WRITE)

    def exit_node_write_sub_mode(self, counter):
        self._exit_sub_mode(TrackingModeEnum.NODE_WRITE, counter)

    def enter_buffer_element_read_sub_mode(self):
        self._enter_mode(TrackingModeEnum.BUFFER_ELEMENT_READ)

    def exit_buffer_element_read_sub_mode(self, counter):
        self._exit_sub_mode(TrackingModeEnum.BUFFER_ELEMENT_READ, counter)

    def enter_buffer_element_write_sub_mode(self):
        self._enter_mode(TrackingModeEnum.BUFFER_ELEMENT_WRITE)

    def exit_buffer_element_write_sub_mode(self, counter):
        self._exit_sub_mode(TrackingModeEnum.BUFFER_ELEMENT_WRITE, counter)

    def enter_leaf_element_read_sub_mode(self):
        self._enter_mode(TrackingModeEnum.LEAF_ELEMENT_READ)

    def exit_leaf_element_read_sub_mode(self, counter):
        self._exit_sub_mode(TrackingModeEnum.LEAF_ELEMENT_READ, counter)

    def enter_leaf_element_write_sub_mode(self):
        self._enter_mode(TrackingModeEnum.LEAF_ELEMENT_WRITE)

    def exit_leaf_element_write_sub_mode(self, counter):
        self._exit_sub_mode(TrackingModeEnum.LEAF_ELEMENT_WRITE, counter)

    def enter_overwrite_parent_id_sub_mode(self):
        self._enter_mode(TrackingModeEnum.OVERWRITE_PARENT)

    def exit_overwrite_parent_id_sub_mode(self, counter):
        self._exit_sub_mode(TrackingModeEnum.OVERWRITE_PARENT, counter)


def get_timestamped_benchmark_file_path(is_buffer_tree, benchmark_name):
    current_timestamp = datetime.now().strftime("%d_%m_%Y_%H_%M_%S")
    if is_buffer_tree:
        tree_dir = 'buffer_tree'
    else:
        tree_dir = 'bplus_tree'
    file_path = os.path.join(OUTPUT_DIR, benchmark_name, tree_dir, f'{current_timestamp}.txt')
    return file_path
