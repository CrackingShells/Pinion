# Marketplace source pinning — Test Definition (v0)

Date: 2026-10-09

Proves the change in [00-architecture_relative_marketplace_sources_v0.md](00-architecture_relative_marketplace_sources_v0.md).

## Executive Summary

- **What must be proven:**
  - same-repo marketplaces never pin a sibling plugin to a URL;
  - root output is byte-for-byte unchanged;
  - the checker accepts the new shapes and steers old repos to repair without failing them;
  - real installs work from a fork branch and a local path.
- **Top risks → tests:**

  | Risk | Tests |
  |---|---|
  | R1 a sibling source still names a URL | T1 |
  | R2 root plugin output changes | T2, plus the existing `test_regeneration` |
  | R3 the checker rejects the new shapes | T3 |
  | R4 old repos get no repair signal, or turn red | T4 |
  | R5 Codex `local` subdirectory doesn't install | G1 / I2 |
  | R6 hub mode regresses | T5 |

- **Volume:** 5 regression tests (stdlib, run under pytest like `evals/test_regeneration.py`) plus a
  live integration matrix of 3 installs, recorded as findings rather than automated.

## Scope

### In scope

`_claude_source`, `_codex_source`, `build_claude_marketplace`, `build_codex_marketplace` output for root
and sibling plugins, and the `check_plugin.py` marketplace-entry checks plus the new advisory.

### Out of scope

`install-snippet` (a separate known gap); hooks, dev plugins and MCP manifests (unchanged); downstream
repos; Claude Code / Codex / VS Code internals (exercised live only, never mocked).

### Assumptions

- `evals/fixtures/two_plugins.spec.json` stays the multi-plugin fixture. A root-plugin spec exists
  (`assets/examples/colgrep-mcp.spec.json`).
- Tests import the scripts by path, as `test_regeneration.py` does, with no third-party dependency.
- Gate G1 has been run, and its result decides whether T1/T3 assert the Codex `local` shape or keep `git-subdir`.

### Trust boundaries

- Generator and checker: exercised for real, in a temp directory.
- Hosts (Claude Code, Codex, VS Code): never mocked; covered only by the live matrix I1–I3.

## Test Matrix

| Group | Scenario | Risk it covers | Tier | Setup / Data | Assertion (observable) |
|------:|----------|----------------|------|--------------|-------------------------|
| Gen | T1 sibling sources are relative in both marketplaces (parameterized over ecosystem) | R1 | regression | `plugin_entries(two_plugins spec)` → `build_claude_marketplace` / `build_codex_marketplace` | each sibling entry's `source` is `"./<dir>"` (Claude) / `{"source": "local", "path": "./<dir>"}` (Codex); no entry carries `url` anywhere in its source |
| Gen | T2 root plugin sources unchanged | R2 | regression | root spec (colgrep-mcp example) | Claude `source == "./"`, Codex `source == {"source": "local", "path": "./"}` |
| Check | T3 a freshly spawned two-plugin tree passes the checker | R3 | integration (`component`) | `spawn` two_plugins spec into a temp dir (not dry-run), then `collect_problems(root, spec)` | returns `[]` |
| Check | T4 a legacy `git-subdir` self-URL entry is advisory, not a problem (parameterized over ecosystem) | R4 | regression | the T3 tree with one entry's source replaced by `{git-subdir, url: <own repository>.git, path}` | `collect_problems` returns `[]`; `notes` contains one line naming the entry and `marketplace-source-pinning` |
| Hub | T5 hub-mode spec still writes no marketplace | R6 | regression | two_plugins spec plus `"marketplace": {"hub": "<url>"}`, `spawn --dry-run` | neither marketplace path appears in `Writer.written` or `Writer.merged` |

Integration matrix (live, `end_to_end`, recorded in `01-findings_…`, not automated):

| Id | Host | Marketplace added from | Expected |
|---|---|---|---|
| I1 | Claude Code | fork `#branch` with two spawned siblings that are absent upstream | both install; `claude mcp list` shows them connected (if they carry servers) or `plugin list` shows them enabled |
| I2 (= G1) | Codex | fork URL + branch, and a local path | install succeeds both ways |
| I3 | VS Code | local folder (`chat.pluginLocations`) and fork `main` via Install Plugin from Source | plugins discovered and installed |

## Fixtures / Test Data Strategy

- **Data needed:** the existing `two_plugins.spec.json` and colgrep-mcp example spec. T4 mutates the T3
  output in memory, so no new fixture file is needed.
- **Where it lives:** `skills/spawning-agent-plugins/evals/` (the skill keeps tests there; there is no `tests/` dir).
  Proposed file: `evals/test_marketplace_sources.py`.
- **Mock vs real:** no mocks. Generator and checker run for real against `tempfile.TemporaryDirectory()`.
  Hosts run only in the live matrix.

## Observability Requirements

- Run with `python -m pytest skills/spawning-agent-plugins/evals -q` and keep the output in the PR description.
- Live matrix: record the exact commands, host versions and outcomes in the findings report, as
  `mcp-biomodelling-servers`' `verification_note.md` did.

## Minimal Must-Run Regression Set

- T1 (sibling sources relative)
- T2 (root unchanged)
- T4 (legacy entries advisory, not red)
- existing `test_regeneration.py::test_spec_regenerates_manifests`

## Scope Control Notes

- **Consolidations:** T1 and T4 are each one parameterized test over `{claude, codex}` rather than two.
  The root and sibling path forms of the checker are collapsed into T3, since a spawned tree exercises both.
- **Size:** 5 regression tests, within the "bug fix" bound once T5 is counted as protection against hub-mode regression.
