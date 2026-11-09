# designing-tests — Contamination review (v0)

Date: 2026-11-09. A read-only review of `skills/designing-tests/` at `70c8c3e`. It looked for text that would pollute a cold reader's context. Every file a reader could load was read in full, including the script's help and error text, and `evals/`. The review checked five classes:

1. meta-discourse about the skill;
2. leaks of the authoring context;
3. references outside the skill;
4. slips that address a specific human;
5. time-sensitive or environment-specific statements.

There were no leaks of people, sessions, roadmap history or earlier versions anywhere. Nothing names another skill, plugin or organisation. The only URLs are citations.

## Findings and decisions

| # | Where | Finding | Decision |
|---|---|---|---|
| F1 | `science-data.md` (`contract_version`); the schema's top `description` | "A breaking change … is a breaking release of the skill": release mechanics the reader does not act on | accept: dropped. The rule the reader uses, that a manifest for another version is rejected, stays |
| F2 | `software-roles-and-scope.md` intro; `science-showing-and-explaining.md` "Explaining the design"; `science-questions-and-tests.md` "Roles in science"; `science-analysis-plan.md` intro | The skill describes its own purpose ("the failures this skill exists to prevent", "The skill owes an explanation", "roles of the skill", "There is no template") | accept: rewritten as instructions to the reader |
| F3 | `software-false-safety.md` and `software-planning.md` intros; "this page" and "the list above" in three software references | Remarks on the page's own structure. Two intro sentences only repeated the Contents list | accept: the two intro sentences are deleted, and the three closing prompts now address the case ("no cell names", "none of these covers", "not named here"). The science closing questions ("not on this page") are kept: each is an instruction to look past the sample |
| F4 | `science-test-landscape.md`, 18 tags | "(abstract-level claim)" records what the author read, not what the reader should do | accept, rewrite A: the tag is now "(abstract only)", and one sentence in "How to use this map" tells the reader to open the paper before relying on details the abstract does not give |
| F5 | the four software references | "we own", "our code": the authors speaking as themselves | accept: "the project owns", "the project's code" |
| F6 | `.releaserc.js`, `package.json` | Release plumbing in the skill directory; `.releaserc.js` names a path outside it | reject here: every skill in the repository has both files, and `plugin.spec.json` reads the version from `package.json`. The assembled plugin copy excludes both files, as well as `evals/`. The `.skill` archive from `package_skill.py` excludes `package.json` but still ships `.releaserc.js`, as it does for every skill in the repository. That is a tooling fix outside this skill |
| F7 | `evals/test_study_contract.py` docstring | Run commands written from the repository root; a remark on packaging | accept: commands now run from the skill directory (checked: 79 passed from there), and the packaging remark is deleted |

**Kept on judgement.** "Parent agent" and "dispatch an agent" tell the reader whom to ask about an assumption, and `agreed_by` must name a real party. Fixture dates are test data, not claims about time.

**Rerun after the fixes.**
- `quick_validate`: valid.
- Guards: 79 passed, both from the repository root and from the skill directory.
- Narrowed banned-word check: clean.
- No first-person "we", "our" or "us" is left in the software references.
- No "abstract-level", "this skill" or "of the skill" is left in the references or assets.
