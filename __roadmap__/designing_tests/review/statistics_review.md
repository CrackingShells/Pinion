# Statistics review

**Goal**: Attack the science half and the study contract for statistical errors, and get every finding fixed by the leaf that owns it.
**Pre-conditions**:
- [ ] All five L0 leaves merged into `claude/test-design-skill-03d1cc`; the verifier works read-only on that branch
- [ ] Web search and the arXiv tools are reachable, for spot-checking sources
**Success Gates**:
- ⬜ The findings report names, for each attack below, what was attacked, how, and what was found, including which landscape sources were opened and whether each says what the entry claims
- ⬜ Every finding is fixed by the owning leaf's implementer or answered by the coordinator with a reason
- ⬜ `uv run --with pytest --with jsonschema pytest skills/designing-tests/evals/ -q` passes after the fixes
**References**: [R01 §3, §5, §7, appendix](../../../__reports__/designing_tests/00-architecture_designing_tests_v0.md) — the science method and the contract

## Step 1: Attack and record
**Goal**: Assume a statistical claim is wrong and find it.
**Implementation Logic**:
The verifier is read-only and assumes the statistics are wrong until shown otherwise. Attacks, each reported with its result: validity conditions in `science-test-landscape.md` that are wrong, missing or uncheckable as written; sources that do not say what the entry claims (open a spread of them, more where the claim is surprising); any prose implying the map is exhaustive; wrong claims anywhere in the science references (what a test tests, what its default should be); post-hoc power or power from a pilot's effect presented as acceptable; a "no difference" claim without an equivalence or non-inferiority path; pseudoreplication not caught by the protocol guidance; whether the battery and pattern-of-outcomes method holds (can a battery be argued sufficient this way; is multiplicity handled across it); whether the known-truth runs would detect a broken pipeline; whether the contract's checks are sound (would `check` let through data that silently breaks a test in the battery; does `compare` call two incomparable studies SWAPPABLE). The coordinator writes the findings, with each one's owning file and leaf, to the report below.
**Deliverables**: `__reports__/designing_tests/01-statistics_review_v0.md` (sections: attacks and results, sources checked, findings by owning leaf, questions for the coordinator)
**Consistency Checks**: `test -f __reports__/designing_tests/01-statistics_review_v0.md` (expected: PASS)
**Commit**: `docs(reports): record the statistics review of designing-tests`

## Step 2: Fix through the owners
**Goal**: Close every finding where it belongs.
**Implementation Logic**:
As in the consistency review: each finding goes to the owning leaf's implementer with `SendMessage`, fixed on its branch, rebased and merged by the coordinator; rejected findings are answered with a reason in the report. A fix to the contract's checks comes with the guard that would have caught it, seen failing first. After the fixes, rerun the attacks that found something.
**Deliverables**: fixes under `skills/designing-tests/` on the owning leaves' branches; `__reports__/designing_tests/01-statistics_review_v0.md` (updated: each finding's resolution)
**Consistency Checks**: `uv run --with pytest --with jsonschema pytest skills/designing-tests/evals/ -q && ! find skills/designing-tests -type f -not -path '*/__pycache__/*' -print0 | xargs -0 perl -ne 'print "$ARGV:$.: $_" if lc($_) =~ /writing-reports|managing-roadmaps|writing-history|writing-release|plumage|playbook|skill-creator|dataviz|waiting-on-processes|spawning-agent-plugins|invariant|(?<!standard )deviation/; close ARGV if eof' | grep .` (expected: PASS)
**Commit**: `fix(designing-tests): resolve the statistics review findings`
