# Consistency review

**Goal**: Attack the merged skill for drift from R01 and Eliott's words, for broken routing from the root, and for prose that invites stopping at a list, and get every finding fixed by the leaf that owns it.
**Pre-conditions**:
- [ ] All five L0 leaves merged into `claude/test-design-skill-03d1cc`; the verifier works read-only on that branch
- [ ] R01 in full, its appendix first, read by the verifier
**Success Gates**:
- ⬜ The findings report names, for each attack below, what was attacked, how, and what was found (an attack that found nothing says so)
- ⬜ Every finding is fixed by the owning leaf's implementer or answered by the coordinator with a reason
- ⬜ The standalone and banned-word grep over `skills/designing-tests` prints nothing
**References**: [R01, appendix first](../../../__reports__/designing_tests/00-architecture_designing_tests_v0.md) — the design and Eliott's words, which win over leaf prose

## Step 1: Attack and record
**Goal**: Assume something is wrong and find it.
**Implementation Logic**:
The verifier is read-only and assumes the skill is broken until shown otherwise. Attacks, each reported with its result: a cold read of `SKILL.md` as a fresh agent given a feature to plan and a study to design (where would it stop, which reference would it never open, where would a weaker model need more); the root against each reference (every procedure step's gate names a reference that actually explains it; roles defined the same way everywhere); the role definitions against Eliott's words in the appendix; any count target, ratio, tier or "N tests" phrasing; "invariant" and "deviation"; bug advice that leads to one test per bug; catalogs and tables that do not open with a principle or do not end by asking for the unlisted case; one term per concept (grep for synonyms of guard, confirm, probe, battery, evolution log, study contract); every reference linked from `SKILL.md` and each over 100 lines with a `## Contents`; relative links that do not resolve; the script's features each traced to one of the three problems of R01 §7, and its guards attacked for tautology (would a plausible wrong implementation pass?); names of other skills, repositories or org tools. The coordinator writes the findings, with each one's owning file and leaf, to the report below.
**Deliverables**: `__reports__/designing_tests/01-consistency_review_v0.md` (sections: attacks and results, findings by owning leaf, questions for the coordinator)
**Consistency Checks**: `test -f __reports__/designing_tests/01-consistency_review_v0.md && ! grep -riE 'writing-reports|managing-roadmaps|writing-history|writing-release|plumage|playbook|skill-creator|dataviz|waiting-on-processes|spawning-agent-plugins|invariant|deviation' skills/designing-tests` (expected: PASS)
**Commit**: `docs(reports): record the consistency review of designing-tests`

## Step 2: Fix through the owners
**Goal**: Close every finding where it belongs.
**Implementation Logic**:
The coordinator sends each finding to the implementer of the owning leaf with `SendMessage`; the implementer fixes it on its own branch, which the coordinator rebases and merges as at L0. A finding the coordinator rejects is answered in the report with its reason. Small cross-file fixes with no owning leaf (a link, a term) the coordinator makes itself. After the fixes, rerun the attacks that found something.
**Deliverables**: fixes under `skills/designing-tests/` on the owning leaves' branches; `__reports__/designing_tests/01-consistency_review_v0.md` (updated: each finding's resolution)
**Consistency Checks**: `uv run tools/quick_validate.py skills/designing-tests && ! grep -riE 'writing-reports|managing-roadmaps|writing-history|writing-release|plumage|playbook|skill-creator|dataviz|waiting-on-processes|spawning-agent-plugins|invariant|deviation' skills/designing-tests` (expected: PASS)
**Commit**: `fix(designing-tests): resolve the consistency review findings`
