#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["jsonschema"]
# ///
"""Check that data fit a study contract, and that two studies are comparable.

Run it, do not read it:

    uv run <skill-dir>/scripts/study_contract.py init <data.csv|data.tsv ...> [--out study-manifest.json]
    uv run <skill-dir>/scripts/study_contract.py check <manifest.json>
    uv run <skill-dir>/scripts/study_contract.py compare <a.json> <b.json>

where <skill-dir> is the skill's base directory.

It serves three problems and nothing else: swapping a dataset under an existing battery
(`check`), telling whether two studies' contracts are comparable (`compare`, which never
opens data), and starting a manifest
from a data file's header (`init`). It chooses no test and runs no analysis.

Output: `check` prints `RESULT=OK` or `RESULT=PROBLEMS n`; `compare` prints
`RESULT=SWAPPABLE` or `RESULT=DIFFERS n`; details follow, one per line. Exit 0 for OK or
SWAPPABLE, 1 for PROBLEMS or DIFFERS (and for `init` refusing to overwrite), 64 for a bad
argument. Nothing is fetched over the network; the schema is read from ../assets/.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

import jsonschema

EXIT_OK, EXIT_FAILED, EXIT_USAGE = 0, 1, 64

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "assets" / "study-contract.schema.json"

# The word `init` writes wherever a human or agent must still decide something.
PLACEHOLDER = "TODO"

# Cell contents that conventionally mean "no value". A variable must declare which of
# them it uses in `missing_codes`; any other occurrence is reported rather than guessed
# at. A sentinel such as -999 is not listed: it is caught only through a declared range.
COMMON_MISSING_TOKENS = {"", "NA", "N/A", "NaN", "nan", "null", "NULL", "None", "."}

# Problems of one kind in one variable are reported once, with this many examples,
# so that a column of 10 000 bad cells does not bury the other problems.
MAX_EXAMPLES = 3

# A factor with no allowed_values is reported with the levels found in the file, so the
# author can copy them; a column with many distinct values is not a factor, so stop here.
LEVELS_SHOWN = 10

# Origins whose data come from a program; they cannot be regenerated without seeds.
SIMULATED_ORIGINS = ("simulated-null", "simulated-effect")

DELIMITERS = {"csv": ",", "tsv": "\t"}
NUMERIC_TYPES = ("integer", "number")
INTEGER_RE = re.compile(r"[+-]?\d+")
NUMBER_RE = re.compile(r"[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?")


class UsageError(Exception):
    """An argument could not be used; the message says what was expected."""


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        print(f"{self.prog}: error: {message}", file=sys.stderr)
        sys.exit(EXIT_USAGE)


# --- loading ------------------------------------------------------------------

def read_json(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except OSError as exc:
        raise UsageError(f"cannot read {path}: {exc.strerror}")
    except ValueError as exc:
        raise UsageError(f"{path} is not valid JSON: {exc}")


def load_schema():
    return read_json(SCHEMA_PATH)


def contract_version(schema):
    """The version is the last segment of the schema's $id, e.g. urn:...:study-contract:1."""
    return int(schema["$id"].rsplit(":", 1)[1])


def schema_problems(instance, schema, label):
    problems = []
    for error in sorted(jsonschema.Draft202012Validator(schema).iter_errors(instance),
                        key=lambda e: [str(p) for p in e.absolute_path]):
        if error.instance == PLACEHOLDER:
            continue  # reported once, as incomplete, by placeholder_problems
        where = "/".join(str(p) for p in error.absolute_path) or "(top level)"
        message = error.message
        if error.validator == "additionalProperties":
            message += f"; allowed: {', '.join(error.schema['properties'])}"
        problems.append(f"{label}: {where}: {message}")
    return problems


def placeholder_problems(node, label, path=()):
    if node == PLACEHOLDER:
        return [f"{label}: incomplete: {'/'.join(map(str, path))} is still {PLACEHOLDER!r}; "
                f"replace it with the real value"]
    children = []
    if isinstance(node, dict):
        children = node.items()
    elif isinstance(node, list):
        children = enumerate(node)
    return [p for key, child in children for p in placeholder_problems(child, label, path + (key,))]


def load_study(manifest_path, schema):
    """Read a manifest and the dictionaries it points to.

    Returns (manifest, {dataset id: dictionary}, problems). Dictionaries are only
    returned when there are no problems; the contract version is left to the caller.
    """
    manifest = read_json(manifest_path)
    label = "manifest"
    problems = placeholder_problems(manifest, label) + schema_problems(manifest, schema, label)
    if problems:
        return manifest, {}, problems
    base = Path(manifest_path).parent
    dictionary_schema = {"$ref": "#/$defs/dictionary", "$defs": schema["$defs"]}
    dictionaries, seen = {}, set()
    for dataset in manifest["datasets"]:
        if dataset["id"] in seen:
            problems.append(f"dataset id {dataset['id']!r} is used twice; ids must be unique")
        seen.add(dataset["id"])
        dictionary = dataset["dictionary"]
        if isinstance(dictionary, str):
            target = base / dictionary
            dlabel = f"dictionary {dictionary}"
            try:
                dictionary = read_json(target)
            except UsageError as exc:
                problems.append(f"dataset {dataset['id']!r}: {exc} (resolved against the manifest's directory)")
                continue
            found = placeholder_problems(dictionary, dlabel) + schema_problems(dictionary, dictionary_schema, dlabel)
            if found:
                problems += found
                continue
        dictionaries[dataset["id"]] = dictionary
    return manifest, dictionaries, problems


# --- check --------------------------------------------------------------------

def parse_cell(cell, type_name):
    """Return (ok, value) for a non-missing cell."""
    if type_name == "string":
        return True, cell
    if type_name == "integer":
        return (True, int(cell)) if INTEGER_RE.fullmatch(cell) else (False, None)
    return (True, float(cell)) if NUMBER_RE.fullmatch(cell) else (False, None)


def is_missing(cell, codes):
    return cell in codes or cell in COMMON_MISSING_TOKENS or not cell.strip()


def is_not_finite(cell):
    if NUMBER_RE.fullmatch(cell):
        return not math.isfinite(float(cell))
    return cell.lower().lstrip("+-") in ("inf", "infinity")


def examples(items):
    shown = ", ".join(f"line {line} {cell!r}" for line, cell in items[:MAX_EXAMPLES])
    return shown + (f" (+{len(items) - MAX_EXAMPLES} more)" if len(items) > MAX_EXAMPLES else "")


def check_dataset(dataset, dictionary, base):
    """Return (problems, number of data rows) for one dataset against its dictionary."""
    label = f"dataset {dataset['id']!r}"
    variables = dictionary["variables"]
    names = [v["name"] for v in variables]
    by_name = {v["name"]: v for v in variables}
    problems = []

    for name in dict.fromkeys(n for n in names if names.count(n) > 1):
        problems.append(f"{label}: variable {name!r} is declared twice in the dictionary")
    if dataset["unit"] not in by_name:
        problems.append(f"{label}: unit {dataset['unit']!r} is not a variable in the dictionary; "
                        f"dictionary has: {', '.join(names)}")
    for role, advice in (("id", "the id variables jointly key the rows and that combination must not repeat "
                                "(for repeated measures: id = subject + time, unit = subject)"),
                         ("outcome", "name the variable(s) the battery tests")):
        if not any(v["role"] == role for v in variables):
            problems.append(f"{label}: no variable has role {role}; {advice}")
    if dataset["origin"] in SIMULATED_ORIGINS and not dataset["provenance"].get("seeds"):
        problems.append(f"{label}: origin {dataset['origin']!r} requires provenance.seeds with at least "
                        f"one seed, or the dataset cannot be regenerated")
    valid_range = {}
    for var in variables:
        if var["type"] in NUMERIC_TYPES and "units" not in var:
            problems.append(f"{label}: variable {var['name']!r} is numeric but declares no units; "
                            f'add "units" with its unit, or "unitless"')
        if "range" in var:
            low, high = var["range"]
            if var["type"] not in NUMERIC_TYPES:
                problems.append(f"{label}: variable {var['name']!r} is a string but declares a range; "
                                f"range applies to integer and number variables (use allowed_values)")
            elif low > high:
                problems.append(f"{label}: variable {var['name']!r} has range {json.dumps(var['range'])}: "
                                f"min is greater than max")
            else:
                valid_range[var["name"]] = (low, high)

    path = base / dataset["path"]
    if not path.is_file():
        return problems + [f"{label}: file {dataset['path']} not found (looked for {path})"], 0
    with open(path, newline="", encoding="utf-8-sig") as fh:
        reader = csv.reader(fh, delimiter=DELIMITERS[dataset["format"]])
        header = next(reader, None)
        if header is None:
            return problems + [f"{label}: file {dataset['path']} is empty; expected a header line "
                               f"with: {', '.join(names)}"], 0
        rows = [(reader.line_num, row) for row in reader if row]
    if not rows:
        problems.append(f"{label}: file {dataset['path']} has a header but no data rows")

    for name in dict.fromkeys(c for c in header if header.count(c) > 1):
        problems.append(f"{label}: column {name!r} appears twice in the header")
    for name in dict.fromkeys(n for n in names if n not in header):
        problems.append(f"{label}: variable {name!r} is in the dictionary but not in the file; "
                        f"file has: {', '.join(header)}")
    for name in dict.fromkeys(c for c in header if c not in by_name):
        problems.append(f"{label}: column {name!r} is in the file but not in the dictionary; "
                        f"dictionary has: {', '.join(names)}")
    ragged = [(line, len(row)) for line, row in rows if len(row) != len(header)]
    if ragged:
        listed = "; ".join(f"line {line} has {n} cells" for line, n in ragged[:MAX_EXAMPLES])
        problems.append(f"{label}: {len(ragged)} row(s) with the wrong number of cells, e.g. {listed}; "
                        f"header has {len(header)}")

    index = {}
    for position, column in enumerate(header):
        index.setdefault(column, position)
    found = defaultdict(list)  # (kind, variable name) -> [(line, cell)]
    for name in dict.fromkeys(n for n in names if n in index):
        var, position = by_name[name], index[name]
        codes = var.get("missing_codes", [])
        if var["type"] in NUMERIC_TYPES:
            allowed = {float(a) for a in var.get("allowed_values", []) if not isinstance(a, str)}
        else:
            allowed = {str(a) for a in var.get("allowed_values", [])}
        for line, row in rows:
            if position >= len(row):
                continue
            cell = row[position]
            if cell in codes:
                continue
            if cell in COMMON_MISSING_TOKENS or not cell.strip():
                found["missing", name].append((line, cell))
                continue
            if var["type"] in NUMERIC_TYPES and is_not_finite(cell):
                found["finite", name].append((line, cell))
                continue
            ok, value = parse_cell(cell, var["type"])
            if not ok:
                found["type", name].append((line, cell))
            elif "allowed_values" in var and value not in allowed:
                found["set", name].append((line, cell))
            elif name in valid_range and not valid_range[name][0] <= value <= valid_range[name][1]:
                found["range", name].append((line, cell))

    for (kind, name), items in found.items():
        var, head = by_name[name], f"{label}: variable {name!r}: {len(items)}"
        if kind == "type":
            problems.append(f"{head} value(s) not of type {var['type']}, e.g. {examples(items)}")
        elif kind == "set":
            problems.append(f"{head} value(s) outside the allowed values ({', '.join(map(str, var['allowed_values']))}), "
                            f"e.g. {examples(items)}")
        elif kind == "finite":
            problems.append(f"{head} value(s) not finite, e.g. {examples(items)}")
        elif kind == "range":
            problems.append(f"{head} value(s) outside range {json.dumps(var['range'])}, e.g. {examples(items)}")
        else:
            declared = ", ".join(map(repr, var.get("missing_codes", []))) or "none"
            problems.append(f"{head} undeclared missing value(s), e.g. {examples(items)}; declare the code "
                            f"in missing_codes (declared for this variable: {declared})")

    for var in variables:
        if var["role"] == "factor" and "allowed_values" not in var:
            levels = list(dict.fromkeys(
                row[index[var["name"]]] for _, row in rows
                if var["name"] in index and index[var["name"]] < len(row)
                and not is_missing(row[index[var["name"]]], var.get("missing_codes", []))))
            shown = ", ".join(levels[:LEVELS_SHOWN]) + (f" (+{len(levels) - LEVELS_SHOWN} more)"
                                                       if len(levels) > LEVELS_SHOWN else "")
            problems.append(f"{label}: factor {var['name']!r} has no allowed_values; levels found in the file: "
                            f"{shown or 'none'}; list the levels the battery may rely on")
        if var["role"] == "outcome" and rows and var["name"] in index:
            position = index[var["name"]]
            if all(position >= len(row) or is_missing(row[position], var.get("missing_codes", []))
                   for _, row in rows):
                problems.append(f"{label}: outcome {var['name']!r} is entirely missing; "
                                f"nothing can be tested on it")

    id_columns = [n for n in dict.fromkeys(names) if by_name[n]["role"] == "id" and n in index]
    if id_columns:
        lines_of = defaultdict(list)
        for line, row in rows:
            if all(index[n] < len(row) for n in id_columns):
                lines_of[tuple(row[index[n]] for n in id_columns)].append(line)
        repeated = {key: lines for key, lines in lines_of.items() if len(lines) > 1}
        if repeated:
            key, lines = next(iter(repeated.items()))
            shown = ", ".join(f"{n} = {c}" for n, c in zip(id_columns, key))
            problems.append(f"{label}: duplicated id: {len(repeated)} value(s) repeated, e.g. {shown} "
                            f"on lines {', '.join(map(str, lines))}")
    return problems, len(rows)


def cmd_check(args):
    schema = load_schema()
    expected = contract_version(schema)
    manifest, dictionaries, problems = load_study(args.manifest, schema)
    claimed = manifest.get("contract_version") if isinstance(manifest, dict) else None
    if claimed != expected:
        problems.insert(0, f"manifest: contract_version {claimed!r} in the manifest, but this skill's "
                           f"contract version is {expected} (schema $id {schema['$id']}); "
                           f"rewrite the manifest for version {expected}")
    details = []
    if not problems:
        base = Path(args.manifest).parent
        for dataset in manifest["datasets"]:
            found, n_rows = check_dataset(dataset, dictionaries[dataset["id"]], base)
            problems += found
            details.append(f"dataset {dataset['id']!r}: {n_rows} row(s) read against "
                           f"{len(dictionaries[dataset['id']]['variables'])} variable(s)")
    if problems:
        print(f"RESULT=PROBLEMS {len(problems)}")
        for problem in problems:
            print(f"- {problem}")
        return EXIT_FAILED
    print("RESULT=OK")
    for detail in details:
        print(f"- {detail}")
    return EXIT_OK


# --- compare ------------------------------------------------------------------

def show(value):
    return json.dumps(value)


def comparable(field, value):
    """Allowed values are a set: the order they are listed in does not change the shape."""
    if field == "allowed_values" and isinstance(value, list):
        return sorted(json.dumps(v) for v in value)
    return value


def cmd_compare(args):
    schema = load_schema()
    studies = []
    for path in (args.a, args.b):
        manifest, dictionaries, problems = load_study(path, schema)
        if problems:
            raise UsageError(f"cannot compare {path}: it breaks the contract; run check on it first "
                             f"and fix it:\n" + "\n".join(f"- {p}" for p in problems))
        studies.append((manifest, dictionaries))
    (a, dicts_a), (b, dicts_b) = studies

    differences = []
    for field in ("contract_version", "protocol_version"):
        if a[field] != b[field]:
            differences.append(f"{field}: {show(a[field])} in A, {show(b[field])} in B")
    for dataset_id in dicts_a:
        if dataset_id not in dicts_b:
            differences.append(f"dataset {dataset_id!r} only in A (B has: {', '.join(map(repr, dicts_b))})")
    for dataset_id in dicts_b:
        if dataset_id not in dicts_a:
            differences.append(f"dataset {dataset_id!r} only in B (A has: {', '.join(map(repr, dicts_a))})")
    for dataset_id in (d for d in dicts_a if d in dicts_b):
        vars_a = {v["name"]: v for v in dicts_a[dataset_id]["variables"]}
        vars_b = {v["name"]: v for v in dicts_b[dataset_id]["variables"]}
        where = f"dataset {dataset_id!r}"
        unit_a = next(d["unit"] for d in a["datasets"] if d["id"] == dataset_id)
        unit_b = next(d["unit"] for d in b["datasets"] if d["id"] == dataset_id)
        if unit_a != unit_b:
            differences.append(f"{where}: unit: {show(unit_a)} in A, {show(unit_b)} in B")
        for name in vars_a.keys() - vars_b.keys():
            differences.append(f"{where}: variable {name!r} only in A (B has: {', '.join(vars_b)})")
        for name in vars_b.keys() - vars_a.keys():
            differences.append(f"{where}: variable {name!r} only in B (A has: {', '.join(vars_a)})")
        for name in (n for n in vars_a if n in vars_b):
            fields = (vars_a[name].keys() | vars_b[name].keys()) - {"name", "description"}
            for field in sorted(fields):
                if comparable(field, vars_a[name].get(field)) != comparable(field, vars_b[name].get(field)):
                    differences.append(f"{where}: variable {name!r} {field}: "
                                       f"{show(vars_a[name].get(field))} in A, {show(vars_b[name].get(field))} in B")
    if differences:
        print(f"RESULT=DIFFERS {len(differences)}")
        for difference in differences:
            print(f"- {difference}")
        return EXIT_FAILED
    print("RESULT=SWAPPABLE")
    return EXIT_OK


# --- init ---------------------------------------------------------------------

def cmd_init(args):
    out = Path(args.out)
    datasets = []
    for name in args.data:
        path = Path(name)
        file_format = path.suffix.lstrip(".").lower()
        if file_format not in DELIMITERS:
            raise UsageError(f"{name}: unsupported extension {path.suffix!r}; expected one of "
                             f"{', '.join('.' + f for f in DELIMITERS)}")
        if not path.is_file():
            raise UsageError(f"{name}: no such file")
        with open(path, newline="", encoding="utf-8-sig") as fh:
            header = next(csv.reader(fh, delimiter=DELIMITERS[file_format]), None)
        if not header:
            raise UsageError(f"{name}: the file is empty; expected a header line with the column names")
        datasets.append({
            "id": path.stem,
            "path": Path(os.path.relpath(path, out.resolve().parent)).as_posix(),
            "format": file_format,
            "origin": PLACEHOLDER,
            "unit": PLACEHOLDER,
            "dictionary": {"variables": [
                {"name": column, "type": PLACEHOLDER, "role": PLACEHOLDER, "description": PLACEHOLDER}
                for column in header]},
            "provenance": {"instrument": PLACEHOLDER, "dates": {"start": PLACEHOLDER, "end": PLACEHOLDER}},
        })
    if out.exists():
        print(f"error: {out} already exists; init never overwrites. Delete it or pass --out with another path.",
              file=sys.stderr)
        return EXIT_FAILED
    manifest = {
        "contract_version": contract_version(load_schema()),
        "study": PLACEHOLDER,
        "research_questions": [PLACEHOLDER],
        "statistical_questions": [PLACEHOLDER],
        "protocol_version": PLACEHOLDER,
        "datasets": datasets,
        "evolution_log": [],
    }
    out.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out} with {len(datasets)} dataset(s); replace every {PLACEHOLDER!r}, add units, "
          f"allowed values, ranges and missing codes, then run: uv run <skill-dir>/scripts/study_contract.py check {out} "
          f"(<skill-dir> is the skill's base directory)")
    return EXIT_OK


# --- entry point --------------------------------------------------------------

def build_parser():
    parser = _Parser(prog="study_contract.py", description=__doc__.split("\n\n")[0])
    sub = parser.add_subparsers(dest="command", required=True, parser_class=_Parser)
    init = sub.add_parser("init", help="scaffold a manifest and dictionaries from data headers")
    init.add_argument("data", nargs="+", help="data files (.csv or .tsv) with a header line")
    init.add_argument("--out", default="study-manifest.json", help="manifest to write (default: %(default)s)")
    init.set_defaults(func=cmd_init)
    check = sub.add_parser("check", help="validate a manifest and its datasets")
    check.add_argument("manifest")
    check.set_defaults(func=cmd_check)
    compare = sub.add_parser("compare", help="say whether two studies are swappable")
    compare.add_argument("a")
    compare.add_argument("b")
    compare.set_defaults(func=cmd_compare)
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    try:
        return args.func(args)
    except UsageError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return EXIT_USAGE


if __name__ == "__main__":
    sys.exit(main())
