"""Generic BF instruction/run/clear normalization for adversarial comparison.

Pointer motion is retained to preserve first-crossing failures. This analysis
tool is independent of the CUM production emitter and is never called to produce
protected source. More powerful independent attacks remain separate experiments.
"""
import argparse
import json
from pathlib import Path


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
            stack[-1].append(["clear"] if body in ([["add", 1]], [["add", 255]]) else ["loop", body])
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
