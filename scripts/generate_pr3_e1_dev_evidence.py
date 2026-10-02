"""Compatibility entry for closed PR3 evidence; see scripts/legacy/README.md.

This command retains its historical effect. Do not use it for new research runs.
"""

from pathlib import Path
import runpy

if __name__ == "__main__":
    runpy.run_path(str(Path(__file__).parent / "legacy" / "generate_pr3_e1_dev_evidence.py"), run_name="__main__")
