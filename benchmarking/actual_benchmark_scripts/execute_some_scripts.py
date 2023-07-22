from benchmarking.actual_benchmark_scripts.n_100000 import random_insert, ascending_inserts, insert_duplicates_a_lot, insert_10k_delete_2k_6_times, insert_all_delete_all, insert_10k_del_2k_6_times_del_rest, intervals_of_55
from benchmarking.actual_benchmark_scripts.new_benchmarks import new_random_insert, new_insert_all_delete_all, new_insert_50_and_delete_10_many_times, new_insert_10k_and_delete_2k_many_times, new_ascending_inserts

import logging
logger = logging.getLogger(__file__)


benchmark_scripts = [random_insert, ascending_inserts, insert_duplicates_a_lot, insert_10k_delete_2k_6_times, insert_all_delete_all, insert_10k_del_2k_6_times_del_rest, intervals_of_55]
# new_benchmark_scripts = [new_random_insert, new_insert_all_delete_all, new_insert_50_and_delete_10_many_times, new_insert_10k_and_delete_2k_many_times, new_ascending_inserts]
# TODO Quick easy thing to test:
new_benchmark_scripts = [new_random_insert]


def execute_all_benchmark_scripts():
    failed_ones = []
    for script in new_benchmark_scripts:
        try:
            script.execute_benchmark()
        except Exception as e:
            logger.exception(f'Benchmark {script.__name__} failed.')
            failed_ones.append(script.__name__)

    if failed_ones:
        print(f"Some scripts failed... {failed_ones}")


if __name__ == '__main__':
    execute_all_benchmark_scripts()
