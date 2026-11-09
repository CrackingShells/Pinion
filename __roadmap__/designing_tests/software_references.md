# Software references

**Goal**: Write the four software references so an agent at any application size names the guards that matter, keeps confirms transient, keeps probes out of the suite, and recognizes false safety without being handed a count.
**Pre-conditions**:
- [ ] Working in a worktree on `task/designing-tests-software_references`, cut from `claude/test-design-skill-03d1cc`; every command below runs from the worktree root
- [ ] R01 §1c, §2, §3, §4, §6 (software test plan) and the appendix read in full; R02 read for what is kept
**Success Gates**:
- ⬜ The four files exist under `skills/designing-tests/references/` with the names below, each over 100 lines opening with a `## Contents` list
- ⬜ The role × scope matrix gives every one of the 9 cells a typical use and a typical mistake
- ⬜ Bugs lead to the behavior that lacked a guard; nowhere does the prose advise one test per bug
- ⬜ The false-safety catalog opens with its principle, explains why each entry fails, and ends by asking for the case it does not list
- ⬜ The standalone and banned-word grep over `skills/designing-tests` prints nothing
**References**: [R01 §4, §6, appendix](../../__reports__/designing_tests/00-architecture_designing_tests_v0.md) — the method; [R02](/Users/hacker/Documents/src/CrackingShells/cracking-shells-playbook/skills/writing-reports/references/software-test-definition.md) — kept principles (risk first, test what we own, observable behavior, ownership check, equivalence classes, boundaries, pairwise, parameterization, trust boundaries, must-run set)

## Step 1: Roles, scope and planning
**Goal**: Define how roles compose with scope, and how a plan decides which guards exist.
**Implementation Logic**:
`software-roles-and-scope.md`: the roles table of R01 §4 (purpose, lifetime, where it lives), stated with "expected behavior" as the thing a guard defines; the scope axis and why a guard's scope is where its behavior is observable to its consumer, through that consumer's interface; the 3×3 matrix with a typical use and a typical mistake per cell; the lifecycle (probe answered then deleted, or turned into a boundary guard; confirm culled when its guard passes, promoted only when rewritten to guard standards); the TDD flow (guard first and red, confirms for the baby steps, guard green, confirms culled).
`software-planning.md`: where guard candidates come from (behaviors consumers rely on, design cornerstones, seams with code we do not own); the distinct-failure rule replacing every count; equivalence classes, boundaries, pairwise and parameterization as the means of applying it; bugs go to behaviors (the five-step sequence of R01 §4, and the "one test per incident" signal); the software test plan's categories (R01 §6, including what was deliberately not tested and why, and done-criteria); how to embed guards and probes in a feature, implementation or roadmap plan without enumerating confirms; a bug fix's plan as one line.
Both files explain why, so the reader can judge a case the text does not name.
**Deliverables**: `skills/designing-tests/references/software-roles-and-scope.md` (sections: roles, scope, role × scope matrix, lifecycle, TDD flow); `skills/designing-tests/references/software-planning.md` (sections: where guards come from, distinct-failure rule, bugs go to behaviors, the test plan's categories, tests inside a larger plan)
**Consistency Checks**: `for f in software-roles-and-scope software-planning; do p=skills/designing-tests/references/$f.md; test -f $p || exit 1; [ "$(wc -l < $p)" -le 100 ] || grep -q '^## Contents' $p || { echo "no TOC: $f"; exit 1; }; done` (expected: PASS)
**Consistency Checks**: `! grep -riE 'writing-reports|managing-roadmaps|writing-history|writing-release|plumage|playbook|skill-creator|dataviz|waiting-on-processes|spawning-agent-plugins|invariant|deviation' skills/designing-tests` (expected: PASS)
**Commit**: `feat(designing-tests): add the software roles, scope and planning references`

## Step 2: Writing and false safety
**Goal**: Say how each role is written, and how to tell a test that protects from one that only reassures.
**Implementation Logic**:
`software-writing.md`: the writing rules of R01 §4 (name states the behavior; expected values derived independently by hand, oracle or property; no logic in tests; one behavior per test; failure messages name what broke; real thing at boundaries we own, mocks only for what we do not own; deterministic), then per role: how a guard is written to survive refactors, how a confirm is marked with the project's own means (marker, name, tag) so culling is mechanical, why a probe stays outside the suite and where its answer goes; fixtures and trust boundaries; the must-run set.
`software-false-safety.md`: the principle (tautological when no plausible wrong implementation makes it fail, or when it restates its input; trivial when its failure would change no decision); the catalog of R01 §4 as worked illustrations, each saying why it fails; the signs of explosion; the mutation check as the detector, with the ownership check as its special case and mutation tools optional; the role-aware self-review loop. The catalog ends by asking the reader to look for the case it does not list.
**Deliverables**: `skills/designing-tests/references/software-writing.md` (sections: rules for every test, guards, confirms, probes, fixtures and trust boundaries, must-run set); `skills/designing-tests/references/software-false-safety.md` (sections: the principle, catalog, signs of explosion, mutation check, self-review)
**Consistency Checks**: `for f in software-roles-and-scope software-planning software-writing software-false-safety; do p=skills/designing-tests/references/$f.md; test -f $p || exit 1; [ "$(wc -l < $p)" -le 100 ] || grep -q '^## Contents' $p || { echo "no TOC: $f"; exit 1; }; done` (expected: PASS)
**Consistency Checks**: `! grep -riE 'writing-reports|managing-roadmaps|writing-history|writing-release|plumage|playbook|skill-creator|dataviz|waiting-on-processes|spawning-agent-plugins|invariant|deviation' skills/designing-tests` (expected: PASS)
**Commit**: `feat(designing-tests): add the software writing and false-safety references`
