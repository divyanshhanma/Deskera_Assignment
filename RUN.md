# Part 2 — exact run instructions

This file documents how to run the `factory` and `belts` CLIs and the test suite for the cleaned project layout.

Notes about the workspace in this repository:
- The runnable implementations live under `part2_assignment/part2_assignment/` (the inner package).
- For convenience there are small helpers and generators in that same folder: `run_samples.py`, `verify_*.py`, `gen_*.py`.

On Windows use PowerShell (examples below use PowerShell syntax). If you use cmd.exe or Bash, alternate commands are shown.

---

## Prerequisites

- Python 3.8+ (the code uses standard libraries plus PuLP)
- pip
- The project `requirements.txt` (located at `part2_assignment/part2_assignment/requirements.txt`) contains:

  - PuLP==2.7.0
  - pytest==8.0.0

Install dependencies from the inner folder:

```powershell
cd C:\path\to\repo\part2_assignment\part2_assignment
python -m pip install -r requirements.txt
```

---

## Quick samples

Run the bundled sample runner (executes both factory and belts sample inputs):

```powershell
cd C:\path\to\repo\part2_assignment\part2_assignment
python run_samples.py
```

Run a single tool with a JSON file on stdin:

Factory:

```powershell
python factory\main.py < samples\factory_input.json > factory_output.json
```

Belts:

```powershell
python belts\main.py < samples\belts_input.json > belts_output.json
```

Notes:
- `run_samples.py` is a convenience runner that uses in-memory sample inputs and ignores extra CLI arguments.
- `gen_factory.py` and `gen_belts.py` print example JSON to stdout — useful to pipe directly into the CLIs.

---

## Running the test suite (PowerShell)

The tests expect to be executed from the inner `part2_assignment` folder. Set the environment variables and run `pytest` as follows.

One-liner (PowerShell):

```powershell
cd C:\path\to\repo\part2_assignment\part2_assignment; $env:FACTORY_CMD='python factory/main.py'; $env:BELTS_CMD='python belts/main.py'; pytest -q
```

Step-by-step (PowerShell):

```powershell
cd C:\path\to\repo\part2_assignment\part2_assignment
$env:FACTORY_CMD = 'python factory/main.py'
$env:BELTS_CMD   = 'python belts/main.py'
pytest -q
```

If you prefer cmd.exe use `set` and `&&`:

```cmd
cd C:\path\to\repo\part2_assignment\part2_assignment
set "FACTORY_CMD=python factory/main.py" && set "BELTS_CMD=python belts/main.py" && pytest -q
```

If you prefer Bash (WSL / Git-Bash) use:

```bash
FACTORY_CMD="python factory/main.py" BELTS_CMD="python belts/main.py" pytest -q
```

---

## Notes about paths and wrappers

- There are small top-level wrapper files at the repository root (`factory\main.py`, `belts\main.py`) that import the nested implementations. The tests run the relative commands (`python factory/main.py`) from the inner `part2_assignment` folder and will find the wrappers correctly when run from that folder.
- If you prefer a single-level layout (no wrappers), you can remove the root wrappers and move the nested `factory` and `belts` folders up; update the tests or the `FACTORY_CMD`/`BELTS_CMD` env vars accordingly.

---

## Troubleshooting

- If a solver (PuLP/CBC) error occurs, ensure PuLP is installed and that CBC is available (PuLP will use its bundled CBC by default on many platforms).
- Tests may be sensitive to numeric tolerances; outputs are rounded to 9 decimal places in the CLIs.

---

## Example quick checks

Run a single factory sample and print JSON to console:

```powershell
cd C:\path\to\repo\part2_assignment\part2_assignment
python gen_factory.py | python factory\main.py
```

Run belts sample generator and pipe to the belts CLI:

```powershell
python gen_belts.py | python belts\main.py
```

---

If you'd like, I can replace the existing `RUN.md` with this final version (or delete the root-level wrappers to make the tree strictly single-folder). Tell me which and I'll apply the change and re-run the tests.
