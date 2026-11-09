# Plugin and README wiring

**Goal**: Package `designing-tests` as a plugin listed by the Nest hub, the same way as its siblings, and list it in the README.
**Pre-conditions**:
- [ ] Both review leaves are `done`; work happens on `claude/test-design-skill-03d1cc` itself (the coordinator does this level)
- [ ] `git status --porcelain plugins/ plugin.spec.json README.md` is empty
**Success Gates**:
- ⬜ `uv run skills/spawning-agent-plugins/scripts/check_plugin.py --root . --spec plugin.spec.json` reports no problems
- ⬜ The other plugins' files are unchanged after spawning and assembling
- ⬜ `README.md` lists `designing-tests` in the tagline, the intro sentence and the Skills table
**References**: [R01 "Repository wiring"](../../../../__reports__/designing_tests/00-architecture_designing_tests_v0.md) — the spec entry and the commands

## Step 1: Plugin
**Goal**: Generate and assemble the plugin from the spec.
**Implementation Logic**:
Add the `plugins[]` entry of R01 "Repository wiring" to `plugin.spec.json`, copying the shape of the existing entries. Run `uv run skills/spawning-agent-plugins/scripts/spawn_plugin.py spawn --spec plugin.spec.json` (with `--force` only if it refuses on existing files, then confirm the other plugins show no diff), `uv run tools/assemble_plugin.py designing-tests`, `uv run tools/package_skill.py skills/designing-tests dist/` as the validator (delete `dist/` output afterwards if it is not ignored), and `check_plugin.py`. These run by hand because the pre-commit hook is not active in worktrees.
**Deliverables**: `plugin.spec.json` (new `plugins[]` entry `plugins/designing-tests`); `plugins/designing-tests/` (generated manifests and the assembled skill copy)
**Consistency Checks**: `uv run skills/spawning-agent-plugins/scripts/check_plugin.py --root . --spec plugin.spec.json && git diff --quiet HEAD -- plugins/ ':!plugins/designing-tests'` (expected: PASS)
**Commit**: `build(plugin): package designing-tests as a plugin listed by the Nest hub`

## Step 2: README
**Goal**: List the skill where readers look.
**Implementation Logic**:
Extend the tagline and the intro sentence to name test design, and add a Skills table row in the same voice as the others: what it does, when it loads.
**Deliverables**: `README.md` (tagline, intro sentence, Skills table row for `designing-tests`)
**Consistency Checks**: `grep -q 'designing-tests' README.md` (expected: PASS)
**Commit**: `docs(readme): list the designing-tests skill`
