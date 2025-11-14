"""Small test-case generator for belts inputs.

Prints a JSON problem instance to stdout that can be piped to the belts CLI.
"""
import json


def make_sample():
    return {
        "nodes": [
            {"id": "s1", "type": "source", "supply": 900},
            {"id": "s2", "type": "source", "supply": 600},
            {"id": "a", "type": "normal"},
            {"id": "b", "type": "normal"},
            {"id": "c", "type": "normal"},
            {"id": "sink", "type": "sink"}
        ],
        "edges": [
            {"from": "s1", "to": "a", "lo": 0, "hi": 1000},
            {"from": "s2", "to": "a", "lo": 0, "hi": 1000},
            {"from": "a", "to": "b", "lo": 0, "hi": 1000},
            {"from": "a", "to": "c", "lo": 0, "hi": 1000},
            {"from": "b", "to": "sink", "lo": 0, "hi": 1000},
            {"from": "c", "to": "sink", "lo": 0, "hi": 1000}
        ],
        "caps": {}
    }


def main():
    print(json.dumps(make_sample(), indent=2))


if __name__ == "__main__":
    main()
