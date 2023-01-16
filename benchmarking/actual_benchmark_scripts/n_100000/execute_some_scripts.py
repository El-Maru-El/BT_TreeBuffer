from benchmarking.actual_benchmark_scripts.n_100000 import random_insert, ascending_inserts, insert_duplicates_a_lot, insert_10k_delete_2k_6_times, insert_all_delete_all, insert_10k_del_2k_6_times_del_rest, intervals_of_55
import logging
logger = logging.getLogger(__file__)


benchmark_scripts = [random_insert, ascending_inserts, insert_duplicates_a_lot, insert_10k_delete_2k_6_times, insert_all_delete_all, insert_10k_del_2k_6_times_del_rest, intervals_of_55]


def execute_all_benchmark_scripts():
    failed_ones = []
    for script in benchmark_scripts:
        try:
            script.execute_benchmark()
        except Exception as e:
            logger.exception(f'Benchmark {script.__name__} failed.')
            failed_ones.append(script.__name__)


if __name__ == '__main__':
    execute_all_benchmark_scripts()
