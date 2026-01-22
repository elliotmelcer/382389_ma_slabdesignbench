"""
Author: Max Dombrowski
"""

# src/slab_benchmark/core/import_specs.py
from __future__ import annotations
from pathlib import Path
from pprint import pprint
from typing import Dict, List, Any
from .io_util import _read_rows, _to_bool, _to_float, _enf


#----------------------------------------------------------------------------------------------------------#
# Method to turn .csv-file parameter_defaults into python-readable Dict
#----------------------------------------------------------------------------------------------------------#
def load_param_defaults(path: str | Path) -> Dict[str, dict]:
    """
    Read parameter_defaults.csv and return:
      { name: {domain, values, lb, ub, fixed_idx, role, value_type} }

    Required columns:
      name;domain;values;grid_start;grid_step;grid_count;
      default_lb;default_ub;default_fixed;role;value_type

    - domain: 'catalog' uses 'values' as a |-separated list (for numeric types).
              'grid' uses start/step/count to generate values.
    - role: 'var' or 'fixed' (per default; problem_list.csv can override per problem)
    - lb/ub/fixed_idx are 0-based indices into 'values'.
    - value_type: 'float', 'int' oder 'str' (default: 'float', falls leer).
    """
    path = Path(path)
    spec: Dict[str, dict] = {}

    expected = [
        "name", "domain", "values",
        "grid_start", "grid_step", "grid_count",
        "default_lb", "default_ub", "default_fixed",
        "role", "value_type",
    ]

    for r in _read_rows(path, expected):
        name = r["name"]
        dom = (r["domain"] or "").lower()
        role = (r["role"] or "var").lower()
        if role not in ("var", "fixed"):
            raise ValueError(
                f"{path}: parameter '{name}' has invalid role '{role}' (use 'var' or 'fixed')."
            )

        value_type = (r.get("value_type") or "float").strip().lower()

        if dom == "catalog":
            vals_str = (r["values"] or "").strip('"').strip()
            if not vals_str:
                raise ValueError(
                    f"{path}: parameter '{name}' uses domain 'catalog' but has empty 'values'."
                )

            if value_type == "str":
                # ganze Zelle als EIN Wert (z.B. "150,157,181,...")
                vals = [vals_str]

            elif value_type == "int":
                try:
                    vals = [int(v) for v in vals_str.split("|")]
                except ValueError as e:
                    raise ValueError(
                        f"{path}: parameter '{name}' has non-integer catalog value."
                    ) from e

            elif value_type == "float":
                try:
                    vals = [float(v) for v in vals_str.split("|")]
                except ValueError as e:
                    raise ValueError(
                        f"{path}: parameter '{name}' has non-numeric catalog value."
                    ) from e

            else:
                raise ValueError(
                    f"{path}: parameter '{name}' has unknown value_type "
                    f"'{value_type}' (use 'float', 'int' or 'str')."
                )

        elif dom == "grid":
            try:
                start = float(r["grid_start"])
                step = float(r["grid_step"])
                count = int(r["grid_count"])
            except ValueError as e:
                raise ValueError(
                    f"{path}: parameter '{name}' has invalid grid_start/step/count."
                ) from e
            if count <= 0:
                raise ValueError(
                    f"{path}: parameter '{name}' has non-positive grid_count={count}."
                )
            vals = [start + i * step for i in range(count)]

        else:
            raise ValueError(
                f"{path}: parameter '{name}' has unknown domain '{dom}' "
                f"(use 'catalog' or 'grid')."
            )

        L = len(vals)
        if L == 0:
            raise ValueError(
                f"{path}: parameter '{name}' produced an empty value list."
            )

        def clamp_idx(s: str, dflt: int) -> int:
            # empty cell -> default; otherwise clamp to [0, L-1]
            return dflt if s == "" else max(0, min(int(float(s)), L - 1))

        lb = clamp_idx(r["default_lb"], 0)
        ub = clamp_idx(r["default_ub"], L - 1)
        if lb > ub:
            lb, ub = ub, lb

        fixed = clamp_idx(r["default_fixed"], lb)

        spec[name] = {
            "domain": dom,
            "values": vals,
            "lb": lb,
            "ub": ub,
            "fixed_idx": fixed,
            "role": role,
            "value_type": value_type,
        }

    return spec


#----------------------------------------------------------------------------------------------------------#
# Build optimization space from parameter model
#----------------------------------------------------------------------------------------------------------#
def build_space(model: Dict[str, dict]) -> tuple[list[str], list[int], list[int]]:
    """
    From a full parameter model (with roles), extract the optimization space:
    returns (var_names, lb_idx_list, ub_idx_list)
    """
    var_names, lb, ub = [], [], []
    for n, m in model.items():
        if m["role"] == "var":
            var_names.append(n)
            lb.append(m["lb"])
            ub.append(m["ub"])
    return var_names, lb, ub


def make_decode(model: Dict[str, dict], var_names: List[str]):
    """
    Build a decoder: decode(x_idx) -> dict of parameters,
    merging fixed parameters with variable indices (clamped to lb/ub).
    No aliases/synonyms. Parameter names must match the CSVs exactly.
    """
    n_vars = len(var_names)

    def decode(x_idx: List[int]) -> Dict[str, Any]:
        if len(x_idx) != n_vars:
            raise ValueError(
                f"decode: got {len(x_idx)} indices, expected {n_vars} ({var_names})."
            )

        full: Dict[str, Any] = {}

        # 1) fixed parameters
        for name, m in model.items():
            if m["role"] == "fixed":
                full[name] = m["values"][m["fixed_idx"]]

        # 2) variable parameters
        for name, k in zip(var_names, x_idx):
            m = model[name]
            kk = max(m["lb"], min(int(k), m["ub"]))
            full[name] = m["values"][kk]

        return full

    return decode


#----------------------------------------------------------------------------------------------------------#
# Method to turn .csv-file constraint_defaults into python-readable Dict
#----------------------------------------------------------------------------------------------------------#
def load_constraint_defaults(path: str | Path) -> Dict[str, dict]:
    """
    Read constraints_default.csv and return:
      { name: {kind, enforced, weight, exponent, active_default} }
    """
    path = Path(path)
    spec: Dict[str, dict] = {}
    expected = ["name", "kind", "enforced", "weight", "exponent", "active_default"]

    for r in _read_rows(path, expected):
        spec[r["name"]] = {
            "kind": (r["kind"] or "").lower(),
            "enforced": _enf(r["enforced"] or "SOFT"),
            "weight": _to_float(r["weight"], 1.0),
            "exponent": _to_float(r["exponent"], 1.0),
            "active_default": _to_bool(r["active_default"], True),
        }
    return spec


def load_problems_combined(
    param_defaults: Dict[str, dict],
    constr_defaults: Dict[str, dict],
    problem_list_csv: str | Path,
) -> Dict[str, dict]:
    """
    Read problem_list.csv and overlay per-problem configuration onto defaults.
    Returns:
      {
        problem_id: {
          "model": merged parameter model (roles + lb/ub/fixed_idx adjusted),
          "constraints": { name: {kind, enforced, weight, exponent, active} },
          "label": str,
        },
        ...
      }
    """
    problem_list_csv = Path(problem_list_csv)
    expected = [
        "problem_id", "type", "name", "role",
        "lb_idx", "ub_idx", "fixed_idx",
        "active", "enforced", "weight", "exponent",
        "label",
    ]
    rows = list(_read_rows(problem_list_csv, expected))

    by_problem: Dict[str, dict] = {}
    # initialisiere pro Problem eine Kopie der Parameterdefaults
    for r in rows:
        problem_ID = r["problem_id"]
        by_problem.setdefault(
            problem_ID,
            {
                "model": {k: v.copy() for k, v in param_defaults.items()},
                "constraints": {},
                "label": r["label"],
            },
        )

    for r in rows:
        problem_ID, typ, name = (
            r["problem_id"],
            (r["type"] or "").lower(),
            r["name"],
        )
        info = by_problem[problem_ID]

        if typ == "param":
            if name not in info["model"]:
                raise KeyError(
                    f"{problem_list_csv}: problem {problem_ID} refers to unknown parameter '{name}'."
                )
            m = info["model"][name]
            role = (r["role"] or m["role"]).lower()
            if role not in ("var", "fixed"):
                raise ValueError(
                    f"{problem_list_csv}: problem {problem_ID}, param '{name}' has invalid role '{role}'."
                )
            m["role"] = role

            L = len(m["values"])
            clamp = lambda s, d: d if s == "" else max(0, min(int(float(s)), L - 1))
            if role == "var":
                m["lb"] = clamp(r["lb_idx"], m["lb"])
                m["ub"] = clamp(r["ub_idx"], m["ub"])
                if m["lb"] > m["ub"]:
                    m["lb"], m["ub"] = m["ub"], m["lb"]
            else:
                m["fixed_idx"] = clamp(r["fixed_idx"], m["fixed_idx"])

        elif typ == "constraint":
            if name not in constr_defaults:
                raise KeyError(
                    f"{problem_list_csv}: problem {problem_ID} refers to unknown constraint '{name}'."
                )
            base = constr_defaults[name].copy()
            base["active"] = _to_bool(r["active"], base["active_default"])
            if r["enforced"]:
                prev = base["enforced"].name if hasattr(base["enforced"], "name") else "SOFT"
                base["enforced"] = _enf(r["enforced"], prev)
            if r["weight"]:
                base["weight"] = float(r["weight"])
            if r["exponent"]:
                base["exponent"] = float(r["exponent"])
            info["constraints"][name] = base

        if r["label"]:
            info["label"] = r["label"]

    return by_problem


#----------------------------------------------------------------------------------------------------------#
# Example to test if import_specs.py is working correctly
#----------------------------------------------------------------------------------------------------------#
if __name__ == "__main__":
    HERE = Path(__file__).resolve().parent  # .../src/slab_benchmark/core
    PKG_ROOT = HERE.parent                  # .../src/slab_benchmark
    SLABS_DIR = PKG_ROOT / "slabs"          # .../src/slab_benchmark/slabs

    slab_type = "solid_slab_one_way"
    slab_dir = SLABS_DIR / slab_type

    print("SLABS_DIR :", SLABS_DIR)
    print("slab_dir  :", slab_dir)
    print("exists?   :", slab_dir.exists())

    params_csv = slab_dir / "parameter_defaults.csv"
    constr_csv = slab_dir / "constraint_defaults.csv"
    problem_list_csv = slab_dir / "problem_list.csv"

    for p in (params_csv, constr_csv, problem_list_csv):
        print(p, "exists?", p.exists())

    PDEF = load_param_defaults(params_csv)
    CDEF = load_constraint_defaults(constr_csv)
    PROBLEMS = load_problems_combined(PDEF, CDEF, problem_list_csv)
    print("OK: loaded", len(PDEF), "params;", len(CDEF), "constraint;", len(PROBLEMS), "problems")

    print("== Paths ==")
    print(params_csv.resolve())
    print(constr_csv.resolve())
    print(problem_list_csv.resolve())

    print("\n== Loading defaults ==")
    PDEF = load_param_defaults(params_csv)
    CDEF = load_constraint_defaults(constr_csv)
    print(f"Parameters loaded: {len(PDEF)}  |  Constraints loaded: {len(CDEF)}")

    some_params = list(PDEF.items())[:5]
    print("\nSample parameter defaults (first 1–2):")
    for name, spec in some_params:
        print(
            f"- {name}: role={spec['role']}, "
            f"values={spec['values'][:5]}{'...' if len(spec['values'])>5 else ''}, "
            f"lb={spec['lb']}, ub={spec['ub']}, fixed_idx={spec['fixed_idx']}, "
            f"value_type={spec.get('value_type')}"
        )

    some_constr = list(CDEF.items())[:2]
    print("\nSample constraint defaults (first 1–2):")
    for name, spec in some_constr:
        print(
            f"- {name}: kind={spec['kind']}, "
            f"enforced={getattr(spec['enforced'],'name',spec['enforced'])}, "
            f"weight={spec['weight']}, exponent={spec['exponent']}, "
            f"active_default={spec['active_default']}"
        )

    print("\n== Loading problems & overlays ==")
    PROBLEMS = load_problems_combined(PDEF, CDEF, problem_list_csv)
    print(f"Problems found: {len(PROBLEMS)}  -> {sorted(PROBLEMS.keys())}")

    problem_ID = sorted(PROBLEMS.keys())[0]
    info = PROBLEMS[problem_ID]
    print(f"\n== Inspect problem {problem_ID} ({info['label']}) ==")

    var_names, lb_idx, ub_idx = build_space(info["model"])
    print("Variables:", var_names)
    print("lb_idx   :", lb_idx)
    print("ub_idx   :", ub_idx)

    fixed = {n: m for n, m in info["model"].items() if m["role"] == "fixed"}
    if fixed:
        print("\nFixed params in this problem:")
        for n, m in fixed.items():
            print(f"- {n}: fixed_idx={m['fixed_idx']} -> value={m['values'][m['fixed_idx']]}")

    if info["constraints"]:
        print("\nConstraints in this problem:")
        for cname, c in info["constraints"].items():
            enforced = getattr(c["enforced"], "name", c["enforced"])
            print(
                f"- {cname}: active={c['active']}, kind={c['kind']}, "
                f"enforced={enforced}, weight={c['weight']}, exponent={c['exponent']}"
            )
    else:
        print("\nNo constraints configured for this problem.")

    print("\n== Decode test ==")
    decode = make_decode(info["model"], var_names)
    try:
        mid = [(lo + (hi - lo) // 2) for lo, hi in zip(lb_idx, ub_idx)]
        print("x_idx (mid) =", mid)
        params = decode(mid)
        print("decoded params:")
        pprint(params)
    except ValueError as e:
        print("Decode length error:", e)

    print("\n== Negative length check ==")
    try:
        bad = [0] * (len(var_names) + 1)
        decode(bad)
    except ValueError as e:
        print("OK (caught):", e)
