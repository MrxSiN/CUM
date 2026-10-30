"""Opaque byte-program dispatch and tree mapping, with no extension classifier."""
import os
from pathlib import Path

from .errors import require
from .machine import transduce
from .process import checked, pinned_executable
from .storage import atomic_json, confined


def machine_tree(spec):
    results = []
    require(spec["paths"], "SCOPE", "Explicit machine source operands required")
    for index, name in enumerate(spec["paths"]):
        source = confined(spec.get("input_root", spec["root"]), name)
        target = confined(spec["root"], name)
        require(target.is_file(), "SCOPE", "Mapping target is outside approved public projection")
        destination = target.with_name(target.name + ".mapped")
        request = dict(spec["machine"], source=str(source), destination=str(destination),
                       journal=str(Path(spec["journal_directory"]) / (str(index) + ".json")))
        record = transduce(request)
        os.replace(destination, target)
        results.append({"path": name, **record})
    atomic_json(spec["report"], {"format": "BYTE-MAP-REPORT", "files": results})
    return results


def dispatch_list(spec):
    # Import only after the VM service table has been initialized.
    from .vm import SERVICES
    results = []
    require(spec["items"], "SCOPE", "No explicit dispatch items")
    for item in spec["items"]:
        executable = pinned_executable(item["worker"])
        request = bytes.fromhex(item["request_hex"])
        require(len(request) == item["request_bytes"], "RECORD_LENGTH", "Incomplete dispatch request")
        response = checked([executable], stdin=request, timeout=item["timeout_seconds"],
                           max_output=item["max_response_bytes"])["stdout"]
        require(len(response) == 3 and response[-1] == 0, "DISPATCH", "BF refused adapter dispatch")
        opcode, binding = response[:2]
        require(opcode in SERVICES and str(binding) in item["bindings"], "DISPATCH", "Missing BF-selected primitive/operand")
        result = SERVICES[opcode](item["bindings"][str(binding)])
        results.append({"opcode": opcode, "operand": binding, "result": result})
    if "report" in spec:
        atomic_json(spec["report"], {"format": "BYTE-DISPATCH-REPORT", "items": results})
    return results
