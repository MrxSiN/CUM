"""Independent fixture checks inside a credential-free release-check VM."""
import json
from html.parser import HTMLParser
from pathlib import Path
import sys

from host.bytehost.errors import HostError, require
from host.bytehost.storage import digest, load, atomic_json
from tests.native_checks import verify
from tests.machine_checks import verify as machine_verify


class Document(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.tags, self.text = [], []
        self.feed(text)
        self.close()

    def handle_starttag(self, tag, attrs):
        require(tag in {"html", "head", "title", "body", "h1", "h2", "p", "pre", "code"},
                "FIXTURE", "Unsupported fixture document tag")
        self.tags.append(("open", tag, attrs))

    def handle_endtag(self, tag):
        self.tags.append(("close", tag))

    def handle_data(self, value):
        self.text.append(value)


def presentation(original, protected):
    source, result = (Path(root) / "main.bf" for root in (original, protected))
    commands = b"><+-.,[]"
    comments = bytes(byte for byte in result.read_bytes() if byte not in commands).decode("ascii")
    require("Stream input staging" in comments and "Accumulator transition" in comments,
            "PRESENTATION", "Protected BF lost its non-executable annotations")
    require(bytes(byte for byte in source.read_bytes() if byte in commands) !=
            bytes(byte for byte in result.read_bytes() if byte in commands),
            "STRUCTURAL", "Comments alone cannot establish executable camouflage")
    documents = []
    for name in ("README.html", "docs/usage.html"):
        before, after = (Path(root) / name for root in (original, protected))
        left, right = Document(before.read_text()), Document(after.read_text())
        require(left.tags == right.tags and "".join(left.text) == "".join(right.text),
                "DOCUMENT", "Rendered fixture documentation changed")
        require(before.read_bytes() != after.read_bytes() and "&#x" in after.read_text(),
                "DOCUMENT", "Document source was not transformed")
        documents.append({"path": name, "original_sha256": digest(before), "protected_sha256": digest(after),
                          "rendered_text_sha256": __import__("hashlib").sha256("".join(right.text).encode()).hexdigest()})
    require((Path(original) / "LICENSE").read_bytes() == (Path(protected) / "LICENSE").read_bytes(),
            "LICENSE", "Distribution terms changed")
    return documents


def main():
    case, binding_path = sys.argv[1:]
    binding = load(binding_path)
    launcher = {"executable": "/usr/lib/wine/wine64", "sha256": digest("/usr/lib/wine/wine64")}
    if case == "machine-boundary":
        for name in ("fixed", "real"):
            binding[name]["launcher"] = launcher
        machine_verify(binding)
    else:
        binding["launcher"] = launcher
        documents = presentation(binding["original"], binding["protected"])
        verify(binding, case)
        report = load(binding["report"])
        report["documents"] = documents
        report["input_hex"] = binding["fixtures"][0]["input_hex"]
        report["source_files"] = {side: {name: digest(Path(binding[side]) / name) for name in
            ("main.bf", "README.html", "docs/usage.html", "LICENSE")} for side in ("original", "protected")}
        atomic_json(binding["report"], report, replace=True)


if __name__ == "__main__":
    try:
        main()
    except HostError as error:
        sys.stderr.write(json.dumps(error.record()))
        raise SystemExit(1)
