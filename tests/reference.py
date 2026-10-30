"""Independent generic BF interpreter used only for differential verification.

This is not a production compiler or a CUM transformation implementation. Memory
grows on demand. Step and output limits are caller-selected measurement budgets.
"""
from dataclasses import dataclass


@dataclass
class Result:
    output: bytes
    pointer: int
    tape: bytes
    consumed: int
    steps: int


def execute(source, data=b"", *, steps=50000000, output_bytes=1048576):
    commands = bytes(byte for byte in source if byte in b"><+-.,[]")
    stack, jumps = [], {}
    for pc, command in enumerate(commands):
        if command == 91:
            stack.append(pc)
        elif command == 93:
            if not stack:
                raise ValueError("unmatched close")
            start = stack.pop()
            jumps[start], jumps[pc] = pc, start
    if stack:
        raise ValueError("unmatched open")
    tape, output = bytearray(1), bytearray()
    pointer = pc = cursor = count = 0
    while pc < len(commands):
        if count >= steps:
            raise TimeoutError("independent interpreter step budget")
        count += 1
        command = commands[pc]
        if command == 62:
            pointer += 1
            if pointer == len(tape):
                tape.append(0)
        elif command == 60:
            if pointer == 0:
                raise IndexError("negative pointer")
            pointer -= 1
        elif command == 43:
            tape[pointer] = (tape[pointer] + 1) & 255
        elif command == 45:
            tape[pointer] = (tape[pointer] - 1) & 255
        elif command == 44:
            tape[pointer] = data[cursor] if cursor < len(data) else 0
            cursor += cursor < len(data)
        elif command == 46:
            if len(output) >= output_bytes:
                raise BufferError("independent interpreter output budget")
            output.append(tape[pointer])
        elif command == 91 and tape[pointer] == 0:
            pc = jumps[pc]
        elif command == 93 and tape[pointer] != 0:
            pc = jumps[pc]
        pc += 1
    return Result(bytes(output), pointer, bytes(tape), cursor, count)
