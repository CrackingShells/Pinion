# marketplace_source_pinning reports

`spawn` writes sibling plugins' marketplace sources as `git-subdir` + the spec's repository URL. That pins
every install to the upstream default branch and breaks installs from a fork, a branch or a local checkout.
Found while packaging `marcorusc/mcp-biomodelling-servers` (PR marcorusc/mcp-biomodelling-servers#10).

## Round 00 (2026-10-09)

| Report | Covers | Latest |
|:-------|:-------|:------:|
| [00-observation_git_subdir_pins_installs_v0.md](00-observation_git_subdir_pins_installs_v0.md) | The defect, the install evidence across Claude Code, Codex and VS Code, and the location map | ✓ |
| [00-architecture_relative_marketplace_sources_v0.md](00-architecture_relative_marketplace_sources_v0.md) | Fix: relative sources in both marketplaces, checker advisory, trap entry; gate G1 for Codex | ✓ |
| [00-test_definition_marketplace_sources_v0.md](00-test_definition_marketplace_sources_v0.md) | 5 regression tests and a 3-host live install matrix | ✓ |

## Status

- Open. No code changed yet.
- Next step: gate G1, a live Codex check of `{"source": "local", "path": "./plugins/<x>"}`, recorded as `01-findings_…`.
- Then the generator and checker change, in Pinion's `skills/spawning-agent-plugins/` (edit there until the hand-over, `rp-09`).
- Tracked by the macOS reminder `id: skills-spawning-plugins-marketplace-source-pinning` (list *Agent Skills*).
