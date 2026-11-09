# designing_tests

## Context
Pinion gains a fourth kind of agent mechanics: a standalone skill, `designing-tests`, that designs tests in both senses of the word. Software: which tests deserve to exist (roles guard, confirm and probe, composed with the unit, integration and end-to-end scope), written so they can fail. Science: the battery of statistical tests that answers a research question, designed together with the protocol, sample, cohort, data contract and figures. It replaces the playbook's test-definition report type and makes Eliott's recurring test prompt unnecessary. Depends on nothing in this repository except the release and packaging tools; produces `skills/designing-tests/`, its plugin under `plugins/designing-tests/`, and the README row.

## Reference Documents
- [R01 Architecture](../../__reports__/designing_tests/00-architecture_designing_tests_v0.md) — the approved design (§1–§7, layout, wiring, execution model) and, in its appendix, Eliott's words verbatim, which win over any leaf prose
- [R02 Old reference](/Users/hacker/Documents/src/CrackingShells/cracking-shells-playbook/skills/writing-reports/references/software-test-definition.md) — the test-definition reference being replaced; read for what is kept and what is dropped (R01 Context), never copy its size table or tiers
- [R03 House style](../../skills/waiting-on-processes/SKILL.md) — Pinion's SKILL.md voice: long pushy third-person description, numbered sections, tables, references linked relative to the skill
- [R04 Category style](/Users/hacker/Documents/src/CrackingShells/cracking-shells-playbook/skills/writing-reports/references) — how a report type is defined by the categories it must establish rather than by a template (for R01 §6 artifacts)
- [R05 Skill best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) — Anthropic's authoring rules, summarized as R01 §1c

## Goal
Ship `skills/designing-tests/` as a validated, packaged, Nest-listed Pinion skill that names no other skill.

## Pre-conditions
- [x] R01 approved by Eliott (2026-11-09)
- [x] `uv run tools/quick_validate.py skills/waiting-on-processes` prints "Skill is valid!" in this worktree (environment measured)

## Success Gates
- ✅ `uv run tools/quick_validate.py skills/designing-tests` prints "Skill is valid!"
- ✅ `uv run --with pytest --with jsonschema pytest skills/designing-tests/evals/ -q` passes, and each guard was seen failing (recorded in the Progress notes of `study_contract`)
- ✅ `grep -riE 'writing-reports|managing-roadmaps|writing-history|writing-release|plumage|playbook|skill-creator|dataviz|waiting-on-processes|spawning-agent-plugins' skills/designing-tests` prints nothing
- ✅ `uv run skills/spawning-agent-plugins/scripts/check_plugin.py --root . --spec plugin.spec.json` reports no problems
- ✅ `git diff main --stat` touches only `skills/designing-tests/`, `plugins/designing-tests/`, `plugin.spec.json`, `README.md`, `__roadmap__/designing_tests/` and `__reports__/designing_tests/`

## Gotchas
- Fixed vocabulary, one term per concept (R01 §1c): guard, confirm, probe; unit, integration, end-to-end; expected behavior (never "invariant"); research question, hypothesis, statistical question, battery, pattern-of-outcomes table, SESOI (only where an effect size is meaningful), evolution log (never "deviation"), study contract, data dictionary, known-truth run. A role is always paired with the field's own term in science ("probe: exploratory analysis").
- Fixed file names: the layout in R01 "Skill layout" is the contract between parallel leaves. Link to a sibling leaf's file by that name even before it exists; never invent another file.
- Standalone: nothing under `skills/designing-tests/` names another skill, repository or tool of this org. The R02–R04 sources are inspiration, not citations.
- No count targets, no code:test ratios, no tiers. Checklists are samples: every catalog opens with its principle and ends by asking the reader for the case it does not list (R01 §2 "Balance").
- The pre-commit hook is not active in worktrees (`core.hooksPath` is unset and is shared git config, so leave it). Once `plugins/designing-tests/` exists (after `wiring`), any later edit under `skills/designing-tests/` needs `uv run tools/assemble_plugin.py designing-tests` before committing.
- No auto-memory writes. No push, PR or release.

## Status
```mermaid
graph TD
    root_skill[Root SKILL.md]:::done
    software_references[Software references]:::done
    science_method[Science method references]:::done
    test_landscape[Statistical test landscape]:::done
    study_contract[Study contract and script]:::done
    review[Review]:::inprogress
    classDef done       fill:#166534,color:#bbf7d0
    classDef inprogress fill:#854d0e,color:#fef08a
    classDef planned    fill:#374151,color:#e5e7eb
    classDef amendment  fill:#1e3a5f,color:#bfdbfe
    classDef blocked    fill:#7f1d1d,color:#fecaca
```

## Nodes
| Node | Type | Status |
|:-----|:-----|:-------|
| `root_skill.md` | 📄 Leaf Task | ✅ Done |
| `software_references.md` | 📄 Leaf Task | ✅ Done |
| `science_method.md` | 📄 Leaf Task | ✅ Done |
| `test_landscape.md` | 📄 Leaf Task | ✅ Done |
| `study_contract.md` | 📄 Leaf Task | ✅ Done |
| `review/` | 📁 Directory | 🔄 In Progress |

## Amendment Log
| ID | Date | Source | Nodes Added | Rationale |
|:---|:-----|:-------|:------------|:----------|

## Progress
| Node | Branch | Commits | Notes |
|:-----|:-------|:--------|:------|
