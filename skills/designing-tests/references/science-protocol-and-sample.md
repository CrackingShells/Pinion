# Protocol, known-truth runs, sample size, cohort and budget

Open this once the battery's questions and candidate tests exist
([science-questions-and-tests.md](science-questions-and-tests.md)) and before any data are
collected or analyzed. The protocol and the tests are designed together because each protocol
decision changes which test is valid, and each test changes what the protocol must record.

## Contents

- Protocol co-design
- Controls
- Known-truth runs
- Sample size
- Agreeing the assumptions
- Cohort
- Budget

## Protocol co-design

Walk each protocol decision and ask two questions: which tests does it make valid, and which does
it invalidate? The sample of decisions below shows the reasoning; your study will have decisions
that are not here, and they get the same two questions.

- **The unit.** The unit of analysis is the unit that was independently assigned to a condition or
  independently sampled. Replicates below that unit (several measurements per animal, cell
  culture well, user, seed-less rerun of the same model) are not independent evidence about the
  condition. Treating them as if they were is pseudoreplication (Hurlbert 1984): the test's error
  rate no longer holds, and the cause is in the protocol, so it cannot be repaired by the test
  alone. Decide here whether replicates are averaged, modelled with a random effect for the unit,
  or analyzed with a method that handles clustering.
- **Biological versus technical replicates.** Technical replicates measure the assay's noise and
  improve the precision of each unit's value; biological replicates (independent units) carry the
  between-unit variation the inference needs. Adding technical replicates cannot buy the power that
  more units would.
- **Pairing.** A paired design (the same unit under both conditions, or matched units) lets the
  analysis use within-pair differences, which helps in proportion to how strongly the pair members
  correlate. The paired analysis follows the paired design; analyzing paired data as independent
  wastes the pairing, and the reverse invents a dependence that is not there.
- **Blocking.** Blocks remove known nuisance variation from the comparison only if the analysis
  includes the block. Randomize within blocks, and put the block in the model or the stratified
  test.
- **Randomization.** It is the design's argument for independence and for exchangeability under
  H0, which is what a permutation or randomization test needs, and it protects against confounding
  by variables nobody listed. Say how the sequence is generated and concealed.
- **Blinding.** It protects the outcome from the expectations of whoever measures or handles. It is
  not a validity condition of a test, but without it the estimate can be biased in a way no test
  detects. Say who is blinded to what, or why blinding is impossible and what replaces it (an
  objective measure, an automated readout).
- **Repeated measures and time.** More than one observation per unit over time brings dependence
  and missingness patterns; name the structure now so that the test (a mixed model, a GEE, a
  summary measure per unit) is chosen for it.

Iterate between protocol and analysis until they agree: the analysis must be computable from what
the protocol records, and the protocol must record nothing that the analysis ignores without a
reason. A disagreement found after the data exist usually costs the study.

## Controls

Positive and negative experimental controls belong to the protocol, not to the pipeline. A negative
control shows that the setup does not produce the effect from nothing; a positive control shows
that the setup can detect an effect when one exists. They are collected with the data, analyzed
with the data, and reported whatever they show. A failed control is a result about the
experiment, and it tells you what the main result can no longer mean. They are not the known-truth
checks of the pipeline (those are in the next section and use simulated data).

## Known-truth runs

Before any real data, run the real pipeline on data whose truth you set:

1. Simulate data in the shape the study contract fixes ([science-data.md](science-data.md)), with
   the same units, structure, missingness and n as the plan, once under H0 and once under the effect
   that matters (the SESOI or the stated meaningful effect).
2. Run the real analysis code: the same functions that will run on the real data, including any
   preprocessing, model fitting, decision rules and multiplicity handling.
3. Repeat enough times that the Monte Carlo error is smaller than the tolerance you care about.
   The standard error of an estimated rate p from B runs is sqrt(p(1 - p) / B); with a false
   positive rate near 0.05, a tolerance of a few thousandths needs thousands of runs, and the
   decision to run more is made from that formula, not from habit. Report the estimate with its
   interval.
4. Read three things. The **false-positive rate** under H0 should be consistent with the nominal
   level within Monte Carlo error (below it is acceptable for discrete or conservative tests;
   above it means the pipeline or the test is invalid for this design). The **power** at the effect
   that matters. The **recovery** of the planted effect (bias, interval coverage).
5. Repeat under the departures that threaten the validity conditions: unequal variances, heavy
   tails, clustering the model ignores, the expected missingness. The result is the recorded
   evidence for those conditions at the planned n.

This also debugs the pipeline before any data are collected: a bug that flips a sign, drops a
group or leaks the outcome into a selection step shows up as a wrong rate or a wrong effect on data
where the answer is known. The same simulation under H0 is the render target for the pre-specified
figures ([science-showing-and-explaining.md](science-showing-and-explaining.md)).

A known-truth run that cannot fail proves nothing: if the simulation reuses the analysis's own
assumptions to generate data, the pipeline will look calibrated by construction. Generate the data
by a process that is not the model being fitted, at least for the robustness runs.

## Sample size

The question is: how many units give an acceptable chance of detecting the effect that matters,
while keeping errors at the stated level? Build it from these parts:

- **The effect.** Power is computed at the SESOI or a stated meaningful effect. It is never taken
  from the effect a pilot happened to observe: that estimate is noisy, and if the pilot was
  followed up because it looked promising, it is also inflated, so the study is underpowered for
  the true effect (Albers and Lakens 2018 show the bias when power analyses use pilot effects). For
  an equivalence question, power is the chance of concluding equivalence when the true effect is
  zero or at the most plausible value, against the margin.
- **The variance (or the nuisance parameters).** From a pilot or the literature, with its
  uncertainty acknowledged: an SD estimated from a small pilot is itself imprecise, so use an
  upper confidence limit, or show the result at several plausible values.
- **The alpha and the target power**, agreed, and the number of tests the multiplicity decision
  implies ([science-questions-and-tests.md](science-questions-and-tests.md)).
- **The design effect.** Clustering inflates the variance of a mean by about 1 + (m - 1) times the
  intraclass correlation, for clusters of size m; blocks and pairing change it in the other
  direction. The effective sample is the number of units divided by that factor.
- **Attrition and exclusions.** To end with n analyzable units, enroll n / (1 - a) where a is the
  expected loss fraction. Enrolling n x (1 + a) leaves the study short.
- **Analytic or simulated.** Use the closed-form calculation when one exists for exactly your
  design and test. When the analysis is a mixed model, a permutation test, a multiplicity-adjusted
  battery, or anything the formula does not describe, simulate it with the known-truth machinery
  above; the same code then answers the sample-size question, and reports its own Monte Carlo error.

Then give the reader the whole picture rather than one number: a **sensitivity curve** (power
against effect size at the planned n, or n against effect size at the target power) so that every
assumption's consequence is visible, and, when the budget fixes n, the **minimum detectable
effect**: the smallest effect detected with the target power at that n. Reporting it replaces the
temptation to claim a power the budget cannot buy.

Do not compute power after the data are in. Observed ("post-hoc") power is a one-to-one function of
the p-value, so it adds nothing to the result and cannot say whether a null result is
informative (Hoenig and Heisey 2001); the interval and the equivalence test do. See
[science-false-safety.md](science-false-safety.md).

## Agreeing the assumptions

The assumptions that drive n and the budget (variance, the meaningful effect, attrition, unit
cost, the intraclass correlation, the margin) are the study's weak points, and a guess made
alone is silent error. For each one, get another view, from the source that can actually
supply it:

- **The user**, for what matters (the SESOI, the margin, the affordable cost, the tolerable
  error). Only the person who owns the decision can say what effect is worth detecting.
- **The parent agent**, when you were dispatched, for what it knows of the context and the earlier
  decisions; ask it and, if it cannot answer, ask it to ask the user.
- **A dispatched agent**, for what the literature or earlier data can supply (typical variances,
  attrition in similar studies, published intraclass correlations): brief it with the exact
  quantity, the population and the form of answer (value, interval, source).

Record, per assumption: its value, its source (a citation, a pilot, a person), and **who agreed
it**, with the date it was agreed. An assumption with no source and no agreement is listed as
unagreed and shown with its sensitivity curve, so that it is visibly a guess. When nobody can be
asked, say so, show the range, and let the decision-maker see it.

## Cohort

- **Inclusion and exclusion** rules are defined from the question and fixed before outcomes are
  seen. Exclusions based on anything measured after assignment can bias the comparison, because
  they can differ between arms; justify any such rule and say how it is applied the same way in
  each arm.
- **Stratification and matching** are for the variables that predict the outcome strongly or whose
  imbalance would be costly to the comparison. The analysis must mirror them (see blocking above).
  Matching on many variables quickly leaves too few matched units; say what you do about the
  unmatched.
- **Allocation.** Equal allocation is the default. When units cost different amounts or the
  variances differ by group, the allocation that minimizes the variance of a two-group comparison
  for a fixed budget is proportional to the group's SD divided by the square root of its unit cost.
  Check that the analysis tolerates unequal groups.

## Budget

Cost = unit cost x n x attrition margin, where the margin is 1 / (1 - a) as above, plus the costs
that do not scale with n (setup, controls, the pilot). Compare it with the budget before anything
is bought or run.

When the study is unaffordable, take the levers in this order, and tell the decision-maker which one
you took:

1. **Reduce variance.** A better measurement, a paired or blocked design, a covariate that
   explains the outcome, fewer sources of noise. This costs nothing in meaning.
2. **Revise the meaningful effect**, openly and with agreement. A larger SESOI is a smaller
   question; the user must agree that an effect below it no longer matters, and the plan records it.
3. **Downgrade to exploratory.** If neither is acceptable, the study becomes a probe (exploratory
   analysis): it can inform the next study and cannot confirm. Label it so in every output.

Lowering the target power or relaxing alpha without saying so is not a lever, it is a change in the
claim; if the user wants it, it is an agreed assumption and is recorded as one.

Which decision in your protocol is not on this page, and which test does it change?
