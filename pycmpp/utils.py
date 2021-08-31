import hashlib
import struct
import time

_global_seq_no = 0


def get_md5_digest(source_data):
    return hashlib.md5(source_data).digest()


class Unpack(object):
    @staticmethod
    def get_unsigned_long_data(source_data):
        return struct.unpack("!L", source_data)

    @staticmethod
    def get_unsigned_char_data(source_data):
        return struct.unpack("!B", source_data)

    @staticmethod
    def get_unsigned_long_long_data(source_data):
        return struct.unpack("!Q", source_data)


class Pack(object):
    @staticmethod
    def get_unsigned_long_data(source_data):
        return struct.pack("!L", source_data)

    @staticmethod
    def get_unsigned_char_data(source_data):
        return struct.pack("!B", source_data)


def parse_packet_head(message):
    t_len = Unpack.get_unsigned_long_data(message[:4])
    cm_id = Unpack.get_unsigned_long_data(message[4:8])
    seq_id = Unpack.get_unsigned_long_data(message[8:12])
    return t_len, cm_id, seq_id


def get_string_time():
    return time.strftime('%m%d%H%M%S', time.localtime(time.time()))


def split_message(content: str, size=64):
    cursor = 0
    split_messages = []
    for x in range(size, len(content), size):
        split_messages.append(content[cursor: x])
        cursor = x

    if cursor < len(content):
        split_messages.append(content[cursor:])

    return split_messages


def get_sequence_no():
    global _global_seq_no
    if _global_seq_no >= 2 ** 31:
        _global_seq_no = 1
    else:
        _global_seq_no += 1
    return _global_seq_no


def decode_headers(message):
    length, = Unpack.get_unsigned_long_data(message[0:4])
    command_id, = Unpack.get_unsigned_long_data(message[4:8])
    sequence, = Unpack.get_unsigned_long_data(message[8:12])
    return length, command_id, sequence
