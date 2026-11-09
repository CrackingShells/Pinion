# designing-tests — Architecture (v0)

Date: 2026-11-09. Approved by Eliott after two review rounds; this is the plan as approved.
Eliott's own words, which every leaf must stay faithful to, are quoted in the [appendix](#appendix-eliotts-words-verbatim).

## What changed after your review

| Your comment | Change |
|---|---|
| Keeping the right things is not enough: what matters is making them visible to the agent | A new section, "How the skill makes its constraints visible", now drives the layout |
| "Invariant" is the wrong word | Guards now check an *expected behavior*: a transformation or operation the software is relied on to perform, in its current context |
| Not always an estimand; often a set of tests | The chain is now research question → hypotheses → computable statistical questions → a coherent battery of tests, at whatever granularity the topic needs. Estimand and SESOI are used where they apply |
| "Deviation" is pejorative | It is now the **evolution log** |
| A statistical test lives as long as its question | Accepted. That removes my main objection to sharing the roles, and the recommendation flips (§3) |
| Regression guards can overfit to individual bugs | A bug now leads to the *behavior* that lacked a guard, not to one test per bug (§4) |
| The tautology catalog sets the tone | It becomes the illustration of a principle, with a mirror catalog for statistics (§4, §5) |
| Explain pedagogically | New output contract: every design is explained to its recipient, the human in chat or the agent in the hand-off report (§6) |
| Discuss the guesses | New rule: assumptions that drive the design are agreed with the user, the parent agent or a dispatched agent, and the plan records who agreed (§5) |
| Data dictionary as assets; a versioned contract | Added: a JSON Schema study contract, versioned with the skill, plus an example dictionary (§7) |
| Take inspiration from dataviz | Adopted its shape: a procedure in order, non-negotiables, failure catalogs to check against, and "the computable part, compute it" (§2) |
| No template for the analysis plan | Both planning artifacts are now defined by *categories* (what each must establish), in the style of the writing-reports references (§6). No template files |
| Checklists can stop the model from thinking about unlisted cases | A "visible, but not a checklist" rule for the prose: gates ask about the principle, catalogs say they are samples, few absolutes, and a verifier checks for this (§2) |
| Complete the list of tests? Validity conditions must be proved | Both. A dedicated research leaf maps less well-known methods (LASSO with post-selection inference, GEE, survival, compositional data, Bayesian, …). The map opens by inviting the model's own knowledge, as long as it is confirmed by a search. Every test's validity conditions are checked and the evidence is recorded (§5.3) |
| Frontmatter features | §1b: portable fields only. Version stamping goes to three separate sessions |
| Anthropic's best-practices guide | §1c: its rules are adopted and carried into every brief |
| Code is fine if it is not a gadget | The script now has one stated problem: whether a dataset can be swapped under a battery of tests. Its leaf applies the skill's own method to the script (§7) |

## Context

Test planning in the org lives today in `writing-reports` as the "test-definition" report type.
Eliott has decided it becomes a standalone Pinion skill covering two meanings of "test":

- **software tests**: which tests deserve to exist, and how to write them;
- **scientific tests**: statistical tests designed together with the experiments that feed them.

The software half must make his recurring prompt unnecessary, at any application size and without
count targets. That prompt names three failures:

- suites that grow without being useful;
- tautological tests that give false safety;
- confusion between the transient tests that help build blocks and the guards of the design's
  cornerstones.

The scientific half must give the method he repeats to every research agent:

- the questions;
- the test choice, with reasons for it and against the alternatives;
- the null hypothesis;
- the protocol, co-designed with the tests;
- the sample size;
- the cohort and its budget;
- a consistent data format;
- results that are visible whether they are good or bad.

**Constraints:**

- The skill stands alone and names no other skill.
- It loads alongside roadmap and implementation planning through its own description.
- Planning documents go where the project already keeps such documents.
- No auto-memory writes.

**Kept from the current reference:**

- start from risk, not from functions;
- test what we own;
- observable behavior over internals;
- the ownership check;
- equivalence classes, boundaries, pairwise and parameterization;
- the self-review loop;
- trust boundaries;
- a must-run set.

**Dropped:**

- the size table;
- the Development / Regression / Integration tiers;
- the `__reports__/` naming.

## 1. Name: `designing-tests`

It is a gerund plus an object, like its siblings, and "test design" is the established term in both
fields.

## 1b. Frontmatter: the portable set only (agreed)

The frontmatter uses only fields from the Agent Skills spec, which every harness accepts and
`tools/quick_validate.py` allows: `name`, `description`, `license`, `compatibility`, `metadata` and
`allowed-tools`. No Claude Code-only keys.

```yaml
name: designing-tests
description: …                        # ≤1024 chars, third person, no angle brackets
license: AGPL-3.0-or-later            # a .skill file travels without the repository's LICENSE
compatibility: Only scripts/study_contract.py needs uv, or Python 3.9+ with jsonschema; the method itself needs nothing.
allowed-tools: Bash(uv run *study_contract.py*)
```

`metadata.version` is not written by hand. The release-stamping fix, running in its own sessions
(see below), will put it there when the skill is released.

**Release stamping:** three sessions, one each for Playbook, Plumage and Pinion. Each makes the
release step stamp `metadata.version` into SKILL.md, because packaging excludes `package.json` and
an installed `.skill` does not know its own version today. They are independent of this plan.

Each session will:

- extend `tools/set_plugin_version.py` to write the version into SKILL.md, quoted as a string;
- move that step ahead of `package_skill.py` in `release-config.js`;
- add `SKILL.md` to the files the `@semantic-release/git` commit includes;
- show the change works with a dry run, without cutting a release;
- commit with no push.

The Playbook's `tools/` change is the reference copy, and each session reports its diff so the
three can be matched.

## 1c. Authoring rules from Anthropic's skill best practices

These are applied in addition to skill-creator's guidance, and every implementer brief carries
them. (Source: platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices.)

- **References sit one level deep.** Every reference file is linked directly from `SKILL.md`'s
  reference map. A reference may point to a sibling, but that link is never the only way to reach
  the sibling, because an agent may read a file reached through another reference only partially.
- **A table of contents for any reference over 100 lines.** This replaces my earlier threshold of
  300 lines.
- **Concise for the agent, pedagogical for the human.** The skill does not explain to the agent
  what a strong model already knows: what a p-value is, what TDD is. It spends its words on the
  judgement calls and the traps. The pedagogy goes in the *explanation contract*, which the agent
  owes to whoever ordered the design (§6). The pedagogy is not the skill's own prose.
- **Degrees of freedom fit the task.** Choosing a guard or a test is judgement, so it gets high
  freedom: prose, principles and gates. Checking a dataset against its contract is fragile, so it
  gets low freedom: run exactly `study_contract.py check`.
- **A default, then the escape hatches.** Each family in the test landscape names the usual choice
  first, then the alternatives, each with the property that would make it the better fit. This is
  how "not a menu" stays usable.
- **One term per concept.** The vocabulary in the roadmap sketch is fixed, and the consistency
  verifier greps for synonyms.
- **No time-sensitive statements; forward-slash paths; descriptive file names.**
- **Scripts solve problems rather than defer them.** That means:
  - errors are explicit and verbose, naming what was expected and what is available (for example
    "column `dose_mg` not in dictionary; dictionary has: dose, …");
  - no unexplained constants;
  - required packages are declared in the PEP 723 header and in `compatibility`;
  - `SKILL.md` says plainly whether to *run* a script or *read* it.
- **Feedback loops on critical steps.** The study contract is used as validate → fix → repeat, and
  the battery is not run on a dataset until `check` passes. This is the guide's
  plan-validate-execute pattern.
- **Read the skill as a fresh agent, in place of evals (you ruled evals out).** The consistency
  verifier reads `SKILL.md` cold and reports:
  - where it would have stopped;
  - which references it would never have opened;
  - where a weaker model would need more guidance.

## 2. How the skill makes its constraints visible

The principles above are only useful if the agent meets each one at the moment it would break it.
The structure does that in five ways, borrowing dataviz's shape:

1. **The procedure comes in order.** For each half, `SKILL.md` lists the steps in the order they
   are done. Every step ends with a **gate**: one line the agent can check, which names the
   reference that explains it. Example: "Gate: every planned guard names the bug it would catch →
   `software-false-safety.md`". The constraint appears where it bites, not in a principles section
   read once.
2. **Non-negotiables** are a short list in `SKILL.md`, each with the signal that shows it is being
   broken. Example: "no count targets: if you are about to write 'N tests for this', you are
   counting instead of naming behaviors".
3. **Failure catalogs to check against**, one per half (`software-false-safety.md`,
   `science-false-safety.md`). Each opens with the principle and then gives the catalog as worked
   illustrations, so that the agent learns what "tautological" means rather than pattern-matching a
   list.
4. **The computable part is computed.** Whether a dataset matches the contract that its tests were
   written against is checkable, so a script checks it instead of the agent eyeballing it (§7).
   Judgement (which test, which guard) stays in prose, never in templates.
5. **References are named for the moment of use** (planning, writing, choosing, sizing, showing),
   so the reference map in `SKILL.md` reads as "where you are → what to open".

**Balance: visible, but not a checklist.** A list enforced as a checklist hurts quality. The agent
ticks the listed cases, then stops thinking about the ones nobody listed. The prose guards against
that in four ways:

- **Gates are questions about the principle, not boxes about instances.** For example: "could a
  plausible wrong implementation pass this test?" rather than "not a mock echo".
- **Every catalog and table says it is a sample.** It opens by stating the principle and ends by
  asking the agent to look for the case the list does not name. The writing explains *why* each
  entry fails, so the reason transfers to new cases.
- **Few absolute rules.** Non-negotiables are kept to the few that really are absolute. Everything
  else is judgement, with its reason given.
- **The verifiers check this.** The consistency verifier reads each catalog as an agent would, and
  flags any place where the prose invites stopping at the list.

## 3. The roles: shared across both halves (recommendation flipped)

My argument against sharing rested on lifetime: a statistical test runs once. You corrected that: a
statistical test lives as long as its research question is relevant, and the datasets it runs on
can be swapped. With that correction the lens transfers, and so do all three concerns of your
prompt:

| Your concern | Software | Science |
|---|---|---|
| Suites grow without being useful | Maintenance cost, slow suites | **Multiplicity**: each extra test costs power or inflates false positives. In science, test explosion has a measurable price |
| Tautological tests give false safety | Mirror tests, mock echoes | Tests whose result is **fixed by construction**: circular analysis (select on the outcome, then test it), testing baseline balance after randomization, testing a difference created by a threshold or a normalization |
| Transient tests versus cornerstone tests | Confirm and probe versus guard | Pilot, exploratory and pipeline checks versus the battery that answers the research question |

**Mapping in science:**

- **Guard:** the battery of statistical tests attached to a research question, specified before the
  data, rerun on every dataset swapped in while the question stands, together with its
  calibration on known truth.
- **Confirm:** the known-truth checks of each analysis step while the pipeline is being built (does
  step k recover the effect planted in toy data?). They are culled once the guard battery is
  calibrated.
- **Probe:** pilots and exploratory analyses. They answer questions such as the variance, the
  feasibility, or which measure is more precise. They feed decisions and never confirm.

**What still does not map, stated in the skill:**

- Experimental controls (positive and negative) are *not* confirms. They belong to the protocol and
  the data, and are kept and reported.
- The established words stay: the skill always pairs a role with the field's own term ("probe:
  exploratory analysis"), and never replaces it.

The roles are therefore defined once in `SKILL.md` by purpose → lifetime → weight of evidence, and
each half specializes them. If you are still not convinced, the fallback is cheap: the root loses
the shared definition and the science references use exploratory and confirmatory alone.

## 4. Software method (role × scope)

**Roles.** Purpose sets lifetime and where the test lives:

| Role | Purpose | Lives | Where |
|---|---|---|---|
| Guard | Defines an expected behavior of the software: a transformation or operation it is relied on to perform in its context, including the design cornerstones the rest builds on. Written first in TDD | Until that behavior is deliberately changed | In the suite |
| Confirm | Checks that a step toward a guard did what was meant | Until the step is done and the guard covers it | In the suite while work is in progress, marked by the project's own means (marker, name, tag) so culling is mechanical |
| Probe | Answers a question during the work | Until it is answered | Outside the suite; the answer goes where decisions are recorded |

**Scope** stays unit / integration / end-to-end, and sets cost, speed, failure localization and
fixtures. How the axes compose:

- A guard's scope is where its behavior is observable to the consumer that relies on it, never the
  most convenient one. The guard goes through that consumer's interface, so it survives refactors.
- Confirms sit near the block being built and may touch internals, because they are transient.
- Probes take whatever scope their question needs.

A 3×3 matrix gives each cell a typical use and a typical mistake. For example: "an e2e confirm:
usually a missing guard"; "a guard on a private helper: a confirm that was never culled".

**Lifecycle.**

- **Probe:** its answer is recorded, then the test is deleted. If the design comes to rely on what
  the probe found about code we do not own, the probe becomes a boundary guard.
- **Confirm:** deleted when its guard passes. It is promoted only if it encodes a behavior worth
  guarding, and is then rewritten to guard standards.

**Which guards exist (in place of count targets):**

- Candidates come from the behaviors consumers rely on, the design's cornerstones, and the seams
  with code we do not own.
- **Distinct-failure rule:** a second test on the same behavior must catch a plausible bug the
  first misses.
- Equivalence classes, boundaries, pairwise and parameterization are kept from the current
  reference.

**Bugs go to behaviors, not to tests** (your overfitting point):

1. A bug means a behavior had no guard, or a weak one.
2. Reproduce the bug as a *confirm* for the fix step.
3. Then strengthen or add the guard *for the behavior*, so that it covers the class of bug.
4. The reproduction joins that guard only if it is a distinct equivalence class.
5. A suite that grows one test per incident is the signal to look for the missing architectural
   guard.

**False safety (`software-false-safety.md`):**

- **The principle:** a test is tautological when no plausible wrong implementation makes it fail,
  or when it restates its own input. It is trivial when its failure would change no decision.
- **The catalog, as illustrations of that principle:**
  - mirror tests;
  - mock echoes;
  - set-then-get tests;
  - shape-only or not-None assertions;
  - unreviewed snapshots;
  - framework self-tests;
  - assertion-free runs;
  - tests never seen failing.
- **Signs of explosion:**
  - tests enumerated per function or branch;
  - permutations that probe no distinct behavior;
  - one test per incident;
  - code:test ratios used as a goal.
- **The detector is the mutation check:** name a plausible bug, or inject one (invert a condition,
  return a constant), and see red. The ownership check is a special case of it. Mutation tools are
  optional.
- **The self-review loop is role-aware:**
  - each guard states its behavior, its scope with the reason, and the bug it catches;
  - each confirm names the guard it serves;
  - each probe names its question and the decision it feeds.

**Writing (`software-writing.md`):**

- The name states the behavior.
- Expected values are derived independently: by hand, from an oracle, or as a property.
- No logic in tests.
- One behavior per test.
- Failure messages name what broke.
- Use the real thing at boundaries we own; mock what we do not own.
- Tests are deterministic.
- Confirms are marked, and culled at the end of the task.

**Planning integration (`software-planning.md`):**

- When planning a feature, an implementation or a roadmap, each task names the guards it introduces
  (behavior, scope, the failure it catches), written first.
- Probes are their own steps, each with a question and a decision.
- Confirms are not enumerated.
- Done-criteria: each guard has been seen failing, and confirms are culled or promoted.
- A bug fix's plan is one line.

## 5. Scientific method (co-developed, in order)

1. **Questions.**
   - Research questions → hypotheses → the computable statistical questions that, together, answer
     them. The granularity is whatever the topic needs, from one test to a coherent battery.
   - The plan argues *why that battery suffices*, with a pattern-of-outcomes table saying which
     pattern counts as support, as evidence against, or as inconclusive.
   - Estimand and SESOI are used where an effect size is meaningful.
   - Exploratory questions are labelled as probes.
2. **Hypotheses.**
   - H0 and H1 for each statistical question, with one- versus two-sided justified.
   - When the claim is "no difference", flip to equivalence or non-inferiority (TOST).
   - Multiplicity is handled across the battery, as a design choice and not an afterthought.
3. **Test choice with reasons, and validity proved.**
   - **Format:** the chosen test, its nearest alternatives with the property of *this* situation
     that rules each out, then its **validity conditions**, each one checked with recorded evidence,
     and the fallback if a condition fails.
   - **What drives the choice:** the question type, the data dependence (paired, repeated, nested;
     pseudoreplication), the outcome type, the factors and covariates, and n.
   - **Validity is proved, not assumed.** Every test has conditions under which its error rates
     hold. Examples:
     - the approximate normality of the sampling distribution that Welch relies on, which is
       usually argued from n and the shape of the data;
     - the minimum expected cell counts for χ²;
     - exchangeability under the null for a permutation test;
     - the events per variable for logistic and Cox models;
     - proportional hazards;
     - sphericity;
     - independence of the units.

     For each condition, the plan records how it was checked and what the check showed: an argument
     from the design, a diagnostic, a simulation of robustness, or a cited result. The explanation
     to the recipient repeats it. Checking a condition with a significance test on the same data
     (normality tests used as gatekeepers) is itself listed as false safety; the reference says why
     and gives the better checks.
   - **Not a checklist; the model's own knowledge is invited.** The reference opens by saying that
     its map is a sample of methods, not a menu. If the agent knows a method that fits the situation
     better, it should use it, after confirming the method's validity conditions with a web or
     paper search and citing what it read. A method chosen from memory without that check is not
     acceptable. The map is organized around the *properties that discriminate between methods*, so
     the agent learns to choose rather than to look up.
   - **Breadth comes from a dedicated research leaf** (`test_landscape`, below). It compiles a
     situation-family map that goes past the textbook core. Its scope:
     - families: location and scale, proportions and contingency, association and agreement,
       regression and GLM (including ordinal, count and zero-inflated), mixed and GEE models,
       survival, time series and autocorrelation, circular and compositional data, high-dimensional
       data;
     - high-dimensional data in particular: LASSO and elastic net, with the warning that inference
       after selection needs selective inference or sample splitting;
     - equivalence;
     - Bayesian alternatives (Bayes factors, posterior intervals);
     - multiple testing (Holm, BH, hierarchical gating);
     - meta-analysis;
     - ML and benchmark comparisons (pairing by seed or fold, the corrected resampled t-test,
       McNemar, Demšar-style multi-dataset comparison).

     Each entry gives:
     - when the method fits;
     - what distinguishes it from its neighbours;
     - its validity conditions and how to check them;
     - a primary source.

     The core corrections stay explicit, for example that Mann-Whitney tests stochastic dominance,
     not medians.
4. **Protocol co-design.**
   - Each protocol decision changes which test is valid: pairing, blocking, randomization,
     blinding, biological versus technical replicates.
   - Controls are part of the protocol.
   - Iterate between protocol and analysis until they agree.
5. **See the battery fail on known truth.** Simulate data in the contract's schema under H0 and
   under the effect that matters. Run the real pipeline and check the false-positive rate and the
   power. This also debugs the pipeline before any data are collected.
6. **Sample size.**
   - Power from the SESOI or a stated meaningful effect, never from a pilot's observed effect.
   - Variance from a pilot or the literature.
   - Analytic formulas where they exist, simulation otherwise.
   - Account for the design effect and attrition.
   - Give a sensitivity curve.
   - Under a fixed budget, report the minimum detectable effect.
   - No post-hoc power.
   - **Agreeing the guesses:** the assumptions that drive n and the budget (variance, meaningful
     effect, attrition, unit cost) are never guessed alone. The agent asks the user, asks its parent
     agent, or dispatches an agent to search the literature. The plan records each assumption, its
     source, and who agreed it.
7. **Cohort and budget.**
   - Inclusion and exclusion rules; stratification and matching; allocation.
   - Cost = unit cost × n × attrition margin.
   - When the study is unaffordable, the levers in order: reduce variance; then revise the
     meaningful effect, openly and agreed; then downgrade to exploratory.
8. **Data.** Every dataset conforms to the study contract (§7), so datasets can be swapped under the
   same battery.
9. **Showing results** (visibility guidelines, not plot types; dataviz-style procedure and
   non-negotiables):
   - Every unit is shown behind the estimate.
   - The effect is plotted with its uncertainty, against the lines that decide it (zero, the
     meaningful effect), so an inconclusive result *looks* inconclusive.
   - The primary figures are pre-specified and rendered first on the H0 and effect simulations, so
     everyone knows what null and hit look like.
   - Every pre-specified outcome is shown, nulls included.
   - Axes are shared across panels.
   - The nesting is visible.
   - Exploratory results are labelled in the figure.

**Statistical false safety (`science-false-safety.md`)** mirrors the software catalog:

- tests fixed by construction;
- forking paths;
- the pilot's effect used to power the study;
- post-hoc power;
- pseudoreplication;
- normality tests used as gatekeepers;
- "not significant" reported as "no effect";
- p-values reported without effect sizes;
- selective figures.

## 6. Output contracts: planning artifacts and explanation

**Planning artifacts** are defined by *categories* (what each must establish), in the style of the
writing-reports references. Agents are trusted to write them, so there are no template files.

- **Software test plan:**
  - what must keep working: the guards, each with its behavior, scope and the failure it catches;
  - open questions: the probes, each with its decision;
  - trust boundaries and fixtures;
  - what was deliberately *not* tested, and why (restraint made visible);
  - done-criteria.
- **Analysis plan:**
  - research questions and hypotheses;
  - from questions to the battery, with the pattern-of-outcomes table;
  - test choices with alternatives considered;
  - validity conditions, each with the evidence that it was checked;
  - protocol and cohort;
  - sample size and its assumptions, with who agreed them;
  - the known-truth validation;
  - the data contract;
  - the planned figures;
  - the evolution log.
- **Location:** the project's own convention (its plan or docs folder, a roadmap task, a PR
  description). Otherwise inline in the plan being written, or ask. A separate file only when the
  work is big enough to need one.

**Explaining the design (non-negotiable for science, recommended for software).** Whoever ordered
the design gets it explained: the human in the chat, or the agent in the hand-off report. For each
choice, the explanation says:

- what was chosen;
- why it fits this situation;
- why the alternatives do not;
- which assumptions it rests on, and who agreed them;
- what each possible outcome would mean.

It is written in plain terms, with each term defined at first use. An expert-level summary of the
results alone is not enough, because statistical choices and their justifications are widely
misunderstood.

## 7. Code: the study contract (constrained generation, one stated problem)

**Problem it solves:**

- Tests attached to a research question outlive any one dataset, and new cohorts, reruns and
  simulations get swapped in.
- Today each agent saves data its own way, so nobody can tell whether a dataset can be fed to an
  existing battery, or whether two studies are comparable.
- The contract makes the shape of the data checkable. The script checks it, and does nothing else:
  it chooses no test and runs no analysis.

**Files:**

- **`assets/study-contract.schema.json`:** a JSON Schema for a study manifest.
  - Fields: `contract_version`; the study; the research and statistical question ids; the protocol
    version; and the datasets, each with path, format, origin (`simulated-null`,
    `simulated-effect`, `pilot`, `real`), data dictionary and provenance (code commit, seeds,
    instrument, dates). Also the evolution log.
  - `contract_version` lives in the schema's `$id`, and a breaking schema change ships as a breaking
    release of the skill. Contract and skill versions therefore move together.
- **`assets/data-dictionary.example.json`:** a filled example of a dictionary. Each variable has:
  - name, type and units (or an explicit `unitless`);
  - allowed values or range;
  - missing codes;
  - role (id, factor, outcome, covariate);
  - description.
- **`scripts/study_contract.py`:** PEP 723 header (`jsonschema`), run with `uv run`. Subcommands
  only where a problem asks for one:
  - `init <data.csv…>`: scaffolds a manifest and dictionary from the headers, for the agent to
    complete (constrained generation).
  - `check <manifest.json>`: validates the manifest against the schema, and each CSV or TSV dataset
    against its dictionary. Problems it reports:
    - missing or extra columns;
    - type violations;
    - out-of-set or out-of-range values;
    - undeclared missing codes;
    - duplicate ids;
    - numeric columns without units;
    - contract-version mismatch.
  - `compare <a.json> <b.json>`: says whether datasets or studies are swappable or comparable.
    Reports variables added or removed, changed types, units and ranges, and protocol and contract
    versions.
  - Output is one `RESULT=OK|PROBLEMS n` line (or `SWAPPABLE|DIFFERS n`) plus details. Exit codes
    are 0, 1, and 64 on a bad argument.
- **`evals/test_study_contract.py`:** guards only. They follow the precedent of
  `spawning-agent-plugins/evals/`, and `evals/` is excluded from packaging.

**Not a gadget:** the leaf begins by applying this skill to its own code.

- It writes the script's test plan: the guards for each problem above, each seen failing.
- Every feature must trace to one of the three problems, or it is cut.
- The consistency verifier checks that trace, and attacks the tests for tautologies.

## Skill layout

```
skills/designing-tests/
├── SKILL.md                               shared principles; roles defined once; the two procedures in order with
│                                          gates; non-negotiables; the explanation contract; plan locations; reference map
├── package.json / .releaserc.js           as the siblings (version 0.0.0)
├── references/
│   ├── software-roles-and-scope.md        role × scope matrix, lifecycle, TDD flow
│   ├── software-planning.md               guard sources, distinct-failure, bugs → behaviors, test-plan categories, plan integration
│   ├── software-writing.md                writing each role, marking and culling confirms, fixtures, trust boundaries
│   ├── software-false-safety.md           tautology principle + catalog, explosion signs, mutation check, self-review
│   ├── science-questions-and-tests.md     RQ → hypotheses → statistical questions → battery; roles in science; how to choose
│   │                                      a test and prove its validity; multiplicity
│   ├── science-test-landscape.md          situation-family map: fit, discriminating properties, validity conditions + checks,
│   │                                      sources; opens with "a sample, not a menu" (TOC)
│   ├── science-protocol-and-sample.md     co-design, controls, known-truth runs, power, agreeing assumptions, cohort, budget
│   ├── science-data.md                    the study contract, dictionary, provenance, evolution log, study_contract.py
│   ├── science-showing-and-explaining.md  visibility procedure + non-negotiables; how to explain the design
│   ├── science-false-safety.md            statistical tautologies and false-safety catalog
│   └── science-analysis-plan.md           the analysis plan's categories
├── assets/study-contract.schema.json, assets/data-dictionary.example.json
├── scripts/study_contract.py
└── evals/test_study_contract.py
```

Every reference over 100 lines gets a table of contents. Every reference is linked from
`SKILL.md` (one level deep, §1c). Links go only to the root and between the skill's own files.

**Description** (draft; the gate is ≤1024 characters and no angle brackets, checked by
`tools/quick_validate.py`):

> Designs tests before they are written, in both senses of the word, so each one answers a stated
> question and can fail. Software: decides which tests deserve to exist and writes them, giving each
> a role (probe, confirm or guard) that sets how long it lives, composed with its scope (unit,
> integration, end-to-end), so suites stay small and free of tautological tests that give false
> safety. Science: designs the statistical tests that answer a research question together with the
> experiment that feeds them: hypotheses, why each test fits and its alternatives do not, sample
> size, cohort and budget, a data contract, and figures that show the result whether good or bad.
> Use whenever writing, adding, reviewing or pruning tests, doing TDD or fixing a bug, and whenever
> planning a feature, an implementation or a roadmap, even if tests are not mentioned; also when
> choosing a statistical test, sizing a sample, comparing algorithms or models across noisy runs,
> designing an experiment, or writing an analysis plan.

## Repository wiring (the same as the existing skills)

- **`plugin.spec.json`:** add a `plugins[]` entry:
  - `dir: plugins/designing-tests`
  - `displayName: "Designing Tests"`
  - `version_from: package.json:skills/designing-tests/package.json`
  - `skills: ./skills/`
  - keywords `testing`, `tdd`, `statistics`, `experiment-design`, `agents`
  - codex category `Developer Tools`
- **Generate the manifests:** `spawn_plugin.py spawn --spec plugin.spec.json`, with `--force` if it
  refuses on existing files. Then confirm that the other plugins show no diff.
- **Assemble and check:** `uv run tools/assemble_plugin.py designing-tests`, `uv run
  tools/package_skill.py skills/designing-tests dist/` (validator), and `check_plugin.py --root .
  --spec plugin.spec.json`. These run by hand, because `core.hooksPath` is unset in this worktree;
  shared git config stays untouched.
- **`README.md`:** extend the tagline and the intro sentence, and add a row to the Skills table.
- **Commits:**
  - `docs(roadmap): …` for the roadmap;
  - `feat(designing-tests): …` per content leaf (the first release will be 1.0.0);
  - `build(plugin): package designing-tests as a plugin listed by the Nest hub`;
  - `docs(readme): list the designing-tests skill`.
  Every message ends with the Co-Authored-By line and goes through `-F <file>`.

## Roadmap sketch (`__roadmap__/designing_tests/`, committed)

Depth is ordering; siblings run in parallel.

```
__roadmap__/designing_tests/
├── README.md
├── root_skill.md               L0  SKILL.md (procedures, gates, non-negotiables, roles, explanation contract), package.json, .releaserc.js
├── software_references.md      L0  the four software references                                   [adversarial review]
├── science_method.md           L0  questions-and-tests, protocol-and-sample, showing-and-explaining,
│                                   false-safety, analysis-plan                                      [adversarial review]
├── test_landscape.md           L0  science-test-landscape.md: research leaf (web + arXiv search, every entry sourced)
│                                                                                                    [adversarial review: statistics]
├── study_contract.md           L0  schema, example dictionary, study_contract.py, its guards, science-data.md
│                                   (starts with its own test plan)                                  [adversarial review: gadget + tautology]
└── review/
    ├── README.md
    ├── consistency_review.md   L1  verifier: root ↔ references, terminology, fidelity to Eliott's words, standalone, gadget trace
    ├── statistics_review.md    L1  verifier: statistical correctness of the science references and of the contract's checks
    └── wiring/
        ├── README.md
        └── wiring.md           L2  spec, spawn, assemble, check_plugin, README (the coordinator does this: mechanical)
```

The L0 leaves run in parallel because this plan fixes the file names, the vocabulary (guard,
confirm, probe; unit, integration, end-to-end; research question, statistical question, battery,
SESOI, evolution log, study contract) and the `study_contract.py` interface. L1 catches any drift.

## Execution model (coordinator-led team of subagents)

- **Phase 0 (coordinator):** author the roadmap with `dirtree-rdm init` and `add`, write the leaf
  prose from this plan, and commit it.
- **Implementers:** five Sonnet subagents (`model: "sonnet"`), one per L0 leaf, each in its own
  worktree on `task/designing-tests-<leaf>` from `claude/test-design-skill-03d1cc`. Each brief
  carries:
  - this plan's sections;
  - the sources: the current reference, `waiting-on-processes/SKILL.md` for house style, and the
    writing-reports references for the category style;
  - skill-creator's writing guidance: explain why, use the imperative, keep SKILL.md under 500
    lines;
  - §1c's best-practice rules;
  - Eliott's verbatim prompt;
  - the standalone rule;
  - an instruction to **report spec defects instead of implementing them**;
  - no auto-memory;
  - the colgrep worktree note: index and search with the worktree path as scope; shell `grep -r` is
    blocked;
  - the environment: `uv run`, shared uv cache, no project env;
  - cleanup: remove the worktree after merge.
- **Verifiers:** two Sonnet subagents, each told to assume something is wrong and to name what it
  attacked.
  - **Consistency:**
    - the root matches its references;
    - the role definitions match Eliott's;
    - no count target or ratio has crept back in;
    - "invariant" and "deviation" do not appear;
    - the regression-guard advice does not lead to one test per bug;
    - gates exist at each step;
    - no other skill or repository is named: `grep -riE
      'writing-reports|managing-roadmaps|writing-history|writing-release|plumage|playbook|skill-creator|dataviz|waiting-on-processes|spawning-agent-plugins'`
      → no hits;
    - the script's features trace to its problems, and its tests are not tautological;
    - every reference is linked from `SKILL.md`, and each one over 100 lines has a table of
      contents;
    - each concept has one term;
    - a cold read of `SKILL.md`, as in §1c.
  - **Statistics:**
    - in the landscape, validity conditions that are wrong, missing or uncheckable, and sources that
      do not say what is claimed (spot-check them);
    - places where the prose implies the map is exhaustive;
    - wrong claims;
    - post-hoc power;
    - a missing equivalence path;
    - pseudoreplication;
    - whether the battery and pattern-of-outcomes method holds;
    - whether the contract checks are sound.
  - Fixes go back to the original implementer via `SendMessage`.
- **Integration:** only the coordinator integrates.
  - Rebase each verified branch onto the tip, then `git merge --no-ff -F <file>` with the message
    `Merge task/<leaf> into claude/test-design-skill-03d1cc (<what it adds>)`.
  - Re-check after any conflict; confirm each merge in `git log`.
  - Once each level closes, check the seams between leaves: references named in the root exist,
    terms match, and the contract interface matches its documentation.
- **Mechanical work** (wiring, small fixes) the coordinator does itself.
- **No push, PR or release.**

## Verification

- `uv run tools/quick_validate.py skills/designing-tests` → valid. Description ≤1024 characters,
  SKILL.md under 500 lines.
- `uv run --with pytest --with jsonschema pytest skills/designing-tests/evals/` → passes, and every
  guard was seen failing.
- `uv run skills/designing-tests/scripts/study_contract.py check assets/…example` round-trips; a
  link check finds no broken relative links.
- The standalone grep → no hits.
- `check_plugin.py` passes, and re-assembling all three plugins leaves `git status --porcelain
  plugins/` empty.
- `git diff main --stat` touches only `skills/designing-tests/`, `plugins/designing-tests/`,
  `plugin.spec.json`, `README.md` and `__roadmap__/designing_tests/`.
- The coordinator reads through against the requirement lists in Context and the table at the top.

## Out of scope / follow-ups

- Slimming `writing-reports`' test-definition type (from the playbook session).
- The Nest listing after the first release.
- Push, PR, release.
- Description-trigger optimization.

## Appendix: Eliott's words, verbatim

These are the maintainer's own words from the planning rounds. When a leaf's prose and this appendix
disagree, the appendix wins.

**The prompt this skill must make unnecessary:**

> Given we are doing a large implementation from scratch, the quality of the tests will matter a lot. Even more so they can: 1. very quickly grow in size while not being that useful 2. include tautological tests given us a sense of safety when they are useless. I am also warning you of the difference between tests that are useful within the process of development to check that blocks we are building are behaving as expected; which relevance if often transient and eventually become useless. And the tests that guards cornerstones of the design and features of the software.

**Comments on the plan:**

- Visibility: "The critical point is how to make these conditions and constraints visible to the agent consuming the skill. The organization of the skill folder, its reference files, helper scripts, and assets are criticial."
- Invariant: "Invariant carry the weight of something that never changes. But software changes. What we want to check is an expected transformation or operation that happens to be relevant for the software it is part of given a context for the software."
- Estimand: "Not necessarily about an estimand. We don't always have one. But it is about a hypothesis or a research question for sure. Maybe only a coherent set of statistical tests are capable of answering the research questions. It's not always one unique test. The granularity between the research question and the computable statistical questions if highly variable depending on the topic."
- Deviations: "are logged as "evolution." Deviation is pejorative; we don't know what is good or bad."
- Lifetime: "a statistical test runs as long as the research question it is associated with is relevant and the datasets it runs on can be swapped."
- Regression guards: "be careful not to fall into the rabbit hole of enumerating all individual problems and implement individual solutions instead of architecturally and scalable ones. Don't overfit to a usecase."
- Tautology catalog: "these sets the tone for a broader awareness of what is tautological or not; what is truly needed or trivial."
- Pedagogy: "it would be nice, whichever agent it is that ordered this analysis, to always re-explain pedagogically the content in the chat (if human) or the hand-off report (if other agent) because average stat level and the justification are, in fact, badly understood in the scientific community. So it will be good to explain the choices made and not only present the results or expert-level reports."
- Guesses: "Probably discuss the guesses with other agents (dispatch, ask parent agent, ask the user, etc...)."
- Templates and code: "This is typically the type of templates that will bias agents in a direction instead of letting them apply a relevant method. I strongly recommend using code for constrained generation; but not for that purpose. Constrained generation to help the agent run things similarly, but not for putting it in a box and making it hard for it to escape."
- Analysis plan: "we should trust how "smart" the language models have become. We can rely on them based on the categories."
- Code: "I am okay with shipping code, but I want to make this doesn't become a gadget and truly solves a problem --> This is, in a way, worth applying the purpose of this same skill to its code."
- Checklists: "enforcing these as checklist can also hurt the quality. The prose must find the balance between listing them and still stimulating the inference engine of the language models to not limit themselves to that list and be stubborn about that and ignore other edge cases that might not have been listed."
- Test choice: "if the Language Models remembers from its training a stat test that would fit a given experiment better then it can do web and paper searches to confirm it. by the way, most of these tests have very specific usage validity conditions. These must always be checked and proved to have been checked."
