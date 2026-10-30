"""Generic Linux cgroup-v2 process measurement, intended inside a fresh container.

This wrapper does not parse application source or make release decisions. It
records OS counters with their actual scope instead of estimating tree RAM from
individual process working sets. A missing counter is an error.
"""
import argparse
import json
import sys
from pathlib import Path

from host.bytehost.errors import require
from host.bytehost.process import checked
from host.bytehost.storage import canonical, load


def cpu():
    values = {}
    for line in Path("/sys/fs/cgroup/cpu.stat").read_text().splitlines():
        name, value = line.split()
        values[name] = int(value)
    require("usage_usec" in values, "METRIC", "cgroup-v2 CPU counter unavailable")
    return values


def observe(spec):
    before = cpu()
    result = checked(spec["argv"], stdin=bytes.fromhex(spec.get("stdin_hex", "")),
                     timeout=spec["timeout_seconds"], max_output=spec["max_output_bytes"], cwd=spec.get("cwd"))
    after = cpu()
    peak = int(Path("/sys/fs/cgroup/memory.peak").read_text().strip())
    require(peak > 0 and after["usage_usec"] >= before["usage_usec"], "METRIC", "Invalid cgroup observation")
    return {"format": "CGROUP-PROCESS-OBSERVATION", "status": "PASS", "exit": result["exit"],
            "wall_seconds": result["wall_seconds"], "cpu_seconds": (after["usage_usec"] - before["usage_usec"]) / 1000000,
            "peak_memory_bytes": peak, "stdout_hex": result["stdout"].hex(), "stderr_hex": result["stderr"].hex(),
            "scope": "whole fresh container memory peak since creation; CPU delta around selected command",
            "assumption": "caller provisions one fresh, isolated container per measurement"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("binding")
    args = parser.parse_args()
    sys.stdout.buffer.write(canonical(observe(load(args.binding))))
