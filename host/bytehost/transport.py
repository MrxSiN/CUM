"""Complete-record transport; zero data is never a physical EOF indicator."""
import hashlib
import io
import json
from pathlib import Path

from .errors import require
from .storage import canonical

MAGIC = b"BFRAME\x00\x01"


def varint(value):
    require(isinstance(value, int) and value >= 0, "LENGTH", "Expected nonnegative integer")
    result = bytearray()
    while value >= 128:
        result.append((value & 127) | 128)
        value >>= 7
    result.append(value)
    return bytes(result)


def exact(stream, size):
    result = bytearray()
    while len(result) < size:
        block = stream.read(size - len(result))
        require(block, "TRUNCATED", "Physical EOF inside a declared record", expected=size, received=len(result))
        result.extend(block)
    return bytes(result)


def frame(header, payload):
    header = dict(header, payload_bytes=str(len(payload)))
    encoded = canonical(header)
    body = MAGIC + varint(len(encoded)) + encoded + payload
    return body + hashlib.sha256(body).digest()


def read_frame(stream, *, max_header, max_payload):
    first = stream.read(1)
    require(first, "PHYSICAL_EOF", "No record present")
    prefix = first + exact(stream, len(MAGIC) - 1)
    require(prefix == MAGIC, "FORMAT", "Unknown frame identifier")
    length, shift, encoded_length = 0, 0, bytearray()
    while True:
        byte = exact(stream, 1)[0]
        encoded_length.append(byte)
        length |= (byte & 127) << shift
        require(len(encoded_length) <= max_header and length <= max_header,
                "HEADER_BUDGET", "Frame header exceeds negotiated budget")
        if not byte & 128:
            break
        shift += 7
    require(bytes(encoded_length) == varint(length), "FORMAT", "Noncanonical length encoding")
    header_bytes = exact(stream, length)
    header = json.loads(header_bytes)
    require(canonical(header) == header_bytes, "FORMAT", "Noncanonical or duplicate frame fields")
    require(set(header) == {"operation", "request", "sequence", "state", "payload_bytes"},
            "FORMAT", "Unknown or missing frame fields")
    for key in ("sequence", "payload_bytes"):
        value = header[key]
        require(isinstance(value, str) and value.isascii() and value.isdecimal() and
                (value == "0" or not value.startswith("0")), "FORMAT", "Noncanonical integer field")
    count = int(header["payload_bytes"])
    require(count <= max_payload, "PAYLOAD_BUDGET", "Record exceeds negotiated transport budget")
    payload = exact(stream, count)
    checksum = exact(stream, 32)
    body = prefix + bytes(encoded_length) + header_bytes + payload
    require(checksum == hashlib.sha256(body).digest(), "INTEGRITY", "Frame checksum mismatch")
    require(stream.read(1) == b"", "TRAILING", "One exchange accepts exactly one record")
    return header, payload


def worker_input(state, payload):
    """A complete pair stream: state bytes, (one,data)*, zero terminator.

    Physical completeness is established outside BF before this function is used.
    The terminator is a marker position, never a data position.
    """
    require(len(state) == 2, "STATE", "Worker ABI requires exactly two opaque state bytes")
    result = bytearray(state)
    for byte in payload:
        result.extend((1, byte))
    result.append(0)
    return bytes(result)


def worker_output(data):
    require(len(data) >= 3, "WORKER_RESPONSE", "Missing worker response trailer")
    status = data[-1]
    require(status == 0, "WORKER_REJECT", "BF worker rejected record", worker_status=status)
    return data[:-3], data[-3:-1]
