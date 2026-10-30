"""Render a selected node using the existing pinned XAX SDK inspection APIs.

This provider does not choose a mutation, generate an edit, alter a graph or build
protected code. BF authors the edit carrier; the native XAX edit/verifier applies
and verifies it. The existing foreign-language SDK query dependency is explicit.
"""
import argparse
import json
import sys
from pathlib import Path

from host.bytehost.errors import require
from host.bytehost.process import checked, pinned_executable
from host.bytehost.storage import atomic_bytes, atomic_json, digest, load


def query(spec):
    sdk = Path(spec["sdk_directory"]).absolute()
    for name, expected in spec["sdk_sha256"].items():
        require(digest(sdk / name) == expected, "TOOL_IDENTITY", "XAX query SDK differs from pin", file=name)
    git = pinned_executable(spec["git"])
    commit = checked([git, "-C", spec["repository"], "rev-parse", "HEAD"], timeout=60, max_output=4096)["stdout"].strip().decode("ascii")
    require(commit == spec["commit"], "TOOLCHAIN_COMMIT", "XAX query repository changed")
    dirty = checked([git, "-C", spec["repository"], "status", "--porcelain", "--", "compiler/src"],
                    timeout=60, max_output=1048576)["stdout"]
    require(not dirty, "TOOL_IDENTITY", "XAX query SDK worktree contains unpinned edits")
    sys.path.insert(0, str(sdk))
    import xax_compiler as X
    reader = X.StoreReader(Path(spec["source"]).read_bytes(), proof_cache=X.ProofCache())
    X.verify_store(reader)
    if "previous_query" in spec:
        previous = load(spec["previous_query"])
        require(digest(spec["previous_source"]) == previous["source_sha256"],
                "STALE", "Previous query belongs to different source bytes")
        before = X.StoreReader(Path(spec["previous_source"]).read_bytes(), proof_cache=X.ProofCache())
        old = {obj.cid for obj in before.objects() if obj.kind == X.Kind.FUNCTION}
        current = {obj.cid for obj in reader.objects() if obj.kind == X.Kind.FUNCTION}
        previous_cid = bytes.fromhex(previous["function_cid"])
        require(previous_cid in old - current, "STALE", "Previously queried function was not replaced")
        _, old_parameters, old_returns = X._decode_function_interface(before.get(previous_cid), before.get)
        candidates = []
        for cid in current - old:
            candidate = reader.get(cid)
            _, parameters, returns = X._decode_function_interface(candidate, reader.get)
            if (parameters, returns) == (old_parameters, old_returns):
                candidates.append(candidate)
        require(len(candidates) == 1, "QUERY_AMBIGUOUS", "Changed function interface does not identify a unique result")
        function = candidates[0]
    else:
        function = reader.get(bytes.fromhex(spec["function_cid"]))
    graph, parameters, returns = X._decode_function_interface(function, reader.get)
    parsed = X.parse_function_graph(function, reader.get)
    block = spec["block"]
    index = (load(spec["node_from_query"])["node"] + spec["node_delta"]
             if "node_from_query" in spec else spec["node"])
    require(0 <= block < len(parsed.blocks) and 0 <= index < len(parsed.blocks[block].nodes),
            "QUERY", "Selected node does not exist")
    node = parsed.blocks[block].nodes[index]
    destination = Path(spec["destination"])
    destination.mkdir(parents=True, exist_ok=False)
    fields = {"root.bin": reader.root_cid, "function.bin": function.cid,
              "block.uleb": X.uleb(block), "node.uleb": X.uleb(index),
              "operation.bin": X.uleb(int(node.operation)), "graph.body": graph.body,
              "graph-kind.bin": X.uleb(int(graph.kind)),
              "operand.bin": X._encode_value(node.operands[1]) if len(node.operands) > 1 else b"",
              "type.bin": node.results[0] if node.results else b""}
    for name, value in fields.items():
        atomic_bytes(destination / name, value)
    atomic_json(destination / "query.json", {"format": "XAX-SDK-NODE-OBSERVATION", "commit": commit,
                "root_cid": reader.root_cid.hex(), "function_cid": function.cid.hex(),
                "block": block, "node": index, "operation": int(node.operation),
                "operand_count": len(node.operands), "result_count": len(node.results),
                "parameter_types": [cid.hex() for cid in parameters], "return_types": [cid.hex() for cid in returns],
                "source_sha256": digest(spec["source"]), "native_query": False})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("binding")
    arguments = parser.parse_args()
    query(load(arguments.binding))
