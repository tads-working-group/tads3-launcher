import re
import sys


def search_loop(pattern, fh_name, fh_read, fh_seek):
    bsize = len(b"".join(pattern)) * 2
    bsize = max(bsize, 2**23)

    len_pattern = len(b"?".join(pattern))  # Byte length of pattern.
    read_size = bsize - len_pattern  # Amount to read each loop.

    # Convert pattern into a regular expression for insane fast searching.
    pattern = [re.escape(p) for p in pattern]
    pattern = b".".join(pattern)
    # Grab regex search function directly to speed up function calls.
    regex_search = re.compile(pattern, re.DOTALL + re.MULTILINE).search

    offset = 0
    # Set start reading position in file.
    try:
        if offset:
            fh_seek(offset)
    except IOError:
        e = sys.exc_info()[1]
        raise e

    buffer = fh_read(len_pattern + read_size)  # Get initial buffer amount.
    match = regex_search(buffer)  # Search for a match in the buffer.
    # Set match to -1 if no match, else set it to the match position.
    match = -1 if match == None else match.start()

    while True:  # Begin main loop for searching through a file.
        if match == -1:  # No match.
            offset += read_size
            # If end exists and we are beyond end, finish search.
            buffer = buffer[read_size:]  # Erase front portion of buffer.
            buffer += fh_read(read_size)  # Read more into the buffer.
            match = regex_search(buffer)  # Search for next match in the buffer.
            # If there is no match set match to -1, else the matching position.
            match = -1 if match == None else match.start()
        else:
            # Print matched offset
            find_offset = offset + match
            print(
                "Match at offset: %14d %12X in  %s\n"
                % (find_offset, find_offset, fh_name)
            )
            return True

        if len(buffer) <= len_pattern:  # If finished reading input then end.
            return False
