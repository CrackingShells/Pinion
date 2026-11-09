# Science method references

**Goal**: Write the five science references that take an agent from a research question to a battery of tests co-designed with its protocol, sized, budgeted, shown honestly and explained to whoever ordered it.
**Pre-conditions**:
- [ ] Working in a worktree on `task/designing-tests-science_method`, cut from `claude/test-design-skill-03d1cc`; every command below runs from the worktree root
- [ ] R01 §1c, §2, §3, §5, §6 and the appendix read in full
**Success Gates**:
- ⬜ The five files exist under `skills/designing-tests/references/` with the names below; each over 100 lines opens with a `## Contents` list
- ⬜ The chain research question → hypotheses → statistical questions → battery admits any granularity, and the plan argues sufficiency with a pattern-of-outcomes table
- ⬜ Every test choice carries its alternatives, its validity conditions and the recorded evidence that each was checked; normality tests as gatekeepers are named as false safety with better checks given
- ⬜ Sample-size assumptions are agreed with the user, the parent agent or a dispatched agent, and the plan records who agreed them; no post-hoc power, no power from a pilot's observed effect
- ⬜ The standalone and banned-word grep over `skills/designing-tests` prints nothing
**References**: [R01 §3, §5, §6, appendix](../../__reports__/designing_tests/00-architecture_designing_tests_v0.md) — the method, the artifacts, Eliott's words

## Step 1: Questions and tests
**Goal**: Teach how questions become a battery, and how each test in it is chosen and proved valid.
**Implementation Logic**:
`science-questions-and-tests.md`: R01 §5 steps 1–3. The chain from research question to the battery at whatever granularity the topic needs; the pattern-of-outcomes table (support, evidence against, inconclusive); estimand and SESOI where an effect size is meaningful, and what to do when there is none; H0 and H1, one- versus two-sided with its justification, the switch to equivalence or non-inferiority (TOST) when the claim is "no difference"; multiplicity as a design choice across the battery; the roles in science (guard battery rerun on swapped datasets, confirms as known-truth checks of pipeline steps, probes as pilots and exploratory analyses, controls belonging to the protocol); the test-choice format (chosen test, nearest alternatives and the property of this situation that rules each out, validity conditions each with recorded evidence, the fallback). It opens the choice by saying the landscape is a sample, not a menu, links `science-test-landscape.md` for breadth, and invites a better-fitting method from the agent's own knowledge provided its validity conditions are confirmed by a search and cited.
**Deliverables**: `skills/designing-tests/references/science-questions-and-tests.md` (sections: from research question to battery, pattern-of-outcomes table, hypotheses, multiplicity, roles in science, choosing a test, proving validity)
**Consistency Checks**: `p=skills/designing-tests/references/science-questions-and-tests.md; test -f $p && grep -q 'science-test-landscape.md' $p && { [ "$(wc -l < $p)" -le 100 ] || grep -q '^## Contents' $p; }` (expected: PASS)
**Consistency Checks**: `! grep -riE 'writing-reports|managing-roadmaps|writing-history|writing-release|plumage|playbook|skill-creator|dataviz|waiting-on-processes|spawning-agent-plugins|invariant|deviation' skills/designing-tests` (expected: PASS)
**Commit**: `feat(designing-tests): add how questions become a battery of valid tests`

## Step 2: Protocol and sample
**Goal**: Co-design the protocol with the tests, see the battery fail on known truth, and size the cohort within its budget.
**Implementation Logic**:
`science-protocol-and-sample.md`: R01 §5 steps 4–7. Each protocol decision and the tests it validates or invalidates (pairing, blocking, randomization, blinding, biological versus technical replicates, pseudoreplication); controls as part of the protocol; iterating protocol and analysis until they agree; known-truth runs (simulate data in the study contract's shape under H0 and under the effect that matters, run the real pipeline, read the false-positive rate and power; this also debugs the pipeline). Sample size: power from the SESOI or a stated meaningful effect, variance from a pilot or the literature, analytic where possible and simulation otherwise, design effect and attrition, a sensitivity curve, the minimum detectable effect under a fixed budget, why post-hoc power and pilot-effect power mislead. Agreeing the guesses: who to ask (user, parent agent, a dispatched literature search) and how the plan records each assumption, its source and who agreed it. Cohort and budget: inclusion and exclusion, stratification and matching, allocation, cost as unit cost × n × attrition margin, and the ordered levers when the study is unaffordable.
**Deliverables**: `skills/designing-tests/references/science-protocol-and-sample.md` (sections: protocol co-design, controls, known-truth runs, sample size, agreeing assumptions, cohort, budget)
**Consistency Checks**: `p=skills/designing-tests/references/science-protocol-and-sample.md; test -f $p && { [ "$(wc -l < $p)" -le 100 ] || grep -q '^## Contents' $p; }` (expected: PASS)
**Consistency Checks**: `! grep -riE 'writing-reports|managing-roadmaps|writing-history|writing-release|plumage|playbook|skill-creator|dataviz|waiting-on-processes|spawning-agent-plugins|invariant|deviation' skills/designing-tests` (expected: PASS)
**Commit**: `feat(designing-tests): add protocol co-design, sample size and budget`

## Step 3: Showing, explaining and the analysis plan
**Goal**: Make results visible whether good or bad, make the design understood, and define the analysis plan by its categories.
**Implementation Logic**:
`science-showing-and-explaining.md`: visibility guidelines, not plot types (R01 §5 step 9): a procedure in order and non-negotiables, each with its reason, covering every unit shown behind the estimate, effect with uncertainty against the lines that decide it, pre-specified figures rendered first on the H0 and effect simulations, every pre-specified outcome shown, shared axes, visible nesting, exploratory results labelled. Then the explanation contract (R01 §6): what each explanation covers, plain terms defined at first use, addressed to the human in chat or the agent in the hand-off report, and why (statistical choices and their justifications are widely misunderstood).
`science-analysis-plan.md`: the analysis plan defined by the categories of R01 §6, each saying what it must establish and why, with no template; where it lives (the project's convention first); the evolution log as a neutral record of how the plan changed and why.
**Deliverables**: `skills/designing-tests/references/science-showing-and-explaining.md` (sections: showing results, non-negotiables, explaining the design); `skills/designing-tests/references/science-analysis-plan.md` (sections: the categories, where it lives, the evolution log)
**Consistency Checks**: `for f in science-showing-and-explaining science-analysis-plan; do p=skills/designing-tests/references/$f.md; test -f $p || exit 1; [ "$(wc -l < $p)" -le 100 ] || grep -q '^## Contents' $p || exit 1; done` (expected: PASS)
**Consistency Checks**: `! grep -riE 'writing-reports|managing-roadmaps|writing-history|writing-release|plumage|playbook|skill-creator|dataviz|waiting-on-processes|spawning-agent-plugins|invariant|deviation' skills/designing-tests` (expected: PASS)
**Commit**: `feat(designing-tests): add showing results, explaining the design and the analysis plan`

## Step 4: Statistical false safety
**Goal**: Mirror the software catalog for statistics, as illustrations of one principle.
**Implementation Logic**:
`science-false-safety.md`: the principle (a test gives false safety when its result is fixed by construction, or when the analysis could not have come out otherwise); the catalog of R01 §5 as worked illustrations, each saying why it fails and what to do instead (tests fixed by construction such as circular analysis, baseline tests after randomization, differences created by a threshold or a normalization; forking paths; pilot-effect power; post-hoc power; pseudoreplication; normality tests as gatekeepers; "not significant" read as "no effect"; p-values without effect sizes; selective figures). It closes by asking for the case it does not list, and links the software counterpart by its file name only.
**Deliverables**: `skills/designing-tests/references/science-false-safety.md` (sections: the principle, catalog, what to do instead)
**Consistency Checks**: `p=skills/designing-tests/references/science-false-safety.md; test -f $p && { [ "$(wc -l < $p)" -le 100 ] || grep -q '^## Contents' $p; }` (expected: PASS)
**Consistency Checks**: `! grep -riE 'writing-reports|managing-roadmaps|writing-history|writing-release|plumage|playbook|skill-creator|dataviz|waiting-on-processes|spawning-agent-plugins|invariant|deviation' skills/designing-tests` (expected: PASS)
**Commit**: `feat(designing-tests): add the statistical false-safety catalog`
