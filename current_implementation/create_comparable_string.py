def create_string_from_int(number, biggest_number, string_length=None):
    first = str(number).zfill(len(str(biggest_number)))
    if string_length:
        num_chars_missing = string_length - len(first)
        first += 'x' * num_chars_missing
    return first
