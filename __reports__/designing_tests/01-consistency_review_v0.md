# designing-tests — Consistency review (v0)

Date: 2026-11-09. Read-only review of the merged skill at `8929463`, against
[R01](00-architecture_designing_tests_v0.md) and its appendix. The verifier changed no file.
It ran the guards (56 passed), `tools/quick_validate.py` (valid, description 1023 characters),
and `check` and `compare` on probe fixtures in the scratchpad.

## Attacks and results

| # | Attack | Result |
|---|---|---|
| A1 | Role definitions against the appendix | Faithful. A guard checks an expected behavior; "invariant" is absent; the lifetime wording for science is present. One softening (F21) |
| A2 | Banned words, other skills' names, authoring-context leaks | The R01 grep prints nothing. One leak of the authoring context (F1). "maintainer" in `evals/` is harmless and not packaged |
| A3 | Wording forced by the ban | "SD" three times in two files, never defined (F5). The cause is the over-broad `deviation` pattern in the check, a coordinator defect. "Departure" is used only for violated conditions and reads naturally |
| A4 | One term per concept | Guard, confirm, probe and battery are consistent. "Data contract" against "study contract" (F2). Four names for the known-truth step, not tied to the roles (F10) |
| A5 | Are 56 guards an explosion? | No. About 22 functions; the parametrized rows are distinct problem classes, each with a distinct bug. Two tests repeat a count another row already asserts (F22) |
| A6 | Tautology attack on the guards | None passes with a plausible wrong implementation: a constant `RESULT=OK` and an always-SWAPPABLE `compare` are both caught. Gaps the guards do not cover are F7 to F9 |
| A7 | Each script feature traced to an R01 §7 problem | All trace. Nothing to cut |
| A8 | Each gate names a reference that explains it | Software step 1 points to the wrong file (F3). All others hold |
| A9 | Count targets, ratios, tiers, quotas | None. Every mention is a negative |
| A10 | Bug advice leading to one test per bug | None. The five-step sequence is present and agrees across files |
| A11 | Catalogs open with the principle and end by asking for the unlisted case | All but the Proportions family of the landscape (F15) |
| A12 | Links, one level deep, contents lists | Every relative link resolves; all 11 references are linked from `SKILL.md`; every reference over 100 lines has `## Contents` |
| A13 | Coordinator's open notes | Leak confirmed (F1); ban over-match confirmed (A3); citations from memory confirmed (F20); 56 guards answered (A5) |
| A14 | Cold reads of `SKILL.md`: "plan CSV export for a CLI", "compare two training methods across seeds" | See below |

**Cold read, CSV export.** The description triggers. Step 1's gate sends the reader to the wrong
file (F3). A planning task stalls at steps 4 to 6, which describe running tests, and the reader
never learns that a plan lists what was deliberately not tested (F16). Gates of mixed polarity
(F17) could be answered the wrong way round.

**Cold read, seeds study.** The description triggers. "SESOI" is undefined at step 1 (F12). The
landscape's ML family covers cross-validation, not seed runs (F19). Step 5 simulates data before
the contract exists at step 8 (F11). Nothing says how far each step scales down for a small study
(F18). The script command fails from the project directory (F4). The closing paragraph omits the
explanation owed to the requester (F14), and the evolution log never appears in the procedure
(F13).

## Findings by owning leaf

Decision legend: **accept** (fixed by the owner), **coordinator** (fixed by the coordinator,
no owning leaf), **reject** (with reason).

| # | Where | Finding | Decision | Owner |
|---|---|---|---|---|
| F1 | `software-planning.md`:28 | "the guards the user's warning is about" leaks the authoring context | coordinator: reworded | software_references |
| F2 | `SKILL.md` description; `science-analysis-plan.md`:46 | "data contract" where every other file says "study contract" | accept | root_skill, science_method |
| F3 | `SKILL.md` software step 1 | Gate points to roles-and-scope; the sources of guards are in `software-planning.md` | accept | root_skill |
| F4 | `SKILL.md`:121; `science-data.md`; `study_contract.py` `init` hint | `uv run scripts/study_contract.py` is relative to the skill directory, but the agent works from the project | accept: show the script by the skill's base directory, run from the project | root_skill, study_contract |
| F5 | `science-protocol-and-sample.md`:109, 166; `science-test-landscape.md`:217 | "SD" never defined | accept: "standard deviation (SD)" at first use. The banned-word check becomes `(?<!standard )deviation` | science_method, test_landscape; coordinator for the check |
| F6 | schema `evolution_entry`; `science-analysis-plan.md`:80-87 | The schema rejects the stage, who agreed and the effect on the claim, which the plan requires | accept: all six fields (date, stage, change, reason, agreed by, effect on the claim) required in the schema and named in `science-data.md` | study_contract |
| F7 | `science-data.md`:87; `cmd_compare` | `compare` never opens data, yet the doc says it refuses a manifest that fails `check` | accept: document `compare` as dictionary-, unit- and protocol-level, run after `check` passes on both sides | study_contract |
| F8 | `check_dataset` | No duplicate check when no variable has role `id` | accept: a dataset with no `id` variable is a problem | study_contract |
| F9 | `check_dataset`; schema `range` | A UTF-8 BOM gives two baffling problems; `range` on a string is ignored; an inverted range is accepted | accept: read with `utf-8-sig`; both range cases are problems. A simulated dataset without seeds is also a problem (the doc already says it cannot be reproduced) | study_contract |
| F10 | `science-protocol-and-sample.md`; `science-analysis-plan.md`:42 | Known-truth check, run, calibration and validation are not tied to confirm and guard | accept: per step while building is a confirm; end to end on the battery is the guard's known-truth run; one term each | science_method |
| F11 | `SKILL.md` steps 5 and 8 | Step 5 simulates in the contract's shape before step 8 introduces the contract | accept: step 5 writes the manifest and runs `check` on the simulated datasets; order kept, since step 8 is where real data arrive | root_skill |
| F12 | `SKILL.md` science step 1 | "SESOI" not expanded | accept | root_skill |
| F13 | `SKILL.md` science procedure | The evolution log never appears in the procedure | accept | root_skill |
| F14 | `SKILL.md` closing paragraph of the science procedure | The explanation owed to the requester is missing from the last thing read | accept | root_skill |
| F15 | `science-test-landscape.md` Proportions | Only family without the closing "which case is not named?" prompt | accept | test_landscape |
| F16 | `SKILL.md` software procedure | Planning-only use is not marked; "what was deliberately not tested" never appears in the root | accept | root_skill |
| F17 | `SKILL.md` gates | Mixed polarity; step 6 bundles two questions | accept: every gate passes on "yes"; step 6 split | root_skill |
| F18 | `SKILL.md` science procedure | No proportionality rule | accept: scale each step to the study; a step trivially met says why in one line, never skipped silently | root_skill |
| F19 | landscape, ML and benchmark comparisons | Seed runs: unit, pairing and what the inference covers are not stated | accept | test_landscape |
| F20 | science references (ten citations) | Author and year only, no venue or DOI; cited from memory | accept: open each, add venue and DOI; mark any that could not be opened | science_method |
| F21 | `science-questions-and-tests.md`:123 | "kept as a unit check of the code" softens the culling of confirms | accept: a kept check is rewritten as a software guard under the software rules | science_method |
| F22 | `evals/test_study_contract.py`:211, 411 | Two count tests repeat what another row asserts | accept: merge into the existing rows | study_contract |
| F23 | `SKILL.md` compatibility | `Draft202012Validator` needs jsonschema 4 or later | accept | root_skill |
| F24 | landscape:34 | Points to a "normality pretest entry" that does not exist | accept | test_landscape |

## Questions for the coordinator, answered

1. **F11, reorder or cross-reference?** Cross-reference. The order follows R01 §5, which the
   references mirror; step 5 now writes the manifest early, so simulated data are checked like
   any other.
2. **F6, full log entry or short index?** Full entry. Two logs with different fields would drift,
   and the stage and the effect on the claim are what make the log an evolution record rather than
   a changelog.
3. **F7, should `compare` check data?** No. `check` answers "does this dataset fit its
   dictionary"; `compare` answers "do these two contracts describe the same shape". Keeping them
   apart keeps each result's meaning narrow. The doc says to run `check` on both sides first.
   Exit 64 stays for a manifest `compare` cannot load.
4. **F8, F9, seeds.** All become problems reported by `check`, not warnings: a second severity
   would make `RESULT=OK` ambiguous.
5. **The banned-word check.** Changed to ban "deviation" only when not preceded by "standard ", in
   the remaining roadmap leaves and the fix briefs.

## Appendix: mutation evidence for the study contract guards

The study_contract implementer injected 58 plausible bugs into `study_contract.py`, one at a
time. Two survived the first pass (an exclusive upper range bound; numeric allowed values compared
as text); a guard was added for each, and both then turned the suite red. Each guard, with a bug
that turned it red:

| Guard (behavior) | Bug that turned it red |
|---|---|
| accepts a conforming study (path and inline dictionary, declared missing codes) | missing codes ignored; dictionary by path never loaded; `check` always OK |
| accepts values on both range bounds | upper or lower bound exclusive |
| matches numeric allowed values by number | allowed values compared as text |
| missing, extra or repeated column, ragged row, variable declared twice | each class dropped, one mutant per class |
| type violations (integer, number given text) | integer parsed as number; missing tokens never recognised |
| out-of-set, out-of-range | allowed-set test dropped; range bound mutants |
| undeclared missing code, empty cell | missing tokens never recognised |
| duplicate id | duplicates never reported; id test on the wrong role |
| numeric without units | units test dropped; units demanded of strings |
| contract-version mismatch; repeated dataset id | check dropped |
| absent dataset file, empty data file, absent dictionary file, manifest not an object | each check dropped or made to crash |
| schema error names the allowed keys | errors swallowed; hint dropped |
| a manifest still holding TODO is flagged | placeholder check returns nothing |
| `RESULT=PROBLEMS n` counts each problem | count hard-coded to 1 |
| `compare` SWAPPABLE ignoring metadata, descriptions, variable order | descriptions or variable order taken as shape |
| `compare` DIFFERS names each field's difference | each of type, units, range, allowed values, missing codes, role, protocol and contract version ignored, one mutant each |
| `compare` variable or dataset on one side only | each of the four checks dropped |
| `compare` counts every difference | count hard-coded; first variable only; DIFFERS never emitted |
| `compare` refuses a manifest that breaks the schema | refusal removed |
| `init`: header, delimiter, format, overwrite, TODO placeholders, usage errors | second line read as header; TSV split on commas; format hard-coded; overwrite allowed; origin filled; last variable omitted; usage checks removed |
| CLI exit 64 | usage exit 2; argparse exit 2 kept; unreadable input exit 1 |

## Resolution

Every finding was accepted and is fixed. None was rejected.

| Owner | Findings | Fix commit | Merge |
|---|---|---|---|
| coordinator | F1 | `760c2d6` | on the branch |
| root_skill | F2, F3, F4, F11 to F14, F16 to F18, F23 | `f399211`, rebased | `8c67adb` |
| science_method | F2, F5, F10, F20, F21 | `518918c`, rebased | `215c537` |
| test_landscape | F5, F15, F19, F24 | `6739573`, rebased | `c8c00d9` |
| study_contract | F4, F6 to F9, F22 | `bfff14d` (red guards), `036e722`, rebased | `0bd653d` |
| coordinator | seams: the plan's protocol category names clusters, time and event status; the script map says `compare` never opens data | `23839c7` | on the branch |

**Rerun of the attacks that found something.**
- A2: the narrowed banned-word check (it bans "deviation" except in "standard deviation") prints nothing.
- A3: "SD" is defined at first use in both files.
- A4: "study contract" is the only name. The pair "known-truth check" (a confirm) and "known-truth run" (the guard's proof on the whole battery) replaces calibration and validation, in `SKILL.md` and in the science references.
- A8: software step 1's gate now names `software-planning.md`.
- A11: the Proportions family now ends by asking for the unnamed case.
- `quick_validate`: valid, description 1024 characters.
- `SKILL.md`: 214 lines.
- Guards: 79 passed. That is 56 − 2 merged count tests + 25 new guards.

**Mutation evidence for the new guards.** 28 injected bugs, each turning a new or changed guard red. Two mutants survived the first pass and each got a guard: an equal-bounds range rejected, and `utf-8-sig` dropped in `init`. The older guards were not re-mutated; they pass on the changed code.

**Follow-up from the user.** A separate read-only review for meta-discourse and context contamination runs on the merged result before wiring.
