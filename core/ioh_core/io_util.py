"""
Author: Max Dombrowski
"""

import csv
from typing import List
from pathlib import Path
from ioh.iohcpp import ConstraintEnforcement as CE

#----------------------------------------------------------------------------------------------------------#
# methods to read params from the params-dict in a problem object
#----------------------------------------------------------------------------------------------------------#
# Helper to obtain parameters from params and return error if it fails
def _req_param(params: dict, name: str) -> float:
    """Get a numeric parameter or fail loudly with a helpful message."""
    try:
        val = params[name]
    except KeyError as e:
        raise KeyError(f"Required parameter '{name}' missing in params. "
                       f"Got keys: {list(params.keys())}") from e
    try:
        return float(val)
    except (TypeError, ValueError) as e:
        raise ValueError(f"Parameter '{name}' must be numeric, got {val!r}") from e
#----------------------------------------------------------------------------------------------------------#
# .csv-reader + parsers string -> bool, float and ioh-constraint-attribute
#----------------------------------------------------------------------------------------------------------#
# .csv-reader
def _read_rows(path: Path, expected_keys: List[str] | None = None):
    """
    Read ;-delimited CSV, skip blank lines, trim whitespace.
    More forgiving headers:
      - UTF-8 with BOM supported
      - header names matched case/space-insensitively
      - extra columns allowed, but all expected_keys must be present
    Raises:
      - ValueError on empty/missing header
      - ValueError if expected_keys are missing
      - ValueError if no data rows
    """
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f, delimiter=";")
        # error check (1): empty file / missing header
        if reader.fieldnames is None:
            raise ValueError(f"{path}: file is empty or missing a header row.")

        raw_headers = reader.fieldnames
        # Normalize headers for matching (strip + lower)
        norm_headers = [(h or "").strip().lower() for h in raw_headers]
        # Map normalized header -> original header text
        norm_to_raw = {hn: raw_headers[i] for i, hn in enumerate(norm_headers)}

        # header requirement: all expected_keys must be present (allow extras)
        if expected_keys is not None:
            need = [(k or "").strip().lower() for k in expected_keys]
            missing = [k for k in need if k not in norm_to_raw]
            if missing:
                raise ValueError(
                    f"{path}: missing header columns: {missing}. "
                    f"Found headers: {raw_headers}"
                )

        yielded = 0
        for row in reader:
            # Skip fully blank lines
            if not any((v or "").strip() for v in row.values()):        # skips empty lines (included for visual clarity)
                continue

            if expected_keys is not None:
                # Build row using the canonical expected_keys order/names
                clean = {}
                for k in expected_keys:
                    kn = (k or "").strip().lower()
                    rk = norm_to_raw[kn]  # original header name
                    v = row.get(rk, "")
                    clean[k] = v.strip() if v is not None else ""
            else:
                # No schema provided: return normalized-key dict
                clean = {}
                for hn, rk in norm_to_raw.items():
                    v = row.get(rk, "")
                    clean[hn] = v.strip() if v is not None else ""

            yielded += 1
            yield clean

        # (3) no data rows
        if yielded == 0:
            raise ValueError(f"{path}: no data rows found (only header and/or blank lines).")

# parse string -> bool
def _to_bool(s: str, default=False) -> bool:
    return default if s == "" else s.lower() in ("1","true","yes","y")   # if string in s is one of the given, return true

# parse string -> float
def _to_float(s: str, default=None):
    return default if s == "" else float(s)

# parse string -> ioh.iohcpp.ConstraintEnforcement
def _enf(s: str, default="HIDDEN"):
    k = (s or default).upper()
    return {"NOT": CE.NOT, "HIDDEN": CE.HIDDEN, "SOFT": CE.SOFT, "HARD": CE.HARD, "OVERRIDE": CE.OVERRIDE}[k]

# ----------------------------------------------------------------------------------------------------------#
# TEST RUN TO TEST THIS MODULE ONLY - REMOVE BEFORE WRAPPING WHOLE TOOL
# ----------------------------------------------------------------------------------------------------------#

if __name__ == "__main__":
    # Construct Paths relative to this working directory -> has to be moved to builder later
    HERE = Path(__file__).resolve().parent           # .../src/slab-benchmark/core (if io_util.py is in core/)
    PKG_ROOT = HERE.parent                            # .../src/slab-benchmark
    SLABS_DIR = PKG_ROOT / "slabs"
    SLAB_DIR = SLABS_DIR / "solid_slab_one_way"       # your slab folder

    PARAM_CSV  = SLAB_DIR / "parameter_defaults.csv"
    CONSTR_CSV = SLAB_DIR / "constraint_defaults.csv"
    RUNS_CSV   = SLAB_DIR / "runs.csv"

    print("PARAM_CSV :", PARAM_CSV)
    print("CONSTR_CSV:", CONSTR_CSV)
    print("RUNS_CSV  :", RUNS_CSV)

    # Load and peek at a few rows from each file
    for label, p in [("PARAM", PARAM_CSV), ("CONSTR", CONSTR_CSV), ("RUNS", RUNS_CSV)]:
        rows = list(_read_rows(p))
        print(f"\n[{label}] rows={len(rows)}")
        for r in rows[:24]:  # show the first up to 24 dicts
            print(r)