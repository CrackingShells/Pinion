# Review

## Context
The second level runs after all five L0 leaves are merged into `claude/test-design-skill-03d1cc`. Two read-only verifiers attack the assembled skill from different sides: consistency (root against references, vocabulary, Eliott's words, standalone, the script's trace to its problems) and statistics (correctness of the science references and of the contract's checks). Their findings go back to the implementer of the leaf that owns each file; this level closes when every finding is fixed or answered.

## Goal
Find what is wrong in the merged skill and get it fixed by the leaf that owns it.

## Pre-conditions
- [ ] All five L0 leaves are `done` and merged with `--no-ff` into `claude/test-design-skill-03d1cc`
- [ ] The seams were checked at merge: every reference the root links exists, and `science-data.md` matches the script's interface

## Success Gates
- ✅ Each verifier's findings are recorded in `__reports__/designing_tests/` and every finding is fixed or answered with a reason
- ✅ The standalone and banned-word grep over `skills/designing-tests` prints nothing
- ✅ `uv run tools/quick_validate.py skills/designing-tests` and `uv run --with pytest --with jsonschema pytest skills/designing-tests/evals/ -q` both pass after the fixes

## Status
```mermaid
graph TD
    consistency_review[Consistency review]:::done
    statistics_review[Statistics review]:::done
    wiring[Wiring]:::planned
    classDef done       fill:#166534,color:#bbf7d0
    classDef inprogress fill:#854d0e,color:#fef08a
    classDef planned    fill:#374151,color:#e5e7eb
    classDef amendment  fill:#1e3a5f,color:#bfdbfe
    classDef blocked    fill:#7f1d1d,color:#fecaca
```

## Nodes
| Node | Type | Status |
|:-----|:-----|:-------|
| `consistency_review.md` | 📄 Leaf Task | ✅ Done |
| `statistics_review.md` | 📄 Leaf Task | ✅ Done |
| `wiring/` | 📁 Directory | ⬜ Planned |

## Amendment Log
| ID | Date | Source | Nodes Added | Rationale |
|:---|:-----|:-------|:------------|:----------|

## Progress
| Node | Branch | Commits | Notes |
|:-----|:-------|:--------|:------|
