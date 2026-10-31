"""Independent BF instruction/run/affine-loop normalization for comparison.

Pointer motion is retained to preserve first-crossing failures. This analysis
tool is independent of the CUM production emitter and is never called to produce
protected source. More powerful independent attacks remain separate experiments.
"""
import argparse
import json
from pathlib import Path


def loop_form(body):
    offset = low = high = 0
    changes = {}
    for instruction in body:
        if instruction[0] == "add":
            changes[offset] = (changes.get(offset, 0) + instruction[1]) % 256
        elif instruction[0] in ("right", "left"):
            offset += 1 if instruction[0] == "right" else -1
            low, high = min(low, offset), max(high, offset)
        else:
            return ["loop", body]
    counter = changes.get(0, 0)
    if offset or counter % 2 == 0:
        return ["loop", body]
    if low == high == 0:
        return ["clear"]
    # Excursions retain conditional bounds failures; a zero counter skips them.
    inverse = pow(counter, -1, 256)
    transfers = [[position, (-amount * inverse) % 256]
                 for position, amount in sorted(changes.items()) if position and amount]
    return ["affine", transfers, [low, high]]


def normalize(source):
    commands = bytes(value for value in source if value in b"><+-.,[]")
    stack = [[]]
    index = 0
    while index < len(commands):
        command = commands[index]
        if command in (43, 45):
            amount = 0
            while index < len(commands) and commands[index] in (43, 45):
                amount += 1 if commands[index] == 43 else -1
                index += 1
            if amount % 256:
                stack[-1].append(["add", amount % 256])
            continue
        if command == 91:
            stack.append([])
        elif command == 93:
            if len(stack) == 1:
                raise ValueError("unmatched close")
            body = stack.pop()
            stack[-1].append(loop_form(body))
        else:
            stack[-1].append([{62: "right", 60: "left", 46: "output", 44: "input"}[command]])
        index += 1
    if len(stack) != 1:
        raise ValueError("unmatched open")
    return stack[0]


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    arguments = parser.parse_args()
    print(json.dumps(normalize(Path(arguments.source).read_bytes()), separators=(",", ":")))
