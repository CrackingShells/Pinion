#!/usr/bin/env python3
"""Test plan and guards for scripts/study_contract.py.

Run from the skill directory, either way:

    uv run --with pytest --with jsonschema pytest evals/ -q
    uv run --with pytest --with jsonschema evals/test_study_contract.py

# What the script must do (guards)

Scope of every guard: the CLI, through its consumer's interface, a subprocess on
`sys.executable` running the script. The consumer is an agent that reads the first
line (`RESULT=...`), the exit code and the messages, so nothing here imports the
script. Expected values are written by hand from the fixtures, never computed by the
script's own helpers. Every problem below is a problem, never a warning, so that
`RESULT=OK` keeps one meaning.

| Behavior | Bug it catches |
|---|---|
| `check` accepts a dataset that conforms to its dictionary (declared missing codes, values on both range bounds, a range whose bounds coincide, `10.0` for an allowed 10, a BOM at the start of the file), with the dictionary by path or inline, a filled evolution log, and prints `RESULT=OK`, exit 0 | a validator that rejects declared missing codes; an exclusive range bound; numeric allowed values compared as text; a BOM read as part of the first header; a dictionary-by-path that is never loaded; a constant `RESULT=OK` |
| `check` reports a missing column, an extra column, a repeated header, a ragged row, a variable declared twice | column comparison done one-way or by position; csv rows indexed past their end |
| `check` reports values that break a type, leave the allowed set or the range, or are not finite (`inf`, `1e999`) | `int` parsing via `float`; an exclusive bound; a set test dropped; infinity accepted as a number |
| `check` reports a missing-looking cell (empty, whitespace, NA) that the variable does not declare, and accepts it where declared | missing tokens accepted everywhere; whitespace-only cells treated as data |
| `check` reports a dataset with no data rows, and an outcome that is entirely missing | a header-only file passing; an all-missing outcome passing |
| `check` reports duplicated ids, and a dataset with no `id` variable, no `outcome` variable, or a `unit` that is not a variable | the duplicate test run on the wrong role or skipped without ids; a roleless dataset passing |
| `check` reports a factor without `allowed_values`, naming the levels found in the file | factor levels left untyped |
| `check` reports a `range` on a non-numeric variable and a range whose min exceeds its max, once each | range ignored on strings; an inverted range applied to every cell |
| `check` reports a numeric variable with no units | units optional by accident; the check applied to string variables |
| `check` reports a simulated dataset without seeds | simulated data that cannot be regenerated |
| `check` reports a contract_version other than the schema's, a dataset file that is absent or empty, a dictionary file that cannot be read, a manifest that is not an object, a repeated dataset id, a manifest breaking the schema (naming the allowed keys, requiring `unit` and the six evolution-log fields), and a manifest still holding the scaffold's TODO | the version read from nowhere; a missing or unreadable file crashing with a traceback; compare pairing the wrong datasets; schema errors swallowed; a scaffold that passes unfilled |
| `check` counts each problem once in `RESULT=PROBLEMS n` | a count of 1 or of lines of output |
| `compare` says SWAPPABLE when the dictionaries, units and versions agree, whatever differs in path, origin, provenance, study, descriptions, evolution log, variable order or the order of allowed values; it never opens a data file | metadata or order treated as shape; data read |
| `compare` says DIFFERS with the exact difference: variable added or removed, changed type, units, range, allowed values, missing codes, role, unit of the dataset, protocol or contract version, dataset added or removed | one field left out of the comparison; the result computed from the first variable only |
| `init` writes a manifest whose dictionary lists the header columns in order, takes the format from the extension, and refuses to overwrite a file | header read from the wrong line or delimiter; a filled-in manifest destroyed by a rerun |
| `init`'s manifest is flagged by `check` until filled, and passes once filled | a scaffold `check` cannot tell from a finished one, or one no valid manifest can be made from |
| `init` drops a byte-order mark from the first variable name | a BOM read as part of the name |
| a bad argument (unknown flag or subcommand, missing or unreadable input, unsupported extension, empty data file) exits 64 with a message | argparse's exit 2; an unreadable file crashing |

# Open questions (probes)

None. Csv rows are read with the standard `csv` module; a manifest's relative paths
resolve against the manifest's directory.

# Trust boundaries and fixtures

The script reads files written by other agents (a manifest and CSVs), so malformed
input is the main case. `fixtures/trial.csv` and `fixtures/manifest.json` hold one
conforming study; its dictionary is the shipped `assets/data-dictionary.example.json`,
so the example is exercised as a consumer uses it. Each guard lays the study out in a
temporary directory and changes exactly one thing.

# Deliberately not tested

- The schema's own wording (jsonschema's messages): a trusted library; guards check
  that a schema error reaches the agent and names the allowed keys.
- Large files and encodings other than UTF-8: the contract does not promise them.
- Single-level factors and unbalanced groups: whether they break a test depends on the
  battery, so `check` does not judge them.
- Running `--help`: argparse's own behavior.

# Done when

Each guard has been seen failing against an injected bug, and the suite passes.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
SKILL_ROOT = HERE.parent
SCRIPT = SKILL_ROOT / "scripts" / "study_contract.py"
EXAMPLE_DICTIONARY = SKILL_ROOT / "assets" / "data-dictionary.example.json"
FIXTURES = HERE / "fixtures"

BASE_CSV = (FIXTURES / "trial.csv").read_text()


def run(*args, cwd):
    """Run the script as an agent would and return the completed process."""
    return subprocess.run(
        [sys.executable, str(SCRIPT), *map(str, args)],
        capture_output=True, text=True, cwd=cwd, timeout=60,
    )


def swap(text, old, new):
    """Replace one occurrence, failing loudly if the fixture changed under us."""
    assert text.count(old) == 1, f"{old!r} must occur exactly once in the fixture"
    return text.replace(old, new)


def variable(dictionary, name):
    return next(v for v in dictionary["variables"] if v["name"] == name)


def lay_out(root, csv=None, edit_dictionary=None, edit_manifest=None):
    """Write the conforming study into `root`, apply the one change, return the manifest path."""
    root.mkdir(parents=True, exist_ok=True)
    (root / "trial.csv").write_text(BASE_CSV if csv is None else csv, encoding="utf-8")
    dictionary = json.loads(EXAMPLE_DICTIONARY.read_text())
    if edit_dictionary:
        edit_dictionary(dictionary)
    (root / "dictionary.json").write_text(json.dumps(dictionary))
    manifest = json.loads((FIXTURES / "manifest.json").read_text())
    if edit_manifest:
        edit_manifest(manifest)
    path = root / "manifest.json"
    path.write_text(json.dumps(manifest))
    return path


FILLED_ENTRY = {
    "date": "2026-04-01", "stage": "after a pilot", "change": "dose capped at 50 mg",
    "reason": "pilot showed doses above 50 mg were unsafe", "agreed_by": "principal investigator",
    "effect_on_claim": "none: the dose range was exploratory",
}


def first_line(proc):
    return proc.stdout.splitlines()[0] if proc.stdout else ""


# --- check: a conforming dataset ---------------------------------------------

def test_check_accepts_a_conforming_dataset_with_the_dictionary_by_path(tmp_path):
    manifest = lay_out(tmp_path)
    proc = run("check", manifest, cwd=tmp_path)
    assert (proc.returncode, first_line(proc)) == (0, "RESULT=OK"), proc.stdout + proc.stderr


def test_check_accepts_a_conforming_dataset_with_the_dictionary_inline(tmp_path):
    def inline(manifest):
        manifest["datasets"][0]["dictionary"] = json.loads(EXAMPLE_DICTIONARY.read_text())

    manifest = lay_out(tmp_path, edit_manifest=inline)
    proc = run("check", manifest, cwd=tmp_path)
    assert (proc.returncode, first_line(proc)) == (0, "RESULT=OK"), proc.stdout + proc.stderr


def test_check_accepts_values_on_both_range_bounds(tmp_path):
    on_the_bounds = swap(swap(BASE_CSV, "34,0,412.5", "18,50,412.5"), "62,NA", "90,NA")
    proc = run("check", lay_out(tmp_path, csv=on_the_bounds), cwd=tmp_path)
    assert first_line(proc) == "RESULT=OK", proc.stdout + proc.stderr


def test_check_matches_numeric_allowed_values_by_number_not_by_spelling(tmp_path):
    def only_zero_or_ten(dictionary):
        variable(dictionary, "dose_mg")["allowed_values"] = [0, 10]

    spelled_differently = swap(BASE_CSV, "29,10,350.2", "29,10.0,350.2")
    proc = run("check", lay_out(tmp_path, csv=spelled_differently, edit_dictionary=only_zero_or_ten), cwd=tmp_path)
    assert first_line(proc) == "RESULT=OK", proc.stdout + proc.stderr


def test_check_reads_a_file_that_starts_with_a_byte_order_mark(tmp_path):
    proc = run("check", lay_out(tmp_path, csv="\ufeff" + BASE_CSV), cwd=tmp_path)
    assert first_line(proc) == "RESULT=OK", proc.stdout + proc.stderr


def test_check_accepts_a_range_whose_bounds_coincide(tmp_path):
    def only_zero(dictionary):
        variable(dictionary, "dose_mg")["range"] = [0, 0]

    all_zero = swap(BASE_CSV, "29,10,350.2", "29,0,350.2")
    proc = run("check", lay_out(tmp_path, csv=all_zero, edit_dictionary=only_zero), cwd=tmp_path)
    assert first_line(proc) == "RESULT=OK", proc.stdout + proc.stderr


def test_check_accepts_a_filled_evolution_log(tmp_path):
    def log_one_change(manifest):
        manifest["evolution_log"] = [FILLED_ENTRY]

    proc = run("check", lay_out(tmp_path, edit_manifest=log_one_change), cwd=tmp_path)
    assert first_line(proc) == "RESULT=OK", proc.stdout + proc.stderr


# --- check: each problem class -----------------------------------------------

NO_GROUP_CSV = (
    "subject_id,age_years,dose_mg,reaction_ms\n"
    "1,34,0,412.5\n2,51,0,398.0\n3,29,10,350.2\n4,62,NA,341.7\n"
)
EXTRA_SITE_CSV = (
    "subject_id,group,age_years,dose_mg,reaction_ms,site\n"
    "1,control,34,0,412.5,A\n2,control,51,0,398.0,A\n3,treated,29,10,350.2,B\n4,treated,62,NA,341.7,B\n"
)

DATA_PROBLEMS = [
    pytest.param(NO_GROUP_CSV, 1,
                 ["variable 'group'", "not in the file", "file has: subject_id, age_years, dose_mg, reaction_ms"],
                 id="missing-column"),
    pytest.param(EXTRA_SITE_CSV, 1,
                 ["column 'site'", "not in the dictionary",
                  "dictionary has: subject_id, group, age_years, dose_mg, reaction_ms"],
                 id="extra-column"),
    pytest.param(swap(BASE_CSV, "dose_mg,reaction_ms", "dose_mg,dose_mg"), 2,
                 ["'dose_mg' appears twice in the header"],
                 id="repeated-header"),
    pytest.param(swap(BASE_CSV, "2,control,51,0,398.0", "2,control,51,0"), 1,
                 ["line 3", "4 cells", "header has 5"],
                 id="ragged-row"),
    pytest.param(swap(BASE_CSV, "29,10,350.2", "29,10,fast"), 1,
                 ["variable 'reaction_ms'", "not of type number", "line 4", "'fast'"],
                 id="type-number-given-text"),
    pytest.param(swap(BASE_CSV, "29,10,350.2", "29.5,10,350.2"), 1,
                 ["variable 'age_years'", "not of type integer", "line 4", "'29.5'"],
                 id="type-integer-given-a-fraction"),
    pytest.param(swap(BASE_CSV, "4,treated", "4,placebo"), 1,
                 ["variable 'group'", "outside the allowed values (control, treated)", "line 5", "'placebo'"],
                 id="out-of-set"),
    pytest.param(swap(BASE_CSV, "29,10,350.2", "29,75,350.2"), 1,
                 ["variable 'dose_mg'", "outside range [0, 50]", "line 4", "75"],
                 id="out-of-range"),
    pytest.param(swap(BASE_CSV, "341.7", "NA"), 1,
                 ["variable 'reaction_ms'", "undeclared missing", "line 5", "'NA'", "missing_codes"],
                 id="undeclared-missing-code"),
    pytest.param(swap(BASE_CSV, "341.7", ""), 1,
                 ["variable 'reaction_ms'", "undeclared missing", "line 5", "''", "missing_codes"],
                 id="undeclared-empty-cell"),
    pytest.param(swap(BASE_CSV, "350.2", "1e999"), 1,
                 ["variable 'reaction_ms'", "not finite", "line 4", "'1e999'"],
                 id="not-finite-overflow"),
    pytest.param(swap(BASE_CSV, "350.2", "inf"), 1,
                 ["variable 'reaction_ms'", "not finite", "line 4", "'inf'"],
                 id="not-finite-infinity"),
    pytest.param(swap(BASE_CSV, "341.7", "  "), 1,
                 ["variable 'reaction_ms'", "undeclared missing", "line 5", "'  '"],
                 id="undeclared-whitespace-cell"),
    pytest.param("subject_id,group,age_years,dose_mg,reaction_ms\n", 1,
                 ["dataset 'trial'", "no data rows"],
                 id="no-data-rows"),
    pytest.param(swap(BASE_CSV, "2,control", "1,control"), 1,
                 ["duplicated id", "subject_id = 1", "lines 2, 3"],
                 id="duplicate-id"),
]


@pytest.mark.parametrize("csv_text, count, fragments", DATA_PROBLEMS)
def test_check_reports_each_data_problem_class(tmp_path, csv_text, count, fragments):
    manifest = lay_out(tmp_path, csv=csv_text)
    proc = run("check", manifest, cwd=tmp_path)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert first_line(proc) == f"RESULT=PROBLEMS {count}", proc.stdout
    for fragment in fragments:
        assert fragment in proc.stdout, f"{fragment!r} not in:\n{proc.stdout}"


# --- check: the dictionary and the manifest ----------------------------------

def _drop_units(dictionary):
    del variable(dictionary, "dose_mg")["units"]


def _declare_twice(dictionary):
    dictionary["variables"].append(dict(variable(dictionary, "group")))


def _misspell_units(dictionary):
    dose = variable(dictionary, "dose_mg")
    dose["unit"] = dose.pop("units")


def _wrong_contract_version(manifest):
    manifest["contract_version"] = 2


def _point_at_absent_file(manifest):
    manifest["datasets"][0]["path"] = "nope.csv"


def _point_at_absent_dictionary(manifest):
    manifest["datasets"][0]["dictionary"] = "absent-dictionary.json"


def _reaction_may_be_missing(dictionary):
    variable(dictionary, "reaction_ms")["missing_codes"] = ["NA"]


def _group_has_no_allowed_values(dictionary):
    del variable(dictionary, "group")["allowed_values"]


def _no_id_role(dictionary):
    variable(dictionary, "subject_id")["role"] = "covariate"


def _no_outcome_role(dictionary):
    variable(dictionary, "reaction_ms")["role"] = "covariate"


def _unit_is_not_a_variable(manifest):
    manifest["datasets"][0]["unit"] = "participant"


def _unit_is_absent(manifest):
    del manifest["datasets"][0]["unit"]


def _range_on_a_string(dictionary):
    variable(dictionary, "group")["range"] = [0, 1]


def _range_upside_down(dictionary):
    variable(dictionary, "dose_mg")["range"] = [50, 0]


def _simulated_without_seeds(origin):
    def edit(manifest):
        manifest["datasets"][0]["origin"] = origin
    return edit


def _simulated_with_empty_seeds(manifest):
    manifest["datasets"][0]["origin"] = "simulated-effect"
    manifest["datasets"][0]["provenance"]["seeds"] = []


def _log_entry_without(field):
    def edit(manifest):
        manifest["evolution_log"] = [{k: v for k, v in FILLED_ENTRY.items() if k != field}]
    return edit


ALL_OUTCOMES_NA_CSV = (
    "subject_id,group,age_years,dose_mg,reaction_ms\n"
    "1,control,34,0,NA\n2,control,51,0,NA\n3,treated,29,10,NA\n4,treated,62,NA,NA\n"
)
EVOLUTION_FIELDS = ["date", "stage", "change", "reason", "agreed_by", "effect_on_claim"]


def _repeat_the_dataset_id(manifest):
    manifest["datasets"].append(dict(manifest["datasets"][0]))


STRUCTURE_PROBLEMS = [
    pytest.param(dict(edit_dictionary=_drop_units),
                 ["variable 'dose_mg'", "numeric", "no units", "unitless"],
                 id="numeric-without-units"),
    pytest.param(dict(edit_dictionary=_declare_twice),
                 ["variable 'group' is declared twice"],
                 id="variable-declared-twice"),
    pytest.param(dict(edit_dictionary=_misspell_units),
                 ["'unit' was unexpected", "allowed:", "units"],
                 id="schema-error-names-the-allowed-keys"),
    pytest.param(dict(edit_manifest=_wrong_contract_version),
                 ["contract_version 2", "contract version is 1"],
                 id="contract-version-mismatch"),
    pytest.param(dict(edit_manifest=_point_at_absent_file),
                 ["nope.csv", "not found"],
                 id="dataset-file-absent"),
    pytest.param(dict(edit_manifest=_point_at_absent_dictionary),
                 ["absent-dictionary.json", "cannot read"],
                 id="dictionary-file-absent"),
    pytest.param(dict(csv=""),
                 ["trial.csv is empty", "expected a header line with: subject_id"],
                 id="data-file-empty"),
    pytest.param(dict(edit_manifest=_repeat_the_dataset_id),
                 ["dataset id 'trial' is used twice"],
                 id="dataset-id-repeated"),
    pytest.param(dict(csv=ALL_OUTCOMES_NA_CSV, edit_dictionary=_reaction_may_be_missing),
                 ["outcome 'reaction_ms' is entirely missing"],
                 id="outcome-entirely-missing"),
    pytest.param(dict(edit_dictionary=_group_has_no_allowed_values),
                 ["factor 'group' has no allowed_values", "levels found in the file: control, treated"],
                 id="factor-without-allowed-values"),
    pytest.param(dict(edit_dictionary=_no_id_role),
                 ["no variable has role id", "jointly key"],
                 id="no-id-variable"),
    pytest.param(dict(edit_dictionary=_no_outcome_role),
                 ["no variable has role outcome"],
                 id="no-outcome-variable"),
    pytest.param(dict(edit_manifest=_unit_is_not_a_variable),
                 ["unit 'participant' is not a variable in the dictionary",
                  "dictionary has: subject_id, group, age_years, dose_mg, reaction_ms"],
                 id="unit-not-a-variable"),
    pytest.param(dict(edit_manifest=_unit_is_absent),
                 ["'unit' is a required property"],
                 id="unit-absent"),
    pytest.param(dict(edit_dictionary=_range_on_a_string),
                 ["variable 'group'", "string", "range"],
                 id="range-on-a-string"),
    pytest.param(dict(edit_dictionary=_range_upside_down),
                 ["variable 'dose_mg'", "range [50, 0]", "min"],
                 id="range-min-above-max"),
    pytest.param(dict(edit_manifest=_simulated_without_seeds("simulated-null")),
                 ["simulated-null", "provenance.seeds"],
                 id="simulated-null-without-seeds"),
    pytest.param(dict(edit_manifest=_simulated_with_empty_seeds),
                 ["simulated-effect", "provenance.seeds"],
                 id="simulated-effect-with-empty-seeds"),
] + [
    pytest.param(dict(edit_manifest=_log_entry_without(field)),
                 [f"'{field}' is a required property"],
                 id=f"evolution-entry-without-{field}")
    for field in EVOLUTION_FIELDS
]


@pytest.mark.parametrize("changes, fragments", STRUCTURE_PROBLEMS)
def test_check_reports_each_dictionary_and_manifest_problem(tmp_path, changes, fragments):
    proc = run("check", lay_out(tmp_path, **changes), cwd=tmp_path)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert first_line(proc) == "RESULT=PROBLEMS 1", proc.stdout
    for fragment in fragments:
        assert fragment in proc.stdout, f"{fragment!r} not in:\n{proc.stdout}"


def test_check_reports_a_manifest_that_is_not_an_object(tmp_path):
    (tmp_path / "manifest.json").write_text("[]")
    proc = run("check", "manifest.json", cwd=tmp_path)
    assert proc.returncode == 1 and first_line(proc).startswith("RESULT=PROBLEMS"), proc.stdout + proc.stderr
    assert "not of type 'object'" in proc.stdout


# --- compare -----------------------------------------------------------------

def _everything_but_the_shape(manifest):
    manifest["study"] = "reaction-simulation"
    manifest["evolution_log"] = [
        FILLED_ENTRY
    ]
    dataset = manifest["datasets"][0]
    dataset["path"] = "simulated.csv"
    dataset["origin"] = "simulated-null"
    dataset["provenance"] = {
        "instrument": "numpy simulator", "seeds": [1, 2], "code_commit": "abc1234",
        "dates": {"start": "2026-04-02", "end": "2026-04-02"},
    }


def _describe_differently_and_reorder(dictionary):
    for entry in dictionary["variables"]:
        entry["description"] = "rewritten " + entry["description"]
    dictionary["variables"].reverse()
    variable(dictionary, "group")["allowed_values"].reverse()


def test_compare_says_swappable_when_only_the_data_around_the_dictionary_differs(tmp_path):
    a = lay_out(tmp_path / "a")
    b = lay_out(tmp_path / "b", edit_dictionary=_describe_differently_and_reorder,
                edit_manifest=_everything_but_the_shape)
    proc = run("compare", a, b, cwd=tmp_path)
    assert (proc.returncode, first_line(proc)) == (0, "RESULT=SWAPPABLE"), proc.stdout + proc.stderr
    assert not (tmp_path / "b" / "simulated.csv").exists(), "compare must not need the data"


def _drop_group(dictionary):
    dictionary["variables"] = [v for v in dictionary["variables"] if v["name"] != "group"]


def _add_site(dictionary):
    dictionary["variables"].append(
        {"name": "site", "type": "string", "role": "factor", "description": "Recruitment site."}
    )


def _dose_is_integer(dictionary):
    variable(dictionary, "dose_mg")["type"] = "integer"


def _dose_in_grams(dictionary):
    variable(dictionary, "dose_mg")["units"] = "g"


def _dose_range_to_100(dictionary):
    variable(dictionary, "dose_mg")["range"] = [0, 100]


def _third_group(dictionary):
    variable(dictionary, "group")["allowed_values"] = ["control", "treated", "placebo"]


def _extra_missing_code(dictionary):
    variable(dictionary, "dose_mg")["missing_codes"] = ["NA", "-"]


def _age_is_a_factor(dictionary):
    variable(dictionary, "age_years")["role"] = "factor"


def _new_protocol(manifest):
    manifest["protocol_version"] = "2.0"


def _new_contract(manifest):
    manifest["contract_version"] = 2


def _unit_is_group(manifest):
    manifest["datasets"][0]["unit"] = "group"


def _renamed_dataset(manifest):
    manifest["datasets"][0]["id"] = "replication"


DIFFERENCES = [
    pytest.param(dict(edit_dictionary=_drop_group), ["variable 'group' only in A"], id="variable-removed"),
    pytest.param(dict(edit_dictionary=_add_site), ["variable 'site' only in B"], id="variable-added"),
    pytest.param(dict(edit_dictionary=_dose_is_integer),
                 ["variable 'dose_mg'", 'type: "number" in A, "integer" in B'], id="type-changed"),
    pytest.param(dict(edit_dictionary=_dose_in_grams),
                 ["variable 'dose_mg'", 'units: "mg" in A, "g" in B'], id="units-changed"),
    pytest.param(dict(edit_dictionary=_dose_range_to_100),
                 ["variable 'dose_mg'", "range: [0, 50] in A, [0, 100] in B"], id="range-changed"),
    pytest.param(dict(edit_dictionary=_third_group),
                 ["variable 'group'", 'allowed_values: ["control", "treated"] in A, ["control", "treated", "placebo"] in B'],
                 id="allowed-values-changed"),
    pytest.param(dict(edit_dictionary=_extra_missing_code),
                 ["variable 'dose_mg'", 'missing_codes: ["NA"] in A, ["NA", "-"] in B'], id="missing-codes-changed"),
    pytest.param(dict(edit_dictionary=_age_is_a_factor),
                 ["variable 'age_years'", 'role: "covariate" in A, "factor" in B'], id="role-changed"),
    pytest.param(dict(edit_manifest=_unit_is_group),
                 ["dataset 'trial'", 'unit: "subject_id" in A, "group" in B'], id="unit-changed"),
    pytest.param(dict(edit_manifest=_new_protocol),
                 ['protocol_version: "1.0" in A, "2.0" in B'], id="protocol-version-changed"),
    pytest.param(dict(edit_manifest=_new_contract),
                 ["contract_version: 1 in A, 2 in B"], id="contract-version-changed"),
]


@pytest.mark.parametrize("changes, fragments", DIFFERENCES)
def test_compare_says_differs_and_names_the_difference(tmp_path, changes, fragments):
    a = lay_out(tmp_path / "a")
    b = lay_out(tmp_path / "b", **changes)
    proc = run("compare", a, b, cwd=tmp_path)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert first_line(proc) == "RESULT=DIFFERS 1", proc.stdout
    for fragment in fragments:
        assert fragment in proc.stdout, f"{fragment!r} not in:\n{proc.stdout}"


def test_compare_reports_a_dataset_present_on_one_side_only(tmp_path):
    a = lay_out(tmp_path / "a")
    b = lay_out(tmp_path / "b", edit_manifest=_renamed_dataset)
    proc = run("compare", a, b, cwd=tmp_path)
    assert first_line(proc) == "RESULT=DIFFERS 2", proc.stdout
    assert "dataset 'trial' only in A" in proc.stdout
    assert "dataset 'replication' only in B" in proc.stdout


def test_compare_refuses_a_manifest_that_breaks_the_schema(tmp_path):
    a = lay_out(tmp_path / "a")
    b = lay_out(tmp_path / "b", edit_dictionary=_misspell_units)
    proc = run("compare", a, b, cwd=tmp_path)
    assert proc.returncode == 64, proc.stdout + proc.stderr
    assert "run check" in proc.stderr and "'unit' was unexpected" in proc.stderr


# --- init --------------------------------------------------------------------

HEADER = ["subject_id", "group", "age_years", "dose_mg", "reaction_ms"]


def test_init_lists_the_header_columns_in_the_scaffolded_dictionary(tmp_path):
    (tmp_path / "trial.csv").write_text(BASE_CSV)
    proc = run("init", "trial.csv", "--out", "study.json", cwd=tmp_path)
    assert proc.returncode == 0, proc.stdout + proc.stderr
    manifest = json.loads((tmp_path / "study.json").read_text())
    dataset = manifest["datasets"][0]
    assert manifest["contract_version"] == 1
    assert (dataset["path"], dataset["id"]) == ("trial.csv", "trial")
    assert [v["name"] for v in dataset["dictionary"]["variables"]] == HEADER


@pytest.mark.parametrize("file_name, header_line, expected_format, expected_names", [
    pytest.param("a.csv", "x,y\n", "csv", ["x", "y"], id="csv"),
    pytest.param("a.tsv", "x\ty\n", "tsv", ["x", "y"], id="tsv"),
])
def test_init_takes_format_and_delimiter_from_the_extension(
        tmp_path, file_name, header_line, expected_format, expected_names):
    (tmp_path / file_name).write_text(header_line + "1\t2\n")
    run("init", file_name, "--out", "study.json", cwd=tmp_path)
    dataset = json.loads((tmp_path / "study.json").read_text())["datasets"][0]
    assert dataset["format"] == expected_format
    assert [v["name"] for v in dataset["dictionary"]["variables"]] == expected_names


def test_init_does_not_put_a_byte_order_mark_in_the_first_variable_name(tmp_path):
    (tmp_path / "trial.csv").write_text("\ufeff" + BASE_CSV, encoding="utf-8")
    run("init", "trial.csv", "--out", "study.json", cwd=tmp_path)
    dataset = json.loads((tmp_path / "study.json").read_text())["datasets"][0]
    assert dataset["dictionary"]["variables"][0]["name"] == "subject_id"


def test_init_refuses_to_overwrite_an_existing_manifest(tmp_path):
    (tmp_path / "trial.csv").write_text(BASE_CSV)
    (tmp_path / "study.json").write_text("hand-filled work")
    proc = run("init", "trial.csv", "--out", "study.json", cwd=tmp_path)
    assert proc.returncode == 1
    assert "study.json" in proc.stderr
    assert (tmp_path / "study.json").read_text() == "hand-filled work"


def test_check_flags_a_scaffolded_manifest_as_incomplete(tmp_path):
    (tmp_path / "trial.csv").write_text(BASE_CSV)
    run("init", "trial.csv", "--out", "study.json", cwd=tmp_path)
    proc = run("check", "study.json", cwd=tmp_path)
    assert proc.returncode == 1, proc.stdout + proc.stderr
    assert first_line(proc).startswith("RESULT=PROBLEMS")
    for fragment in ["incomplete", "TODO", "study", "datasets/0/origin", "datasets/0/unit",
                     "datasets/0/dictionary/variables/0/role"]:
        assert fragment in proc.stdout, f"{fragment!r} not in:\n{proc.stdout}"


def test_a_scaffolded_manifest_can_be_filled_into_one_that_check_accepts(tmp_path):
    (tmp_path / "trial.csv").write_text(BASE_CSV)
    run("init", "trial.csv", "--out", "study.json", cwd=tmp_path)
    manifest = json.loads((tmp_path / "study.json").read_text())
    manifest["study"] = "reaction-trial"
    manifest["research_questions"] = ["RQ1"]
    manifest["statistical_questions"] = ["SQ1.1"]
    manifest["protocol_version"] = "1.0"
    dataset = manifest["datasets"][0]
    dataset["origin"] = "pilot"
    dataset["unit"] = "subject_id"
    dataset["provenance"] = {"instrument": "rig", "dates": {"start": "2026-03-02", "end": "2026-03-30"}}
    dataset["dictionary"] = json.loads(EXAMPLE_DICTIONARY.read_text())
    (tmp_path / "study.json").write_text(json.dumps(manifest))
    proc = run("check", "study.json", cwd=tmp_path)
    assert first_line(proc) == "RESULT=OK", proc.stdout + proc.stderr


# --- the CLI contract --------------------------------------------------------

BAD_ARGUMENTS = [
    pytest.param(["--no-such-flag"], id="unknown-flag"),
    pytest.param([], id="no-subcommand"),
    pytest.param(["frobnicate"], id="unknown-subcommand"),
    pytest.param(["check"], id="check-without-manifest"),
    pytest.param(["check", "absent.json"], id="check-absent-manifest"),
    pytest.param(["check", "broken.json"], id="check-manifest-not-json"),
    pytest.param(["compare", "broken.json"], id="compare-with-one-manifest"),
    pytest.param(["init"], id="init-without-data"),
    pytest.param(["init", "absent.csv"], id="init-absent-file"),
    pytest.param(["init", "notes.txt"], id="init-unsupported-extension"),
    pytest.param(["init", "empty.csv"], id="init-empty-file"),
]


@pytest.mark.parametrize("args", BAD_ARGUMENTS)
def test_a_bad_argument_exits_64_with_a_message(tmp_path, args):
    (tmp_path / "broken.json").write_text("{not json")
    (tmp_path / "notes.txt").write_text("a,b\n1,2\n")
    (tmp_path / "empty.csv").write_text("")
    proc = run(*args, cwd=tmp_path)
    assert proc.returncode == 64, proc.stdout + proc.stderr
    assert proc.stderr.strip(), "a bad argument must say what was wrong"
    assert "RESULT=" not in proc.stdout


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
