"""Generic BF-authored fragment recipes: literal bytes and opaque buffer copies.

No XAX schema, graph mutation choice, source grammar or compiler algorithm lives
here. Recipes can assemble any byte format. The BF recipe owns its format bytes.
"""
from pathlib import Path
import os
import tempfile

from .errors import require
from .process import checked, pinned_executable
from .storage import digest, no_links


def assemble(spec):
    executable = pinned_executable(spec["worker"])
    if "request_fields" in spec:
        request = b"".join(Path(field["file"]).read_bytes() if "file" in field
                           else bytes.fromhex(field["literal_hex"]) for field in spec["request_fields"])
    else:
        request = bytes.fromhex(spec["request_hex"])
    require(len(request) == spec["request_bytes"], "RECORD_LENGTH", "Recipe request length mismatch")
    recipe = checked([executable], stdin=request, timeout=spec["timeout_seconds"],
                     max_output=spec["max_recipe_bytes"])["stdout"]
    require(recipe and recipe[-1] == 0, "RECIPE", "BF recipe refused operands")
    destination = Path(spec["destination"]).absolute()
    no_links(destination.parent)
    require(not destination.exists(), "EXISTS", "Recipe output exists")
    buffers = {int(index): Path(path) for index, path in spec["buffers"].items()}
    for buffer in buffers.values():
        no_links(buffer)
    identities = {index: digest(path) for index, path in buffers.items()}
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, pending = tempfile.mkstemp(prefix=".pending-", dir=destination.parent)
    position = 0
    try:
        with os.fdopen(fd, "wb") as output:
            while position < len(recipe) - 1:
                require(position + 2 <= len(recipe) - 1, "RECIPE", "Truncated recipe instruction")
                opcode, operand = recipe[position:position + 2]
                position += 2
                if opcode == 1:
                    output.write(bytes([operand]))
                else:
                    require(operand in buffers, "RECIPE", "Missing opaque operand buffer")
                    path = buffers[operand]
                    if opcode == 2:
                        with path.open("rb") as source:
                            for block in iter(lambda: source.read(1024 * 1024), b""):
                                output.write(block)
                                require(output.tell() <= spec["max_output_bytes"], "OUTPUT_BUDGET", "Recipe output exceeds budget")
                    elif opcode == 3:
                        require(path.stat().st_size == 32, "RECIPE", "Expected 32-byte operand")
                    elif opcode == 4:
                        with path.open("rb") as source:
                            require(any(byte for block in iter(lambda: source.read(4096), b"") for byte in block),
                                    "RECIPE", "Expected nonzero opaque operand")
                    elif opcode == 5:
                        # Canonical unsigned LEB128; no fixed-width numeric ceiling.
                        data = path.read_bytes()
                        require(data and not (data[-1] & 128) and
                                all(byte & 128 for byte in data[:-1]) and
                                (len(data) == 1 or data[-1] != 0), "RECIPE", "Noncanonical ULEB operand")
                    else:
                        require(False, "RECIPE", "Unknown fragment instruction")
                require(output.tell() <= spec["max_output_bytes"], "OUTPUT_BUDGET", "Recipe output exceeds budget")
            output.flush()
            os.fsync(output.fileno())
        require(all(digest(path) == identities[index] for index, path in buffers.items()), "CHANGED", "Recipe operand changed")
        os.link(pending, destination)
    finally:
        os.unlink(pending)
    return {"bytes": destination.stat().st_size, "sha256": digest(destination)}
