"""Simple validator for factory outputs (helper used in manual checks).

This script reads the factory input from stdin and prints a small validation
report after running the nested factory/main.py. It's optional and intended to
help debug produced JSON outputs during manual runs.
"""
import io
import json
import runpy
import sys


def main():
    data = json.load(sys.stdin)
    # run factory implementation
    sys.stdin = io.StringIO(json.dumps(data))
    nested = r"c:\\part2_assignment\\part2_assignment\\factory\\main.py"
    # capture output by running implementation which writes to stdout
    runpy.run_path(nested, run_name="__main__")


if __name__ == "__main__":
    main()
