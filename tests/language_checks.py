"""Independent Java/Kotlin builds and boundary-value behavior/bytecode checks.

Run inside the declared isolated environment. This contains verification logic,
not a CUM source transformation. Fixtures are compiled with real public tools.
"""
import argparse
import os
import random
import re
import tempfile
from pathlib import Path

from host.bytehost.errors import require
from host.bytehost.process import checked, pinned_executable
from host.bytehost.storage import atomic_json, load, digest


def verify(spec, case):
    java = pinned_executable(spec["java"])
    javac = pinned_executable(spec["javac"])
    records, signatures, runtimes, artifact_sizes = [], [], [], []
    with tempfile.TemporaryDirectory(prefix="independent-jvm-") as temporary:
        contexts = []
        for label in ("original", "protected"):
            source = Path(spec[label])
            output = Path(temporary) / label
            output.mkdir()
            if spec["language"] == "java":
                compiled = checked([javac, "-g:none", "-d", str(output), str(source), spec["runner"]],
                                   timeout=spec["compile_timeout_seconds"], max_output=spec["max_log_bytes"])
                classpath = str(output)
                if label == "protected":
                    artifact_sizes.append(sum(path.stat().st_size for path in output.glob("Arithmetic*.class")))
            else:
                jar = output / "application.jar"
                for path, expected in spec["kotlinc"].get("inputs_sha256", {}).items():
                    require(digest(path) == expected, "TOOL_IDENTITY", "Kotlin compiler input differs from pin")
                compiled = checked([pinned_executable(spec["kotlinc"]), *spec["kotlinc"].get("argv", []),
                                    str(source), "-include-runtime", "-d", str(jar)],
                                   timeout=spec["compile_timeout_seconds"], max_output=spec["max_log_bytes"])
                checked([javac, "-g:none", "-cp", str(jar), "-d", str(output), spec["runner"]],
                        timeout=spec["compile_timeout_seconds"], max_output=spec["max_log_bytes"])
                classpath = str(output) + os.pathsep + str(jar)
                if label == "protected":
                    artifact_sizes.append(jar.stat().st_size)
            contexts.append(classpath)
            records.append({"side": label, "compile_wall_seconds": compiled["wall_seconds"], "resources": compiled["resources"]})
            if case == "normalization":
                disassembly = checked([pinned_executable(spec["javap"]), "-c", "-p", "-classpath", classpath, "Arithmetic"],
                                      timeout=spec["compile_timeout_seconds"], max_output=spec["max_log_bytes"])["stdout"].decode("utf-8")
                instructions = [re.sub(r"^\s*[0-9]+:\s*", "", line).strip() for line in disassembly.splitlines()
                                if re.match(r"^\s*[0-9]+:", line)]
                require(instructions, "NORMALIZATION", "No JVM instructions observed")
                signatures.append(instructions)
        if case == "normalization":
            require(signatures[0] != signatures[1], "NORMALIZATION", "Public compiler erased all executable changes")
        if case in ("behavior", "budgets", "development"):
            dataset = [(0, 0), (1, -1), (-2147483648, -1), (2147483647, 1), (-2147483648, 2147483647)]
            rng = random.Random(spec["seed"])
            dataset.extend((rng.randrange(-2147483648, 2147483648), rng.randrange(-2147483648, 2147483648))
                           for _ in range(spec["random_cases"]))
            for left, right in dataset:
                results = [checked([java, "-cp", classpath, "Runner", str(left), str(right)],
                                   timeout=spec["runtime_timeout_seconds"], max_output=spec["max_log_bytes"]) for classpath in contexts]
                require(results[0]["stdout"] == results[1]["stdout"], "SEMANTICS", "JVM outputs differ", left=left, right=right)
                if case == "budgets":
                    runtimes.append(results[1]["wall_seconds"])
                    if spec.get("enforce_numeric_budgets", True):
                        require(results[1]["wall_seconds"] <= spec["max_runtime_seconds"], "BUDGET", "JVM runtime budget exceeded")
    atomic_json(spec["report"], {"format": "INDEPENDENT-JVM-CHECK", "case": case, "status": "PASS",
                "language": spec["language"], "records": records,
                "compiler_sha256": spec["javac"]["sha256"] if spec["language"] == "java" else spec["kotlinc"]["sha256"],
                "compiler_inputs_sha256": spec.get("kotlinc", {}).get("inputs_sha256", {}) if spec["language"] == "kotlin" else {},
                "jdk_sha256": spec["java"]["sha256"],
                "metrics": {"source_expansion_ratio": Path(spec["protected"]).stat().st_size / max(1, Path(spec["original"]).stat().st_size),
                            "max_binary_bytes": max(artifact_sizes) if artifact_sizes else None,
                            "max_runtime_seconds": max(runtimes) if runtimes else None},
                "scope": "Declared Arithmetic integer-module domain only"})


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("case", choices=("build", "behavior", "normalization", "budgets", "development"))
    parser.add_argument("binding")
    arguments = parser.parse_args()
    verify(load(arguments.binding), arguments.case)
