# Wiring

## Context
The third level runs after both verifiers' fixes are merged. It is mechanical, so the coordinator does it: the plugin spec entry, generated manifests, the assembled plugin copy, and the README row. It produces `plugins/designing-tests/` and the edits to `plugin.spec.json` and `README.md`.

## Goal
Make `designing-tests` installable as a Nest-listed plugin and list it in the README.

## Pre-conditions
- [ ] `review/consistency_review.md` and `review/statistics_review.md` are `done`
- [ ] `git status --porcelain plugins/` is empty before starting, so any diff afterwards is this level's

## Success Gates
- ✅ `uv run skills/spawning-agent-plugins/scripts/check_plugin.py --root . --spec plugin.spec.json` reports no problems
- ✅ Re-assembling the existing plugins leaves their files unchanged (`git diff --quiet plugins/ -- ':!plugins/designing-tests'`)
- ✅ `README.md` lists `designing-tests` in its Skills table

## Status
```mermaid
graph TD
    wiring[Plugin and README wiring]:::done
    classDef done       fill:#166534,color:#bbf7d0
    classDef inprogress fill:#854d0e,color:#fef08a
    classDef planned    fill:#374151,color:#e5e7eb
    classDef amendment  fill:#1e3a5f,color:#bfdbfe
    classDef blocked    fill:#7f1d1d,color:#fecaca
```

## Nodes
| Node | Type | Status |
|:-----|:-----|:-------|
| `wiring.md` | 📄 Leaf Task | ✅ Done |

## Amendment Log
| ID | Date | Source | Nodes Added | Rationale |
|:---|:-----|:-------|:------------|:----------|

## Progress
| Node | Branch | Commits | Notes |
|:-----|:-------|:--------|:------|
