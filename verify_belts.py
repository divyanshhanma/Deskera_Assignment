"""Simple validator for belts outputs (helper used in manual checks).

This script reads the belts input from stdin and executes the nested belts
implementation, printing its output. It's intentionally minimal.
"""
import io
import json
import runpy
import sys


def main():
    data = json.load(sys.stdin)
    sys.stdin = io.StringIO(json.dumps(data))
    nested = r"c:\\part2_assignment\\part2_assignment\\belts\\main.py"
    runpy.run_path(nested, run_name="__main__")


if __name__ == "__main__":
    main()
