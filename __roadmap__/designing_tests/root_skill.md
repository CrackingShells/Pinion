# Root SKILL.md

**Goal**: Give `designing-tests` its release line and a root `SKILL.md` that routes an agent, at the moment of use, through both procedures and into the right reference.
**Pre-conditions**:
- [ ] Working in a worktree on `task/designing-tests-root_skill`, cut from `claude/test-design-skill-03d1cc`; every command below runs from the worktree root
- [ ] R01 read in full, especially §1b, §1c, §2, §3, §6 and the appendix
**Success Gates**:
- ⬜ `uv run tools/quick_validate.py skills/designing-tests` prints "Skill is valid!"
- ⬜ `SKILL.md` is under 500 lines and links every one of the 11 references, both assets and the script by the names in R01 "Skill layout"
- ⬜ Each of the two procedures lists its steps in order and ends every step with a gate phrased as a question about the principle, naming the reference that explains it
- ⬜ The standalone grep over `skills/designing-tests` prints nothing
**References**: [R01 §1b, §1c, §2, §3, §6, Skill layout, appendix](../../__reports__/designing_tests/00-architecture_designing_tests_v0.md) — what the root must hold; [R03](../../skills/waiting-on-processes/SKILL.md) — house voice

## Step 1: Release line
**Goal**: Make `designing-tests` releasable on its own line, like its siblings.
**Implementation Logic**:
Copy the sibling pattern exactly. `package.json` holds only `name` and `version` (`0.0.0`, so the first `feat` releases 1.0.0). `.releaserc.js` is one line requiring the shared factory with the skill's name. No CHANGELOG.md: semantic-release creates it.
**Deliverables**: `skills/designing-tests/package.json` (`name: designing-tests`, `version: 0.0.0`); `skills/designing-tests/.releaserc.js` (`require('../../release-config')('designing-tests')`)
**Consistency Checks**: `node -e "const c=require('./skills/designing-tests/.releaserc.js'); const p=require('./skills/designing-tests/package.json'); process.exit(c.branches[0]==='main' && p.name==='designing-tests' && p.version==='0.0.0' ? 0 : 1)"` (expected: PASS)
**Commit**: `build(release): give designing-tests its own release line`

## Step 2: Root SKILL.md
**Goal**: Write the root that makes the constraints visible where they bite.
**Implementation Logic**:
Frontmatter uses only the portable fields of R01 §1b, with the exact `license`, `compatibility` and `allowed-tools` values given there. Start the description from R01's draft: third person, under 1024 characters, no angle brackets, triggers kept in the description (co-loading with feature, implementation and roadmap planning depends on them). Do not write `metadata.version`.
The body, in this order:
1. What the skill is for, in a few lines: a test exists to answer a stated question and must be able to fail; the two meanings of "test".
2. The three roles, defined once by purpose, then lifetime, then weight of evidence (R01 §3), with the science mapping and its two limits (controls are not confirms; the field's own terms stay alongside).
3. The software procedure in order (from R01 §4): name expected behaviors and their consumers → choose each guard's scope → plan probes as their own steps → write guards first, confirms while building → mutation check → cull or promote confirms. Every step ends with a one-line gate that asks about the principle (for example "could a plausible wrong implementation pass this guard?") and names its reference.
4. The science procedure in order (R01 §5 steps 1–9), each step with its gate and reference. The validity gate asks for recorded evidence; the data gate is low freedom: run exactly `uv run scripts/study_contract.py check <manifest>` and fix until `RESULT=OK` before any test runs on a dataset (validate → fix → repeat).
5. Non-negotiables: few, each with the signal that shows it is being broken (no count targets; a guard that was never seen failing is not a guard; assumptions that drive n are agreed, not guessed; every pre-specified outcome is shown; the design is explained to whoever ordered it).
6. The explanation contract (R01 §6): what the explanation covers, plain terms, the human in chat or the agent in the hand-off report.
7. Where plans go: the project's own convention first, otherwise inline in the plan being written, otherwise ask.
8. The reference map, read as "where you are → what to open", linking every reference, both assets and the script directly (one level deep), and saying for the script whether to run it (yes) and for assets whether to copy or read them.
Stay concise for the agent (R01 §1c): spend words on judgement and traps, not on what a strong model already knows. Keep every list visibly a sample (R01 §2 "Balance"). Leave depth to the references; the root routes.
**Deliverables**: `skills/designing-tests/SKILL.md` (frontmatter `name`, `description`, `license`, `compatibility`, `allowed-tools`; sections for purpose, roles, software procedure with gates, science procedure with gates, non-negotiables, explanation contract, where plans go, reference map)
**Consistency Checks**: `uv run tools/quick_validate.py skills/designing-tests` (expected: PASS)
**Consistency Checks**: `test "$(wc -l < skills/designing-tests/SKILL.md)" -lt 500 && for f in software-roles-and-scope software-planning software-writing software-false-safety science-questions-and-tests science-test-landscape science-protocol-and-sample science-data science-showing-and-explaining science-false-safety science-analysis-plan; do grep -q "references/$f.md" skills/designing-tests/SKILL.md || { echo "missing $f"; exit 1; }; done && grep -q 'scripts/study_contract.py' skills/designing-tests/SKILL.md && grep -q 'assets/study-contract.schema.json' skills/designing-tests/SKILL.md && grep -q 'assets/data-dictionary.example.json' skills/designing-tests/SKILL.md` (expected: PASS)
**Consistency Checks**: `! grep -riE 'writing-reports|managing-roadmaps|writing-history|writing-release|plumage|playbook|skill-creator|dataviz|waiting-on-processes|spawning-agent-plugins|invariant|deviation' skills/designing-tests` (expected: PASS)
**Commit**: `feat(designing-tests): add the root skill with both procedures and their gates`
