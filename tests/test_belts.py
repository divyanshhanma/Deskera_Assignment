import json
import subprocess
import pytest

def run_belts(input_data):
    cmd = ["python", "belts/main.py"]
    process = subprocess.run(cmd, input=json.dumps(input_data).encode('utf-8'), capture_output=True, check=True)
    return json.loads(process.stdout)

def test_belts_sample():
    input_data = {
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

    expected_output = {
      "status": "ok",
      "max_flow_per_min": 1500,
      "flows": [
        {"from": "s1", "to": "a", "flow": 900},
        {"from": "a", "to": "b", "flow": 900},
        {"from": "b", "to": "sink", "flow": 900},
        {"from": "s2", "to": "a", "flow": 600},
        {"from": "a", "to": "c", "flow": 600},
        {"from": "c", "to": "sink", "flow": 600}
      ]
    }

    result = run_belts(input_data)

    assert result["status"] == expected_output["status"]
    assert result["max_flow_per_min"] == expected_output["max_flow_per_min"]
    # For flows, we need to compare them in a flexible way as order might not be guaranteed
    result_flows = sorted(result["flows"], key=lambda x: (x["from"], x["to"]))
    expected_flows = sorted(expected_output["flows"], key=lambda x: (x["from"], x["to"]))
    
    assert len(result_flows) == len(expected_flows)
    for res_flow, exp_flow in zip(result_flows, expected_flows):
        assert res_flow["from"] == exp_flow["from"]
        assert res_flow["to"] == exp_flow["to"]
        assert abs(res_flow["flow"] - exp_flow["flow"]) < 1e-6
