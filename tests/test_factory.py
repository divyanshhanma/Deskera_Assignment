import json
import subprocess
import pytest

def run_factory(input_data):
    cmd = ["python", "factory/main.py"]
    process = subprocess.run(cmd, input=json.dumps(input_data).encode('utf-8'), capture_output=True, check=True)
    return json.loads(process.stdout)

def test_factory_sample():
    input_data = {
      "machines": {
        "assembler_1": {"crafts_per_min": 30},
        "chemical": {"crafts_per_min": 60}
      },
      "recipes": {
        "iron_plate": {
          "machine": "chemical",
          "time_s": 3.2,
          "in": {"iron_ore": 1},
          "out": {"iron_plate": 1}
        },
        "copper_plate": {
          "machine": "chemical",
          "time_s": 3.2,
          "in": {"copper_ore": 1},
          "out": {"copper_plate": 1}
        },
        "green_circuit": {
          "machine": "assembler_1",
          "time_s": 0.5,
          "in": {"iron_plate": 1, "copper_plate": 3},
          "out": {"green_circuit": 1}
        }
      },
      "modules": {
        "assembler_1": {"prod": 0.1, "speed": 0.15},
        "chemical": {"prod": 0.2, "speed": 0.1}
      },
      "limits": {
        "raw_supply_per_min": {"iron_ore": 5000, "copper_ore": 5000},
        "max_machines": {"assembler_1": 300, "chemical": 300}
      },
      "target": {"item": "green_circuit", "rate_per_min": 1800}
    }

    expected_output = {
      "status": "ok",
      "per_recipe_crafts_per_min": {
        "iron_plate": 1800.0,
        "copper_plate": 5400.0,
        "green_circuit": 1800.0
      },
      "per_machine_counts": {
        "chemical": 50.0,
        "assembler_1": 60.0
      },
      "raw_consumption_per_min": {
        "iron_ore": 1800.0,
        "copper_ore": 5400.0
      }
    }

    result = run_factory(input_data)

    assert result["status"] == expected_output["status"]
    for key, value in expected_output["per_recipe_crafts_per_min"].items():
        assert abs(result["per_recipe_crafts_per_min"][key] - value) < 1e-6
    for key, value in expected_output["per_machine_counts"].items():
        assert abs(result["per_machine_counts"][key] - value) < 1e-6
    for key, value in expected_output["raw_consumption_per_min"].items():
        assert abs(result["raw_consumption_per_min"][key] - value) < 1e-6
