"""Generic isolated launcher; install at the root of an approved runtime bundle."""
from pathlib import Path
import runpy
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
if __name__ == "__main__":
    runpy.run_module("host.bytehost", run_name="__main__")
