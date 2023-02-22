def create_string_from_int_biggest_number(number, biggest_number, string_length=None):
    first = str(number).zfill(len(str(biggest_number)))
    if string_length:
        num_chars_missing = string_length - len(first)
        first += 'x' * num_chars_missing
    return first


def create_string_from_int_with_byte_size(number, byte_size):
    string = str(number).zfill(byte_size)
    if len(string) > byte_size:
        raise ValueError(f"Number {number} too big to create comparable string with byte_size {byte_size} for it")

    return string
