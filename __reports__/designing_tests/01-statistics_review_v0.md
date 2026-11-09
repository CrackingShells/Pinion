# designing-tests — Statistics review (v0)

Date: 2026-11-09. Read-only review of the merged skill at `8929463`: the statistical claims of
the science references and the landscape, their sources, and whether `study_contract.py` lets
through data that would silently break a test. The verifier changed no file; its scratch data
were deleted.

## Attacks and results

| Attack | Result |
|---|---|
| Validity conditions in the landscape: wrong, missing, uncheckable | Mostly sound and checkable without a gatekeeping test. Gaps in F3, F4, F7 to F11 |
| Sources that do not say what is claimed | 15 landscape sources opened (full text or abstract): the numbers hold. Three need narrowing (F11, F12, F13) |
| Prose implying the map is exhaustive | None |
| Formulas: design effect, attrition, Monte Carlo SE, optimal allocation, Holm, BH and BY, TOST and its (1 − 2α) interval | All correct. The design effect holds only for equal cluster sizes (F14) |
| Post-hoc power or pilot-effect power presented as acceptable | None; both are named as false safety, with SESOI, sensitivity curve and MDE as the alternatives |
| "No difference" without an equivalence path | The path exists in all three places; the pattern table leaves the interval level implicit (F2) |
| Pseudoreplication | The protocol guidance catches it; the shuffled-label check can hide it (F5); the contract cannot name the unit (F1) |
| Battery and pattern-of-outcomes method | Sound, but known-truth runs cover only H0 and one effect, and the rate of each outcome pattern is never measured (F2) |
| Known-truth runs detect a broken pipeline | The prose does; the `SKILL.md` gate reads as a single run (F6) |
| `check` on 20 bad datasets | Lets through zero rows, an outcome entirely missing, untyped factor levels, blank strings, infinities, no outcome role, no id (F15, F16) |
| `compare` on 6 pairs | Calls a study with a missing data file SWAPPABLE; misses a change of unit of observation; flags reordered allowed values (F1, F17) |

### Sources

Opened and supporting: Delacre et al. 2017; Rochon et al. 2012 (narrow, F12); IntHout et al.
2014; Campbell 2007; Vehtari et al. (arXiv:1903.08008); Dietterich 1998; Benavoli et al. 2017
(narrow, F11); Raschka 2018 (narrow, F13); Haverkamp and Beauducel 2017; Greenacre et al.;
Landler et al. 2018 (in part); Bradburn et al. 2003; Luke 2017; Karch 2021 (core); IntHout et al.
2016 (in part). The science references' citations from memory that the verifier could check
(Albers and Lakens 2018, Hoenig and Heisey 2001, Lakens 2017, Kriegeskorte et al. 2009) support
what is claimed; Weissgerber 2015, Hurlbert 1984, Gelman and Loken 2013, Altman and Bland 1995 and
Schuirmann 1987 were not retrieved.

## Findings and decisions

Decision legend as in the consistency review.

| # | Where | Finding | Decision | Owner |
|---|---|---|---|---|
| F1 | schema roles; `science-data.md`; `check_dataset` | The contract cannot name the unit of independence. Repeated measures fail with "duplicated id" unless the subject is hidden in a composite id, and `compare` cannot tell one row per subject from repeated rows | accept: each dataset declares its `unit`, the variable whose levels are independent (it may repeat across rows); the `id` variables jointly key the rows; `compare` treats the unit as shape. `science-data.md` says what the contract does not express (clusters, pairing, time, event status), which the plan's protocol section carries. The schema's `$id` stays at 1, because the contract has never been released | study_contract |
| F2 | `science-questions-and-tests.md` pattern table; `science-protocol-and-sample.md` known-truth runs | (a) Interval level not stated per row (90% for TOST at 5%, 95% for the difference); (b) only H0 and one effect are simulated, never the artifact the battery claims to rule out; (c) the rate of each outcome pattern per scenario is never measured | accept: interval level per row; one known-truth scenario per distinction the battery claims; the rate of each pattern per scenario with its Monte Carlo SE | science_method |
| F3 | landscape, signed-rank | Missing the symmetry of differences under H0 | accept | test_landscape |
| F4 | landscape, Bland-Altman | Missing approximate normality of differences and the CI on each limit | accept | test_landscape |
| F5 | `science-false-safety.md`, shuffled labels | A row-level shuffle breaks dependence and hides pseudoreplication; one shuffle proves little | accept: permute at the unit of assignment, many times, read the rejection rate against nominal | science_method |
| F6 | `SKILL.md` step 5 gate | Reads as one run | accept: false-positive rate near nominal and power at the stated effect, each with its Monte Carlo interval | root_skill |
| F7 | landscape, mixed models | Kenward-Roger and Satterthwaite are for linear mixed models; likelihood-ratio comparison of fixed effects needs ML | accept, with what to use for GLMMs and its source | test_landscape |
| F8 | landscape, all families | The missing-data mechanism is absent (complete case and GEE need MCAR, likelihood-based mixed models MAR) | accept: one shared row in "Reading your situation", checked by argument from the design plus a sensitivity analysis | test_landscape |
| F9 | landscape, Bayesian | R-hat alone; Vehtari et al. also ask for at least 4 chains and bulk and tail ESS above 400 | accept | test_landscape |
| F10 | landscape, meta-analysis | HKSJ default without the tau² estimator or the few-studies caution | accept: the implementer opens the Cochrane chapter and states what it supports | test_landscape |
| F11 | landscape, corrected resampled t | n means resamples here; the attribution is about the fold correlation; the correction is a heuristic for k-fold | accept | test_landscape |
| F12 | landscape; `science-questions-and-tests.md`; `science-false-safety.md` | Rochon: n = 30 per group; the conditional rate is distorted while the overall rate stays near nominal; the authors still advise against pretesting | accept | test_landscape, science_method |
| F13 | landscape, McNemar | The "both counts above 50" rule is for the continuity-corrected test; the usual exact-test rule is b + c < 25 | accept: the implementer finds a primary source for the rule or drops it | test_landscape |
| F14 | `science-protocol-and-sample.md`, design effect | Exact only for equal cluster sizes | accept: the implementer opens Eldridge et al. 2006 for the unequal-size inflation | science_method |
| F15 | `check_dataset` | Passes zero rows, an outcome entirely missing, factors with no allowed values, no outcome role, whitespace-only cells, infinities | accept in part: each of these becomes a problem. Rejected: a single-level factor and unbalanced groups, because whether they break a test depends on the battery, not on the shape; `science-data.md` lists them under what `check` does not catch | study_contract |
| F16 | `check_dataset` | No duplicate check without an `id` role | accept: covered by consistency F8 (a dataset with no `id` variable is a problem) | study_contract |
| F17 | `cmd_compare`; `science-data.md` exit codes | (a) `compare` never opens data, yet the doc implies it does; (b) the unit of observation is invisible; (c) reordered allowed values give a false DIFFERS | accept: (a) as consistency F7; (b) through F1; (c) compared as sets | study_contract |

## Questions for the coordinator, answered

1. **F1, roles or documentation?** A `unit` field per dataset, plus documentation of the rest. The
   unit is what decides whether a battery written for one dataset is valid on another, which is
   the contract's one problem; clusters, pairing and time are protocol, and belong in the plan.
2. **F15 and F16, conformance only or data shape?** Problems, not warnings: a second severity
   would make `RESULT=OK` ambiguous. Each one admitted is a property of the data's shape that no
   battery can survive; anything that depends on the battery stays with the plan.
3. **F17, should `compare` read data?** No; it compares contracts, and the doc says to run `check`
   on both sides first.
4. **F10 and F13, second pass?** Yes, by the landscape's implementer, who opens the sources or
   narrows the claim.
5. **Sources not read by the verifier.** The landscape's sources were opened by its implementer
   under the leaf's rule, and the 15 spot checks held, so they stand. The science references'
   citations from memory are opened and completed under consistency F20.
