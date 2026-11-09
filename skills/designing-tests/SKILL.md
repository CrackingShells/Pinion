---
name: designing-tests
description: Designs tests before they are written, in both senses of the word, so each one answers a stated question and can fail. Software - decides which tests deserve to exist and writes them, giving each a role (probe, confirm or guard) that sets how long it lives, composed with its scope (unit, integration, end-to-end), so suites stay small and free of tautological tests that give false safety. Science - designs the statistical tests that answer a research question together with the experiment that feeds them, covering hypotheses, why each test fits and its alternatives do not, sample size, cohort and budget, a study contract, and figures that show the result whether good or bad. Use whenever writing, adding, reviewing or pruning tests, doing TDD or fixing a bug, and whenever planning a feature, an implementation or a roadmap, even if tests are not mentioned; also when choosing a statistical test, sizing a sample, comparing algorithms or models across noisy runs, designing an experiment, or writing an analysis plan.
license: AGPL-3.0-or-later
compatibility: Only scripts/study_contract.py needs uv, or Python 3.9+ with jsonschema 4 or later; the method itself needs nothing.
allowed-tools: Bash(uv run *study_contract.py*)
---

# Designing tests

A test exists to answer a stated question, and it must be able to fail: a test that no plausible
wrong outcome can turn red answers nothing and only lends false confidence. "Test" has two meanings
here and one discipline behind both:

- **software test**: asks whether the software still performs what it is relied on to perform;
- **statistical test**: asks whether the data support a research question, and belongs to the
  experiment that produces the data, so it is designed with it, before the data exist.

Paths such as `references/...` and `scripts/...` are relative to this skill's base directory.

## The three roles

Every test, in either sense, has one of three roles. The role is decided by purpose; purpose sets
lifetime; lifetime sets how much weight the result carries.

| Role | Purpose | Lives | Weight of evidence |
|---|---|---|---|
| **guard** | Defines an expected behavior (a transformation or operation the software is relied on to perform, in its context) or, in science, the battery attached to a research question | Until the behavior is deliberately changed; until the question stops being relevant | Carries the claim: its result is the evidence |
| **confirm** | Checks that one step toward a guard did what was meant | Until the step is done and a guard covers it; then culled | Local reassurance only, never the claim |
| **probe** | Answers a question that decides how to proceed | Until it is answered; the answer is recorded, the test is not kept | Informs a decision, never confirms anything |

In science the same roles read, always alongside the field's own term:

- guard: the **battery** of confirmatory statistical tests for a research question, written before
  the data and rerun on each dataset swapped in while the question stands, together with its
  known-truth run (the end-to-end simulation of the whole battery);
- confirm: the **known-truth check** of one analysis step while the pipeline is built (does it
  recover the effect planted in toy data?), culled once the known-truth run passes;
- probe: **exploratory analysis or pilot**, which feeds decisions (variance, feasibility, which
  measure is more precise) and never confirms.

Two limits of the mapping. Experimental controls, positive and negative, are not confirms: they
belong to the protocol and the data, and are kept and reported. And never replace the field's
term by the role name; write "probe: exploratory analysis" so each reader recognises their own word.

Scope (unit, integration, end-to-end) is a separate axis in software and is about cost, speed and
where a failure localises.

## Software procedure

Use it when writing, reviewing or planning tests, doing TDD, or fixing a bug. Do the steps in order.
When only planning (a feature, an implementation, a roadmap), steps 1 to 3 apply, and steps 4 to 6
become the plan's done-criteria. A software plan names the guards (behavior, scope, the failure each
catches), the probes (question and decision), the trust boundaries, what was deliberately not tested
and why, and the done-criteria.

1. **Name the expected behaviors and who relies on them.** Start from risk and from consumers, the
   design's cornerstones and the seams with code you do not own, never from a list of functions.
   Gate: can you say, for each behavior, who would be hurt if it broke? →
   `references/software-planning.md`, `references/software-roles-and-scope.md`
2. **Choose each guard's scope.** The scope is where the consumer who relies on the behavior can
   observe it, not the most convenient place. Go through that consumer's interface so the guard
   survives refactors. Gate: would this guard still stand if the internals were rewritten, and is
   its scope the cheapest one that still sees the behavior? → `references/software-roles-and-scope.md`
3. **Plan the probes as their own steps.** Each one has a question and the decision it feeds.
   Confirms are not enumerated in a plan; they appear while building. Gate: does every probe name
   the decision that waits on its answer? → `references/software-planning.md`
4. **Write guards first; write confirms while building.** Mark confirms by the project's own means
   so culling is mechanical. Derive expected values independently of the code. Gate: does each test
   name the behavior it checks, and would its failure message say what broke? →
   `references/software-writing.md`
5. **Run the mutation check.** Name a plausible bug, or inject one (invert a condition, return a
   constant), and watch the guard go red. Gate: does this guard go red under a plausible wrong
   implementation? → `references/software-false-safety.md`
6. **Cull or promote confirms; then review the set.** Delete a confirm once its guard passes;
   promote it only if it encodes a behavior worth guarding, rewritten to guard standards. A bug
   leads to the behavior that lacked a guard: reproduce it as a confirm, then strengthen the guard
   for the class of bug. Gates: does every second test on a behavior catch a plausible bug the first
   misses? → `references/software-planning.md`. Is the suite free of growth by one test per
   incident? → `references/software-false-safety.md`

## Science procedure

Use it when choosing a statistical test, sizing a sample, comparing algorithms or models over noisy
runs, designing an experiment or writing an analysis plan. Test and protocol are co-designed: expect
to loop between steps 3 and 4 until they agree.

1. **Questions.** Research question, hypotheses, then the computable statistical questions that
   together answer them, at whatever granularity the topic needs, from one test to a battery.
   Argue why that battery suffices with a pattern-of-outcomes table (support, evidence against,
   inconclusive). Use an effect size and a smallest effect size of interest (SESOI) where one is meaningful; label exploratory
   questions as probes. Gate: is there an outcome pattern that would count against the hypothesis?
   → `references/science-questions-and-tests.md`
2. **Hypotheses.** H0 and H1 for each statistical question, one- or two-sided justified. When the
   claim is "no difference", test equivalence or non-inferiority. Handle multiplicity across the
   battery as a design choice. Gate: does each extra test earn its cost in power or error rate? →
   `references/science-questions-and-tests.md`
3. **Choose each test, and prove its validity.** Give the chosen test, the nearest alternatives with
   the property of this situation that rules each out, and its validity conditions, each with the
   evidence that it was checked and the fallback if it fails. The landscape is a sample: if you
   remember a better-fitting method, use it after confirming its conditions by search and citing
   what you read. Gate: for each condition, is the recorded evidence an argument, a diagnostic, a
   simulation or a cited result, not an assumption? → `references/science-questions-and-tests.md`,
   `references/science-test-landscape.md`
4. **Co-design the protocol.** Pairing, blocking, randomization, blinding and the unit of
   replication each change which test is valid. Controls are part of the protocol. Gate: have you
   checked which design decisions change the test? →
   `references/science-protocol-and-sample.md`
5. **See the battery fail on known truth.** Simulate data in the study contract's shape under H0,
   under the effect that matters, and for each distinction the battery claims to make (effect
   against artifact, say). Write the manifest now and run `check` on the simulated datasets before
   running the pipeline. This also debugs the pipeline before any data are collected. Gate: over
   many simulations, is the false-positive rate near nominal and does power hold at the stated
   effect, each with its Monte Carlo interval, and does each claimed distinction have its own
   known-truth scenario? →
   `references/science-protocol-and-sample.md`
6. **Size the sample.** Power from the SESOI or a stated meaningful effect, never from a pilot's
   observed effect; variance from a pilot or the literature; allow for design effect and attrition;
   give a sensitivity curve. Under a fixed budget report the minimum detectable effect. Gate: is
   each assumption that drives n recorded with its source and who agreed it? →
   `references/science-protocol-and-sample.md`
7. **Cohort and budget.** Inclusion and exclusion, stratification, allocation, and cost as unit cost
   times n times attrition margin. When unaffordable: reduce variance, then revise the meaningful
   effect openly and agreed, then downgrade to exploratory. Gate: was every budget-driven change one of
   those levers, named and agreed? → `references/science-protocol-and-sample.md`
8. **Data.** Every dataset conforms to the study contract so datasets can be swapped under the same
   battery; each dataset declares its `unit`, the variable whose levels are independent. This step has low freedom: validate, fix, repeat. Run exactly
   `uv run <skill-dir>/scripts/study_contract.py check <manifest>` (`<skill-dir>` is this skill's
   base directory; run it from the project) and fix until it prints `RESULT=OK`, before
   any test runs on a dataset. Gate: did `check` print `RESULT=OK` for every dataset about to be
   analysed? → `references/science-data.md`
9. **Show the results.** Every unit behind the estimate; the effect with its uncertainty against the
   lines that decide it; the primary figures pre-specified and first rendered on the H0 and effect
   simulations; every pre-specified outcome shown, nulls included; exploratory results labelled.
   Gate: would an inconclusive result look inconclusive, and a null look like a null? →
   `references/science-showing-and-explaining.md`

Scale each step to the study: a step that is trivially met gets one line saying why, and no gate is
skipped silently. Any change to the plan after it was fixed goes in the evolution log with its stage,
reason, who agreed and its effect on the claim (`references/science-analysis-plan.md`).

Before delivering, check the design against the statistical failure catalog
(`references/science-false-safety.md`), which is a sample: look for the case it does not name. Write
the plan to its categories (`references/science-analysis-plan.md`), and explain the design to
whoever ordered it (see Explaining the design).

## Non-negotiables

Few on purpose; everything else is judgement with its reason in the references. Each comes with the
signal that you are breaking it.

- **No count targets.** Signal: you are about to write "N tests for this", or a code-to-test ratio.
  You are counting instead of naming behaviors.
- **A guard that was never seen failing is not a guard.** Signal: you have no bug, named or injected,
  that turns it red.
- **Assumptions that drive n are agreed, not guessed.** Signal: a variance, effect or attrition rate
  in the plan with no source and no name next to it. Ask the user, ask the parent agent, or dispatch
  an agent to search the literature.
- **Validity conditions are checked and the evidence recorded.** Signal: a test chosen with its
  conditions unstated, or "assumed normal" with nothing behind it.
- **Every pre-specified outcome is shown.** Signal: a figure or table that omits a null, or a
  result described only as "significant".
- **The design is explained to whoever ordered it** (below). Signal: the output is a plan or a
  result with no reasons in plain terms.

## Explaining the design

Whoever ordered the design gets it explained: the human in the chat, the agent in the hand-off
report. Mandatory for science, recommended for software. For each choice say:

- what was chosen;
- why it fits this situation;
- why the alternatives do not;
- which assumptions it rests on and who agreed them;
- what each possible outcome would mean.

Write in plain terms and define each term at first use. An expert-level summary of results is not
enough, because statistical choices and their justifications are widely misunderstood.

## Where plans go

Follow the project's own convention first (its plan or docs folder, a roadmap task, a pull-request
description). Without one, put the plan inline in the plan or answer being written; if neither fits,
ask. A separate file only when the work is big enough to need one. The plans are defined by
categories, not templates: software in `references/software-planning.md`, analysis in
`references/science-analysis-plan.md`.

## Reference map

Read by where you are, not in order. Open only what the moment needs.

| Where you are | Open |
|---|---|
| Deciding what a test is for, which role, which scope; the TDD flow | [software-roles-and-scope](references/software-roles-and-scope.md) |
| Planning a feature, implementation, roadmap or bug fix: which guards, which probes, the plan's categories | [software-planning](references/software-planning.md) |
| Writing or marking tests; culling confirms; fixtures and trust boundaries | [software-writing](references/software-writing.md) |
| Reviewing or pruning a suite; asking whether a test is tautological or trivial; the mutation check | [software-false-safety](references/software-false-safety.md) |
| Turning a research question into hypotheses, statistical questions and a battery; choosing a test; multiplicity | [science-questions-and-tests](references/science-questions-and-tests.md) |
| Looking for a method that fits the situation (a sample of methods, not a menu); its validity conditions | [science-test-landscape](references/science-test-landscape.md) |
| Designing the protocol, controls, known-truth runs, sample size, cohort and budget | [science-protocol-and-sample](references/science-protocol-and-sample.md) |
| Fixing the shape of the data so datasets can be swapped; provenance; the evolution log | [science-data](references/science-data.md) |
| Planning figures; explaining the design to whoever ordered it | [science-showing-and-explaining](references/science-showing-and-explaining.md) |
| Checking an analysis for statistical false safety before delivering | [science-false-safety](references/science-false-safety.md) |
| Writing the analysis plan | [science-analysis-plan](references/science-analysis-plan.md) |

Files that are not references:

- `scripts/study_contract.py`: **run it, do not read it**, as `uv run <skill-dir>/scripts/study_contract.py`. `check` validates a manifest and its
  datasets, `init` scaffolds a manifest and dictionary from CSV headers, `compare` says whether two
  manifests are swappable. Details in [science-data](references/science-data.md).
- `assets/study-contract.schema.json`: the manifest schema. **Read it** when completing a manifest;
  do not copy it.
- `assets/data-dictionary.example.json`: a filled dictionary. **Copy it** as a starting shape for a
  new dictionary and replace its contents.
