# Study contract and script

**Goal**: Ship the study contract (schema, example dictionary, `study_contract.py`, its guards and `science-data.md`) so any agent can tell whether a dataset can be swapped under an existing battery and whether two studies are comparable, and nothing more.
**Pre-conditions**:
- [ ] Working in a worktree on `task/designing-tests-study_contract`, cut from `claude/test-design-skill-03d1cc`; every command below runs from the worktree root
- [ ] R01 §1c, §4 (false safety, writing), §5 step 8 and §7 read in full, with the appendix's "Code" and "Templates and code" comments
- [ ] `uv --version` works; Python packages come only from `uv run --with …` or the PEP 723 header, with the shared uv cache (no project venv)
**Success Gates**:
- ⬜ `uv run --with pytest --with jsonschema pytest skills/designing-tests/evals/ -q` passes
- ⬜ Each guard was seen failing against a named, injected bug, recorded in the `study_contract` row of the campaign Progress table's Notes by the coordinator from the implementer's report
- ⬜ Every feature of the script traces to one of the three problems of R01 §7 (swap a dataset under a battery, compare two studies, scaffold a manifest from data headers); anything else is cut
- ⬜ Output is one `RESULT=OK|PROBLEMS n` (check) or `RESULT=SWAPPABLE|DIFFERS n` (compare) line, then details; exit codes 0, 1, and 64 on a bad argument
- ⬜ The standalone and banned-word grep over `skills/designing-tests` prints nothing
**References**: [R01 §7](../../__reports__/designing_tests/00-architecture_designing_tests_v0.md) — the problem, the files, the interface; [evals precedent](../../skills/spawning-agent-plugins/evals/test_regeneration.py) — how a skill's maintainer guard is laid out and run

## Step 1: Schema and example dictionary
**Goal**: Fix the shape of a study manifest and of a data dictionary.
**Implementation Logic**:
`assets/study-contract.schema.json` (JSON Schema 2020-12) for a study manifest: `contract_version`; the study; research and statistical question ids; protocol version; datasets, each with path, format (CSV or TSV), origin (`simulated-null`, `simulated-effect`, `pilot`, `real`), data dictionary (inline or by path) and provenance (code commit, seeds, instrument, dates); the evolution log. The dictionary's shape lives in the schema's `$defs`. `contract_version` is carried in the schema's `$id` (for example `…/study-contract/1`), so a breaking schema change is a breaking skill release.
`assets/data-dictionary.example.json`: a filled, realistic dictionary, each variable with name, type, units or an explicit `unitless`, allowed values or range, missing codes, role (id, factor, outcome, covariate) and description. It must validate against the schema's dictionary definition.
**Deliverables**: `skills/designing-tests/assets/study-contract.schema.json` (`$id` with the contract version, `$defs.dictionary`, `$defs.dataset`, `$defs.provenance`); `skills/designing-tests/assets/data-dictionary.example.json`
**Consistency Checks**: `uv run --with jsonschema python -c "import json,jsonschema; d='skills/designing-tests/assets/'; s=json.load(open(d+'study-contract.schema.json')); jsonschema.Draft202012Validator.check_schema(s); jsonschema.validate(json.load(open(d+'data-dictionary.example.json')), {'\$ref':'#/\$defs/dictionary', '\$defs':s['\$defs']})"` (expected: PASS)
**Commit**: `feat(designing-tests): define the study contract schema and an example dictionary`

## Step 2: Test plan and failing guards
**Goal**: Apply the skill's own method to its code before the code exists.
**Implementation Logic**:
Write the script's test plan as the module docstring of `evals/test_study_contract.py`, in the categories of R01 §6 (software test plan): the guards, each with the expected behavior, its scope (the CLI, through its consumer's interface: a subprocess call on `sys.executable` running the script) and the plausible bug it catches; what is deliberately not tested and why; done-criteria. Then the guards themselves, only guards (no confirms survive in this file), each one behavior: `check` accepts a conforming dataset and reports each problem class of R01 §7 (missing or extra columns, type violations, out-of-set or out-of-range values, undeclared missing codes, duplicate ids, numeric columns without units, contract-version mismatch) with a verbose message naming what was expected and what is available; `compare` says SWAPPABLE for two datasets with the same dictionary and DIFFERS with the exact difference otherwise (variables added or removed, type, unit or range changes, protocol or contract version); `init` scaffolds a manifest and dictionary from CSV headers that `check` then flags as incomplete until filled; a bad argument exits 64. Use parameterization where cases differ only by input (the problem classes), and the distinct-failure rule everywhere else. Small fixtures go in `evals/fixtures/`. Runnable both with `uv run --with pytest --with jsonschema pytest` and directly, like the precedent.
**Deliverables**: `skills/designing-tests/evals/test_study_contract.py` (docstring test plan; guards for `check`, `compare`, `init` and the CLI contract); `skills/designing-tests/evals/fixtures/` (minimal CSVs and manifests)
**Consistency Checks**: `uv run --with pytest --with jsonschema pytest skills/designing-tests/evals/ -q` (expected: FAIL)
**Commit**: `test(designing-tests): guard the study contract before writing it`

## Step 3: The script
**Goal**: Make the guards pass with the least code that solves the three problems.
**Implementation Logic**:
`scripts/study_contract.py`: PEP 723 header declaring `jsonschema` (and `requires-python >=3.9`), run as `uv run scripts/study_contract.py <subcommand>`, stdlib otherwise; subcommands `init`, `check`, `compare` only. It reads the schema from `../assets/` relative to its own file. It solves problems rather than deferring them: explicit errors that list what was expected and what is available, no unexplained constants. It chooses no test and runs no analysis.
Then the mutation check: for each guard, inject one plausible bug (invert a comparison, drop a problem class, return a constant), see that guard go red, revert. Report each guard with the bug that turned it red; a guard nothing turns red is rewritten or cut.
**Deliverables**: `skills/designing-tests/scripts/study_contract.py` (functions `cmd_init`, `cmd_check`, `cmd_compare`, `main`; exit codes 0, 1, 64)
**Consistency Checks**: `uv run --with pytest --with jsonschema pytest skills/designing-tests/evals/ -q` (expected: PASS)
**Consistency Checks**: `uv run skills/designing-tests/scripts/study_contract.py --no-such-flag; test $? -eq 64` (expected: PASS)
**Commit**: `feat(designing-tests): add study_contract.py to check and compare study data`

## Step 4: The data reference
**Goal**: Tell an agent when and how to use the contract, and why it exists.
**Implementation Logic**:
`references/science-data.md`: the problem (batteries outlive datasets; swapping and comparing need a checkable shape); the manifest and the dictionary, field by field with the reason for each; provenance; the evolution log; the validate → fix → repeat loop with the exact commands, run from the skill directory, and how to read `RESULT=` lines and exit codes; what the script does not do (choose tests, analyse data). Low freedom for the commands, high freedom for everything around them.
**Deliverables**: `skills/designing-tests/references/science-data.md` (sections: why a contract, the manifest, the data dictionary, provenance, the evolution log, checking and comparing)
**Consistency Checks**: `p=skills/designing-tests/references/science-data.md; test -f $p && grep -q 'study_contract.py check' $p && grep -q 'study_contract.py compare' $p && { [ "$(wc -l < $p)" -le 100 ] || grep -q '^## Contents' $p; }` (expected: PASS)
**Consistency Checks**: `! grep -riE 'writing-reports|managing-roadmaps|writing-history|writing-release|plumage|playbook|skill-creator|dataviz|waiting-on-processes|spawning-agent-plugins|invariant|deviation' skills/designing-tests` (expected: PASS)
**Commit**: `feat(designing-tests): document the study contract for agents`
