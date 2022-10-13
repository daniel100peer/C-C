import dataclasses
import struct
import typing
from typing import List
import typer


def pack_data(data: bytes):
    return struct.pack('<I', len(data)) + data


def unpack_data(data: bytes):
    msgs = []
    len_size = struct.calcsize('<I')
    while len(data) > len_size:
        length = struct.unpack('<I', data[:len_size])[0]
        if len(data) < length + len_size:
            break

        msgs.append(data[len_size:len_size + length])
        data = data[len_size + length:]

    return msgs, data

@dataclasses.dataclass
class Command:
    command_payload: bytes
    command_type: str
    command_identifier: int
    command_payload_arguments: List[str]


@dataclasses.dataclass
class Disconnect:
    pass


@dataclasses.dataclass
class KeepAlive:
    ip: str
    port: int
