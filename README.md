# Pinion

[![License](https://img.shields.io/badge/license-AGPL--3.0-blue.svg)](LICENSE)

Agent skills for the mechanics of agents themselves: how they are packaged, installed, and kept from leaving stray processes behind.

A pinion is a bird's outer wing, the feathers that drive its flight, and also the small gear that drives a machine. These skills cover the agent's own working parts, not the task it is working on: turning a repository into installable plugins, and waiting on long-running work without hanging or missing a crash. Pinion is part of the Cracking Shells family of repositories, alongside [Nest](https://github.com/CrackingShells/Nest), the org's plugin marketplace.

## Skills

| Skill | What it does |
|:------|:-------------|
| [`spawning-agent-plugins`](skills/spawning-agent-plugins/SKILL.md) | Turns a repository's skills, MCP server or hooks into plugins that Claude Code, Codex and Agent Plugins 1.0 clients can install from GitHub, generated from one spec and checked for drift that no loader reports. |
| [`waiting-on-processes`](skills/waiting-on-processes/SKILL.md) | Writes waits and watches in Claude Code that end by themselves and catch failures, for servers, builds, test runs, cluster jobs, CI checks and log lines, with a scheduled sweep that stops stray processes. |

## Installation

`spawning-agent-plugins` is listed in the [Nest](https://github.com/CrackingShells/Nest) marketplace; that entry still installs from [cracking-shells-playbook](https://github.com/CrackingShells/cracking-shells-playbook), where the skill was first released, until Pinion publishes its own plugins.

To install a skill from this repository now, copy its directory into your skills folder:

```bash
git clone https://github.com/CrackingShells/Pinion.git
cp -R Pinion/skills/<skill-name> ~/.claude/skills/
```

Copy into `.claude/skills/` inside a repository instead to make the skill available in that project only. Restart Claude Code for the new skill to load.

`spawning-agent-plugins` moved here from cracking-shells-playbook with its history and release tags.

## Contributing

Questions and suggestions go to the [issue tracker](https://github.com/CrackingShells/Pinion/issues).

## License

AGPL-3.0. See [LICENSE](LICENSE).
