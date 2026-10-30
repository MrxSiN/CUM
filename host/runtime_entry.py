"""Generic isolated launcher; install at the root of an approved runtime bundle."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
from host.bytehost.__main__ import main

if __name__ == "__main__":
    main()
