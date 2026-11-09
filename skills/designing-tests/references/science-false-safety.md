# Statistical false safety

Open this when choosing or reviewing a test, a power calculation or a figure, and whenever a result
looks reassuring. It is the statistical counterpart of
[software-false-safety.md](software-false-safety.md): the same question, asked of an analysis.

## Contents

- The principle
- Catalog
- What to do instead

## The principle

A test gives false safety when its result is fixed by construction, or when the analysis could not
have come out otherwise. Then a reassuring result carries no information about the question, and
the reader's confidence rises for nothing.

The detector mirrors the mutation check of software: name how the analysis could have come out
the other way, or make it do so. Run it on data where the answer is known to be negative (the H0
simulation, or the real data with the labels shuffled) and see whether it still reports an effect;
run it on data with a planted effect and see whether it finds it. An analysis that "finds" the
effect in shuffled data, or that cannot miss a planted one, was never testing the question.

The catalog below is a sample of ways this happens, with the reason each fails so that the
reason transfers. It is not a list to tick.

## Catalog

**Tests fixed by construction.** The result is determined by how the comparison was set up.

- *Circular analysis* (selecting on the outcome, then testing it). Units are chosen because they
  show the effect (the voxels, genes or runs with the largest difference) and the same data are then
  tested for the effect: the selection guarantees it (Kriegeskorte et al. 2009, "double dipping").
  Why it fails: the selection step used up the randomness the test relies on.
- *Baseline tests after randomization.* Testing whether randomized groups differ on a baseline
  variable asks whether chance operated, and by construction any difference is chance. A
  significant result does not show the randomization failed, a nonsignificant one does not show
  the groups are balanced in a way that matters, and it says nothing about bias in the outcome.
  Why it fails: the null is true by design. (Checking that the randomization procedure was
  executed as specified is a different, legitimate check; in a study without randomization,
  imbalance is real, and its size, not a p-value, is what matters.)
- *Differences created by a threshold or a normalization.* Dividing a sample at a cutoff of the
  variable and then testing that variable between the halves; expressing results as a fraction of the
  control and then testing the control against 1 (zero spread by construction); selecting extreme
  baseline values and then "showing improvement" at follow-up (regression to the mean). Why it
  fails: the transformation puts the difference in, and the test finds what was placed there.

**Forking paths.** Analysis choices (outliers, covariates, transformations, subgroups, which
outcome) made after seeing the data, even honestly and without searching for significance, mean
that a different dataset would have led to different analyses, and the nominal error rate no
longer describes the procedure (Gelman and Loken 2013). Why it fails: the number of effective
tests is larger than the number reported.

**Pilot-effect power.** Powering a study on the effect a pilot observed. The pilot's estimate is
noisy, and a pilot that was followed up because it looked good is also biased upward, so the study
is underpowered for the real effect (Albers and Lakens 2018). Why it fails: the number looks like
evidence about the effect and is mostly noise.

**Post-hoc power.** Computing power from the observed effect after the result. It is a function of
the p-value, so it re-reports it and cannot say whether the study was informative (Hoenig and Heisey
2001). Why it fails: it cannot differ from what it was computed from.

**Pseudoreplication.** Treating replicates below the unit of assignment as independent (cells in
a dish, measurements per subject, epochs per recording, reruns of one training run). The test then
claims more independent evidence than exists (Hurlbert 1984), and small effects become
"significant". Why it fails: the sample size in the test is not the sample size of the design.

**Normality tests as gatekeepers.** Running a test of normality and choosing the main test from
its outcome. Small samples give it little power to see departures that matter, large samples reject
harmless ones, the condition concerns the sampling distribution of the statistic and not the raw
data, and the conditional procedure alters the error rates of the test that follows (Rochon, Gondan
and Kieser 2012). Why it fails: it looks like a check and decides the wrong question.

**"Not significant" read as "no effect".** Failure to reject H0 is what a small study, or noisy
data, produces too (Altman and Bland 1995). Why it fails: the test was never set up to support
absence; an interval or an equivalence test against a margin can.

**p-values without effect sizes.** A p-value mixes the size of the effect with the precision of the
study: a tiny effect in a huge sample, and a large one in a small sample, can give the same p. Why
it fails: the reader cannot tell whether the result matters.

**Selective figures.** Showing the panels that worked, the summary without the units, or an axis
that exaggerates (see [science-showing-and-explaining.md](science-showing-and-explaining.md)).
Why it fails: the reader sees the selection, not the data.

**A known-truth run that cannot fail.** Simulating data from the very model the analysis fits, with
the assumptions the test needs, and finding the test well calibrated. Why it fails: the assumptions
were put into the data, so the run says nothing about whether they hold.

## What to do instead

- For results fixed by construction: select on independent data (a split, a held-out set, a
  criterion unrelated to the contrast) or model the selection; test on the original scale with the
  baseline in the model; state the question the design can answer.
- For forking paths: pre-specify the battery, log every change with its stage
  ([science-analysis-plan.md](science-analysis-plan.md)), and show the alternative analyses as a
  robustness view labelled exploratory.
- For power: use the SESOI or a stated meaningful effect, show the sensitivity curve, and report the
  interval after the fact ([science-protocol-and-sample.md](science-protocol-and-sample.md)).
- For replicates: define the unit at design time, average or model the clustering.
- For validity conditions: evidence from the design, a simulation at the planned n, a diagnostic
  read as a magnitude, a cited result, or a method robust to the departure from the start
  ([science-questions-and-tests.md](science-questions-and-tests.md)).
- For nulls: report the interval and test equivalence against a margin agreed in advance.
- For figures: follow the procedure and the non-negotiables for showing results.

What other way can an analysis be unable to come out otherwise? If you find one in this study, add
it to the plan, with the check that would have caught it.
