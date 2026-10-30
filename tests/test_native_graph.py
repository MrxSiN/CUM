"""Opt-in native graph regression: four verified edits, not one invalid batch."""
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

from host.bytehost.assembly import assemble
from host.bytehost.process import run
from host.bytehost.storage import atomic_json, digest
from host.providers.xax_query import query
from tests.graph_checks import verify


@unittest.skipUnless(os.environ.get("BYTEHOST_NATIVE_GRAPH") == "1", "Native graph test requires explicit tool opt-in")
class NativeGraphTests(unittest.TestCase):
    def test_each_edit_is_verified_and_final_program_remains_correct(self):
        repository = Path(os.environ["BYTEHOST_XAX_REPOSITORY"])
        sdk = repository / "compiler/src"
        sys.path.insert(0, str(sdk))
        import xax_compiler as X
        import xax_build as B
        # Author the fixture through the actual BBC frontend, not textual XAX.
        fixture_directory = tempfile.TemporaryDirectory(prefix="native-graph-source-")
        self.addCleanup(fixture_directory.cleanup)
        fixture = Path(fixture_directory.name) / "input.exe"
        bbc = Path(os.environ["BYTEHOST_BBC_EXECUTABLE"])
        built = run([str(bbc), "compile", "windows-x86_64", "-O1", str(fixture)], stdin=b",+.", timeout=120)
        self.assertEqual(built["exit"], 0)
        self.assertEqual(run([str(fixture)], stdin=b"\x01", timeout=10)["stdout"], b"\x02")
        snapshot = fixture.with_suffix(".exe.xax")
        reader = X.StoreReader(snapshot.read_bytes())
        request_root = B.decode_snapshot(reader.get(reader.root_cid), reader.get).request_root
        # A resolved snapshot is not an editable build request. Export its existing request closure.
        reachable, pending = set(), [request_root]
        while pending:
            cid = pending.pop()
            if cid not in reachable:
                reachable.add(cid)
                pending.extend(reader.get(cid).references)
        git = shutil.which("git")
        seed = Path(os.environ.get("BYTEHOST_XAX_EXECUTABLE", str(repository / "compiler/bootstrap/windows/xaxc-windows-x86_64.exe")))
        worker = Path(os.environ["BYTEHOST_NATIVE_DIRECTORY"]) / "add_negate.exe"
        commit = run([git, "-C", str(repository), "rev-parse", "HEAD"])["stdout"].strip().decode()
        with tempfile.TemporaryDirectory(prefix="native-four-step-graph-") as temporary:
            root = Path(temporary)
            original = root / "original.xax"
            original.write_bytes(X.write_store(request_root, [reader.get(cid) for cid in reachable]))
            previous = original
            for stage in range(4):
                directory = root / ("query" + str(stage))
                spec = {"sdk_directory": str(sdk), "sdk_sha256": {name: digest(sdk / name) for name in ("xax_compiler.py", "xax_workspace.py")},
                        "repository": str(repository), "commit": commit, "git": {"executable": git, "sha256": digest(git)},
                        "source": str(previous), "destination": str(directory)}
                if stage == 0:
                    selected = []
                    for function in reader.objects():
                        if function.kind != X.Kind.FUNCTION:
                            continue
                        parsed = X.parse_function_graph(function, reader.get)
                        for block_index, block in enumerate(parsed.blocks):
                            for node_index, node in enumerate(block.nodes):
                                if node.operation == X.Operation.ADD_WRAP and reader.get(node.results[0]).body == b"\x01\x08":
                                    selected.append((function.cid.hex(), block_index, node_index))
                    self.assertEqual(len(selected), 1)
                    function_cid, block_index, node_index = selected[0]
                    spec.update(function_cid=function_cid, block=block_index, node=node_index)
                else:
                    spec["block"] = block_index
                    spec.update(previous_query=str(root / ("query" + str(stage - 1)) / "query.json"),
                                previous_source=str(original if stage == 1 else root / ("stage" + str(stage - 2) + ".xax")),
                                node_from_query=str(root / ("query" + str(stage - 1)) / "query.json"), node_delta=1 if stage < 3 else 0)
                query(spec)
                request = b"\x02" + (directory / "operation.bin").read_bytes() + (directory / "graph-kind.bin").read_bytes() + bytes([stage])
                buffers = {str(index): str(directory / name) for index, name in enumerate(("root.bin", "function.bin", "block.uleb", "node.uleb", "operand.bin", "type.bin"))}
                buffers["6"] = str(root / "query0/node.uleb")
                if stage:
                    buffers["7"] = str(root / "query1/node.uleb")
                transaction, candidate = root / ("stage" + str(stage) + ".edit"), root / ("stage" + str(stage) + ".xax")
                assemble({"worker": {"executable": str(worker), "sha256": digest(worker)}, "request_hex": request.hex(), "request_bytes": 4,
                          "timeout_seconds": 30, "max_recipe_bytes": 65536, "max_output_bytes": 1048576,
                          "destination": str(transaction), "buffers": buffers})
                for command, arguments in (("edit", [str(previous), str(transaction), str(candidate)]),
                                           ("verify", [str(candidate), str(root / ("stage" + str(stage) + ".diag"))])):
                    result = run([str(seed), command, *arguments], timeout=120, max_output=1048576,
                                 env=dict(os.environ, XAX_REQUIRE_NATIVE="1"))
                    diagnostic = candidate.read_bytes().hex() if result["exit"] and candidate.exists() else ""
                    self.assertEqual(result["exit"], 0, (stage, command, diagnostic, result["stderr"]))
                previous = candidate
            verify({"compiler": {"executable": str(seed), "sha256": digest(seed)}, "original": str(original), "protected": str(previous),
                    "timeout_seconds": 120, "runtime_timeout_seconds": 10, "require_native_code_change": True,
                    "inputs_hex": ["", "00", "01", "ff"], "report": str(root / "graph-behavior.json")})
            replay = run([str(seed), "edit", str(previous), str(root / "stage0.edit"), str(root / "replay.xax")], timeout=120)
            self.assertNotEqual(replay["exit"], 0)
            if os.environ.get("BYTEHOST_GRAPH_EVIDENCE"):
                atomic_json(os.environ["BYTEHOST_GRAPH_EVIDENCE"], {
                    "format": "NATIVE-FOUR-TRANSACTION-GRAPH-CHECK", "status": "PASS",
                    "bbc_sha256": digest(bbc), "xax_executable_sha256": digest(seed), "sdk_commit": commit,
                    "worker_sha256": digest(worker), "original_sha256": digest(original),
                    "protected_sha256": digest(previous), "replay_exit": replay["exit"],
                    "inputs_hex": ["", "00", "01", "ff"], "native_code_change": "PASS",
                    "stages": [{"query": json.loads((root / ("query" + str(stage)) / "query.json").read_text()),
                                "carrier_sha256": digest(root / ("stage" + str(stage) + ".edit")),
                                "candidate_sha256": digest(root / ("stage" + str(stage) + ".xax")),
                                "native_edit": "PASS", "native_verify": "PASS"} for stage in range(4)],
                    "behavior": json.loads((root / "graph-behavior.json").read_text())})
