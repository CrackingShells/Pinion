# From questions to a battery of valid tests

Open this when a research question exists and no test has been picked yet, or when a test is
picked and nobody has said why. It covers the first three moves of the scientific method:
questions, hypotheses, and the choice of each test with proof that it is valid. Protocol, sample
size and budget are in [science-protocol-and-sample.md](science-protocol-and-sample.md).

## Contents

- From research question to battery
- Pattern-of-outcomes table
- Hypotheses
- Multiplicity
- Roles in science
- Choosing a test
- Proving validity

## From research question to battery

The chain is: research question, then hypotheses, then statistical questions (each computable
from data), then the battery of tests that answers them together. The granularity between two
links is whatever the topic needs. One research question may be answered by a single test; another
needs several tests that only jointly mean something (an effect on the primary outcome, a dose
pattern, a check that it is not an artifact of one subgroup). Do not force one test per question,
and do not invent a level because a template has it.

Two things make the chain worth writing down:

- **Each link is argued.** State why this hypothesis speaks to the question and why this statistical
  question speaks to the hypothesis. A statistical question that cannot be traced upward is a
  probe (below), not part of the battery.
- **Sufficiency is argued.** Say why this battery, and not a smaller or larger one, answers the
  research question. If one member were removed, which claim would no longer be supported? If one
  were added, what would it settle that the others cannot? The table below is where that argument
  becomes checkable.

Estimand and SESOI (smallest effect size of interest) are used where an effect size is
meaningful: a difference, ratio, hazard ratio, correlation, or a change in a rate. State the
estimand in words and units first, then the SESOI, with its justification (a cost, a clinical or
engineering threshold, a prior effect worth confirming, the smallest effect the design could
afford to detect if nothing else is available, stated as such). Some questions have no effect
size: "does the pipeline recover the planted structure", "is the ranking of methods stable",
"does the distribution differ at all". Then the statistical question is about a pattern or a
property, there is no SESOI, and the table is written in terms of that property. Do not invent a
SESOI to fit the vocabulary.

## Pattern-of-outcomes table

Write it before the data exist. One row per pattern of results across the battery; three columns
of meaning: support, evidence against, inconclusive. It forces two things: that every outcome has
a reading, and that "inconclusive" is a planned outcome and not a surprise.

For a single effect with a SESOI, the rows come from where the confidence interval falls against
zero and the SESOI lines. A wholly beyond-SESOI interval supports a meaningful effect. An interval
that excludes zero but lies inside the SESOI band says an effect is detectable and too small to
matter. An interval inside the band, with the equivalence test passed, is evidence against a
meaningful effect. An interval that spans zero and reaches past the SESOI is inconclusive, however
the p-value is phrased. State the interval level per row, because the two lines of reading use
different intervals: the two-sided difference is read from the (1 - alpha) interval (95% at
alpha = 5%), the equivalence test from the (1 - 2 alpha) interval (90% at alpha = 5%), and a row that
mixes them says which line each claim uses. For a battery, rows are combinations: primary test positive with the
robustness test negative reads differently from both positive, and the table says how.

This is a sample of the shape, not the shape. A question about a curve, a ranking or a structure
needs rows of its own kind. Write the rows that your battery can actually produce.

## Hypotheses

Per statistical question, write H0 and H1 in terms of the estimand, not of the test statistic
("the mean difference in recovery time is zero", not "the t statistic is zero").

- **One-sided or two-sided**, with the reason, decided before the data. One-sided is justified when
  an effect in the other direction would be handled exactly like no effect (a new method is adopted
  only if better). It is not justified by having seen the sign, nor by wanting power: the same data
  with the same alpha give a one-sided p-value half the two-sided one only if the sign matches.
  If an effect in the opposite direction would matter (harm, a reversal), the question is
  two-sided.
- **"No difference" is a different claim.** A non-significant difference test does not support it
  (see [science-false-safety.md](science-false-safety.md)). The statistical question becomes
  equivalence or non-inferiority, and H0 flips: H0 is that the effect is at least as large as the
  margin. The two one-sided tests procedure (TOST) rejects both "effect below the lower margin" and
  "effect above the upper margin", each at level alpha; it is equivalent to the (1 - 2 alpha)
  confidence interval lying inside the margins (Schuirmann 1987, Journal of Pharmacokinetics and
  Biopharmaceutics 15:657-680, doi:10.1007/BF01068419; Lakens 2017, Social Psychological and
  Personality Science 8:355-362, doi:10.1177/1948550617697177). The margin is the SESOI or a stated tolerance, justified and agreed
  with the user, and fixed before the data. A margin chosen after seeing the interval proves
  nothing. Non-inferiority is the one-sided version, with a margin on one side only.
- **Composite claims.** "A is better than B on speed and no worse on accuracy" is two statistical
  questions with different H0s; each gets its own row in the table.

## Multiplicity

Multiplicity is a design choice made across the battery, because each extra test costs either power
or error control, and no analysis step can repair that afterwards. Decide three things:

- **What is the claim?** If the claim requires every test to be positive (a co-primary outcome set,
  an effect that must also survive a robustness check), the false-positive risk of the claim does
  not grow with the number of tests, but its power falls, so size the study for the conjunction.
  If the claim is that at least one test is positive, the risk grows, and a correction is required.
- **Which error rate?** Familywise error (probability of any false positive) for a confirmatory
  claim where one false positive is costly: Holm's step-down procedure controls it under any
  dependence and is never worse than Bonferroni. False discovery rate when many tests are screened
  and some errors are tolerable: Benjamini-Hochberg controls it under independence or positive
  dependence of a specific kind; Benjamini-Yekutieli holds under arbitrary dependence at a power
  cost. State which assumption you are relying on and why it holds.
- **Structure.** Ordered hypotheses can be tested in a fixed sequence, or through gatekeeping (a
  secondary is tested only if the primary passes), which spends no alpha on the later ones. The
  order must be pre-specified.

Probes (below) are outside the family, because they confirm nothing, but they must be labelled so
that nobody reads them as members of it. The size of the family is part of what the plan has to
justify; a battery that grew because testing was cheap is the statistical form of a suite that
grew without being useful.

## Roles in science

The three roles carry over, with the field's own term beside each:

- **Guard: the battery** attached to a research question: its tests, its decision rules and its
  known-truth run, specified before the data. It lives as long as the question is
  relevant, and it is rerun on every dataset swapped in (a new cohort, a rerun, a simulation), which
  is what [science-data.md](science-data.md) makes checkable. A swapped-in dataset is a new
  confirmation, not an invitation to retune: a test changed after seeing a dataset is an entry in
  the evolution log ([science-analysis-plan.md](science-analysis-plan.md)), with the reason.
- **Confirm: known-truth check of a pipeline step.** While the pipeline is being built, does step k
  recover the effect planted in toy data? It lives until the battery's known-truth run passes end to end
  (see [science-protocol-and-sample.md](science-protocol-and-sample.md)), then is culled. A check
  worth keeping is rewritten as a software guard of the pipeline code, under the rules for guards.
- **Probe: exploratory analysis or pilot.** It answers a question that feeds a decision (the
  variance, the feasibility, which measurement is more precise) and never confirms. Its output
  goes where decisions are recorded, and a hypothesis that came from a probe needs fresh data to
  be confirmed.
- **Controls are not confirms.** Positive and negative experimental controls belong to the
  protocol and the data; they are kept and reported with the results.

## Choosing a test

The landscape in [science-test-landscape.md](science-test-landscape.md) is a sample of methods
organized by the properties that discriminate between them, not a menu. If you know a method that
fits the situation better, use it, but a method taken from memory is not acceptable on its own:
search for its validity conditions (the primary source, a methods paper, the software
documentation), confirm that they hold here, and cite what you read in the plan.

What drives the choice: the question type; the dependence structure of the data (paired,
repeated, nested, clustered, spatial or temporal; the unit that is independent); the outcome type
and its distribution; the factors and covariates; and n. Decide the unit of analysis first,
because every later property follows from it.

For every test in the battery, record:

1. **The chosen test**, and the statistical question it answers.
2. **The nearest alternatives, each with the property of this situation that rules it out.** "Not
   a paired design, so the paired test is out" is a reason. "Less powerful" without a situation is
   not, and neither is "commonly used".
3. **Validity conditions**, each with its recorded evidence (next section).
4. **The fallback** if a condition fails when the data arrive, chosen now so that switching is
   not a data-driven choice made after seeing p-values.

Prefer tests that estimate the quantity of the hypothesis. Note what a test really tests: the
Mann-Whitney test addresses stochastic dominance (the probability that a draw from one group
exceeds a draw from the other); it is a test of medians only under extra assumptions about the
shape of the distributions, so it cannot answer a question about medians in general.

## Proving validity

Every test has conditions under which its error rates are what they claim. Validity is proved, not
assumed, and the plan holds the proof. For each condition, record how it was established and what
that showed. The forms of evidence, from strongest to weakest for most conditions:

- **An argument from the design.** Independence from randomization or from a protocol that
  separates units; exchangeability under H0 from random assignment. This is the best evidence
  for conditions about independence, which the data can hardly show.
- **A simulation of robustness** at the planned n and the plausible departures: heavy tails,
  unequal variances, clustering, the expected missingness. Run through the real pipeline
  ([science-protocol-and-sample.md](science-protocol-and-sample.md), known-truth runs). It reads
  off the actual false-positive rate and power under the violation, which no assumption test does.
- **A diagnostic of the fitted model**, read as a graph and a magnitude: residual plots,
  influence measures, overdispersion ratios, events per variable, minimum expected counts.
  Interpret it as evidence about how much the violation could matter, not as a pass or fail.
- **A cited result** that the method is robust to the departure at this kind of n, with the source
  and what it actually says.

Conditions of a different kind need different evidence: the minimum expected cell counts of a
chi-squared test (compute them), the events per variable of a logistic or Cox model, proportional
hazards (a diagnostic plus the fallback of a model without it), sphericity, the independence of
units. The first move for each is to ask what the condition protects (the sampling distribution
of the statistic, the variance estimate, the independence of errors) and check that.

Do not prove a condition by running a significance test on the same data and branching on its
result. Normality tests as gatekeepers are false safety: the condition concerns the sampling
distribution of the statistic (usually argued from n, the spread of the data and the robustness of
the test), small samples give these tests little power, large samples reject harmless
departures, and choosing the test conditional on the outcome distorts the conditional error rates of the
test chosen (Rochon, Gondan and Kieser 2012, BMC Medical Research Methodology 12:81,
doi:10.1186/1471-2288-12-81: simulated exponential, uniform and normal data, Shapiro-Wilk
followed by the t test or Mann-Whitney; the conditional Type I error rates were seriously altered,
while the overall rate of the two-stage procedure stayed near nominal, and the authors call the
procedure formally incorrect). Use the evidence
above, or a method robust to the departure from the outset, such as Welch's unequal-variance
t-test in place of the pooled-variance one.

If the data show a condition failing and the fallback was named in advance, switch and log it. If
no fallback was named, stop and decide with whoever agreed the plan; do not search the data for the
analysis that gives the better p-value.

What condition of your chosen test is not on this page? List it, and its evidence.
