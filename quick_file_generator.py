import time

comparison_lines = 3000000


def generate_dummy_file_line_by_line(file_path, amount):
    with open(file_path, 'a') as f:
        for i in range(amount):
            f.write(f'This is line {i}\n')


def generate_dummy_file_all_lines(file_path, amount):
    with open(file_path, 'w') as f:
        lines = [f'This is line {i}\n' for i in range(amount)]
        f.writelines(lines)


def blabla_line_by_line_generator():
    start = time.time()
    amount = 1000000
    file_path = r'C:\Users\marua\PycharmProjects\BT_TreeBuffer\blabla_line_by_line.txt'
    generate_dummy_file_line_by_line(file_path, comparison_lines)
    end = time.time()

    print(f'Execution time line by line: {end - start}')


def blabla_all_lines_generator():
    start = time.time()
    file_path = r'C:\Users\marua\PycharmProjects\BT_TreeBuffer\blabla_all_lines.txt'
    amount = 1000000
    generate_dummy_file_all_lines(file_path, comparison_lines)
    end = time.time()

    print(f'Execution time all lines: {end - start}')


def compare_file_generators():
    blabla_line_by_line_generator()
    blabla_all_lines_generator()


def read_directly_line_by_line():
    start = time.time()
    file_path = r'C:\Users\marua\PycharmProjects\BT_TreeBuffer\blabla_all_lines.txt'

    counter = 0
    for line in open(file_path, 'r'):
        counter += len(line)

    print(counter)
    end = time.time()
    return end - start


def read_then_line_by_line():
    start = time.time()

    file_path = r'C:\Users\marua\PycharmProjects\BT_TreeBuffer\blabla_all_lines.txt'
    with open(file_path, 'r') as f:
        data = f.readlines()

    counter = 0
    for line in data:
        counter += len(line)

    print(counter)
    end = time.time()
    return end - start


def as_then_directly_iterate():
    start = time.time()

    file_path = r'C:\Users\marua\PycharmProjects\BT_TreeBuffer\blabla_all_lines.txt'
    counter = 0
    with open(file_path, 'r') as f:
        for line in f:
            counter += len(line)

    print(counter)
    end = time.time()
    return end - start


def compare_file_readers():
    first = read_directly_line_by_line()
    # second = read_then_line_by_line()
    third = as_then_directly_iterate()

    print(f'First duration: {first}')
    # print(f'Second duration: {second}')
    print(f'Third duration: {third}')


if __name__ == '__main__':
    compare_file_generators()
