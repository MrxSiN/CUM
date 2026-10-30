"""Generic measured-record collection and isolated paired samples.

External counters are imported as explicit tool-produced measurements. Missing
CPU/RAM/counter evidence remains BLOCKED rather than substituted with estimates.
"""
import math
import platform
import random
import statistics
from .errors import require
from .process import isolated
from .storage import atomic_json, load, digest


def collect(spec):
    values, origins = {}, {}
    for name, operand in spec["measurements"].items():
        record = load(operand["file"])
        value = record[operand["field"]]
        require(isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value),
                "METRIC", "Required finite numeric measurement missing", metric=name)
        values[name] = value
        origins[name] = {"file_sha256": digest(operand["file"]), "field": operand["field"]}
    atomic_json(spec["destination"], {"format": "MEASURED-RESOURCE-SET", "values": values,
                "origins": origins, "context": spec["context"]})


def paired(spec):
    require(spec["repetitions"] > 0 and len(spec["arms"]) >= 2, "SAMPLES", "Two arms and positive repetitions required")
    correctness = load(spec["correctness_report"])
    require(correctness["status"] == "PASS", "EVIDENCE", "Correctness must precede timing")
    schedule = random.Random(spec["order_seed"])
    samples = {name: [] for name in spec["arms"]}
    order = []
    for repeat in range(spec["repetitions"]):
        names = list(spec["arms"])
        schedule.shuffle(names)
        for name in names:
            result = isolated(spec["arms"][name])
            samples[name].append(result["wall_seconds"])
            order.append({"repeat": repeat, "arm": name})
    summary = {name: {"samples_seconds": values, "median_seconds": statistics.median(values),
                     "min_seconds": min(values), "max_seconds": max(values),
                     "population_stddev_seconds": statistics.pstdev(values)} for name, values in samples.items()}
    atomic_json(spec["destination"], {"format": "PAIRED-ISOLATED-WALL-SAMPLES", "samples": summary,
                "execution_order": order, "context": spec["context"], "host": platform.platform(),
                "peak_memory": None, "peak_memory_status": "BLOCKED", "cold_warm": spec["cold_warm"]})
