# Marketplace source pinning — Observation (v0)

Date: 2026-10-09

---
type: observation
topic: marketplace_source_pinning
spotted-during: packaging marcorusc/mcp-biomodelling-servers as four sibling plugins with spawning-agent-plugins 1.0.0 (PR marcorusc/mcp-biomodelling-servers#10)
date: 2026-10-09
domain: code
confidence: confirmed
urgency: medium
deferred-because: the fix belongs in this skill; the downstream repo was hand-patched to ship its PR
---

## What Was Noticed

For a multi-plugin spec (`plugins[]`), `spawn` writes every sibling's marketplace `source` as
`{"source": "git-subdir", "url": "<spec repository>.git", "path": "./<dir>"}`, in **both**
`.claude-plugin/marketplace.json` and `.agents/plugins/marketplace.json`. The `url` names the
repository the spec declares (the upstream). So an install always fetches that repository's default
branch, whatever checkout the marketplace itself was added from:

- a marketplace added from a **fork**, a **branch** (`owner/repo#ref`) or a **local path** still
  installs the plugin trees from the upstream default branch;
- before the plugins are merged upstream, every pre-merge install fails, in Claude Code and Codex
  alike, even though the marketplace is listed and the plugins are discovered.

A root plugin (`dir == ""`) does not have the problem: it gets `"./"` (Claude) or
`{"source": "local", "path": "./"}` (Codex), both relative to the marketplace checkout.

## Context

The skill was used as designed: one spec, `spawn`, `check_plugin.py` green, `claude plugin validate`
green. The failure only appears at install time from anything other than the upstream default branch,
which is exactly where a contributor tests before opening a PR. `check_plugin.py` *requires* the
Codex shape (`expected_kind = "git-subdir"` for siblings), so it would also flag the fix.

The downstream repo shipped with two hand edits: relative Claude sources, and a temporary commit that
pointed the Codex `url` at the fork to test, then reverted it. A second repo, `sysbio-curie/MCP_Hackaton`,
had already hand-edited its Claude marketplace to relative sources for the same reason.

## Location Map

- `skills/spawning-agent-plugins/scripts/spawn_plugin.py:338` — `_git_clone_url` (dies without `repository`)
- `skills/spawning-agent-plugins/scripts/spawn_plugin.py:344` — `_claude_source` (sibling → `git-subdir`)
- `skills/spawning-agent-plugins/scripts/spawn_plugin.py:352` — `_codex_source` (sibling → `git-subdir`)
- `skills/spawning-agent-plugins/scripts/spawn_plugin.py:360,396` — `build_claude_marketplace`, `build_codex_marketplace`
- `skills/spawning-agent-plugins/scripts/spawn_plugin.py:549` — `Writer.merge_marketplace` (appends only; never rewrites an existing entry)
- `skills/spawning-agent-plugins/scripts/check_plugin.py:136,141` — `_resolve_local_source_path`, `_source_matches` (already accept a plain string)
- `skills/spawning-agent-plugins/scripts/check_plugin.py:487` — `expected_kind = "local" if root == repo_root else "git-subdir"`
- `skills/spawning-agent-plugins/references/manifests.md:163,265` — documents the `git-subdir` sibling shape as intended
- `skills/spawning-agent-plugins/references/traps.md` — no entry for this failure yet
- `skills/spawning-agent-plugins/evals/fixtures/two_plugins.spec.json` — the multi-plugin fixture
- Paths are relative to the **Pinion** repo, where the skill is edited until the hand-over (reminder `rp-09`). The same paths and line numbers hold in `cracking-shells-playbook` `origin/main` `4bb9aec` (spawning-agent-plugins 1.0.1), which is what Nest publishes today
- Downstream evidence: `LittleCoinCoin/mcp-biomodelling-servers` `main`, file `__roadmap__/agent_plugins/integrate/verify/verification_note.md`; commits `fa7f0b4` (relative Claude sources), `2009a39` / `c4d3b8c` (Codex fork test and revert)
- Second repo with the same hand fix: `sysbio-curie/MCP_Hackaton`, `.claude-plugin/marketplace.json` (relative), commit `a20695c`

## Evidence

Install outcomes for the four `mcp-biomodelling-servers` plugins (Claude Code 2.1.273, Codex GUI,
VS Code with Copilot Chat, 2026-10-09):

| Marketplace added from | Claude source | Codex source | Claude Code | Codex | VS Code |
|---|---|---|---|---|---|
| fork branch, generator output | `git-subdir` → upstream | `git-subdir` → upstream | not run (it would fetch upstream) | listed, **all four installs fail** | — |
| fork branch | relative `./plugins/<x>` | `git-subdir` → upstream | **installs, servers connect** | — | — |
| local checkout | relative | `git-subdir` → upstream | installs | — | installs |
| fork `main` | relative | `git-subdir` → **fork** (test commit) | installs | **installs and runs** | installs and runs |
| scratch marketplace, `git-subdir` with `url` = fork + `ref` = branch | — | — | installs (proves the `./<dir>` path form is accepted) | — | — |

- After the change to relative Claude sources, `check_plugin.py --spec` still prints `ok` and
  `claude plugin validate .` passes, so the checker already tolerates the Claude fix. It would reject a
  Codex `local` sibling source (`source.source should be git-subdir`).
- VS Code's docs (code.visualstudio.com/docs/agent-customization/agent-plugins#_configure-plugin-marketplaces)
  defer the marketplace schema to Claude Code's and say relative-path entries are verified against
  repository, resolved revision and path. So VS Code is served by the same Claude file.

## Re-observation Steps

1. Spawn `evals/fixtures/two_plugins.spec.json` (or any `plugins[]` spec) into a scratch repo, commit, and push it to a branch of a fork whose upstream lacks the plugin dirs.
2. `claude plugin marketplace add <fork-owner>/<repo>#<branch>`, then `claude plugin install <plugin>@<marketplace>`.
3. Observe: the marketplace is added, and the install fetches the `url` repository's default branch and fails to find `./<dir>`.
4. Edit that Claude entry's `source` to `"./<dir>"`, push, and repeat: the install succeeds.

## Hand-off Questions

Working theory: the `git-subdir` shape was chosen because it is "the only one that names a
subdirectory" (`_claude_source` docstring). But a plain relative string already names a subdirectory
in Claude Code (and VS Code) and resolves inside the marketplace checkout, which is the behaviour a
same-repo marketplace wants. For Codex, `{"source": "local", "path": "./<dir>"}` is the probable
equivalent: the generator already uses `local` with `"./"` for root plugins. It has not been
exercised for a subdirectory.

- Does Codex accept `{"source": "local", "path": "./plugins/<x>"}` in a marketplace added from a git URL, a branch and a local path? This is the one live check the fix depends on. See the architecture report.
- Is there any case where a same-repo marketplace *should* pin to the upstream URL? (Hub mode is different: hub catalogues list other repos and legitimately need `url`, but the generator writes no marketplace in hub mode.)
- Should `check_plugin.py` warn when a local marketplace's `git-subdir` `url` equals the plugin's own `repository`, so repos spawned with ≤1.0.1 are told to repair? `merge_marketplace` never rewrites existing entries, so regeneration will not fix them.

## Scope Boundary

This report authorizes changes to `skills/spawning-agent-plugins/` in Pinion (generator, checker, references, evals)
only. It does not authorize editing any downstream repository (`mcp-biomodelling-servers`, `MCP_Hackaton`)
or the published `CrackingShells/Nest` catalogue.
