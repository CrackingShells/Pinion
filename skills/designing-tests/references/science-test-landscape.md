# Test landscape: a map of statistical-test families

## Contents

- How to use this map
- Reading your situation
- Location and scale
- Proportions and contingency
- Association and agreement
- Regression and GLM (ordinal, count, zero-inflated)
- Mixed models and GEE
- Survival

## How to use this map

This file is a sample, not a menu. It names the families most studies meet, and for each one the usual default, the properties that make an alternative fit better, and the validity conditions with a way to check each. A situation outside the sample is normal, not a failure.

Go beyond the map when your situation calls for it:

1. Use what you know. A method you remember is a candidate, never a decision.
2. Confirm it by search (web or paper search): find a primary source that states the method's validity conditions and that fits your situation's axes (next section).
3. Cite what you read in the plan, next to the validity evidence. A method taken from memory without that check is not acceptable, because the failure is silent: the test runs and returns a p-value either way.

Every entry follows one shape: when it fits, what separates it from its neighbours, validity conditions each with how to check it, and a source. Prove validity by an argument from the design, a diagnostic, a robustness simulation, or a cited result. Do not prove it with a significance test run on the same data you are about to analyse: the pretest has its own error rates, and the main test's error rates become conditional on it passing (see the normality pretest entry below). A diagnostic you read as a plot or an estimate (expected counts, a residual plot, an intraclass correlation) is not a gatekeeping test.

Where an entry says a condition "holds by design", the argument itself goes in the plan: how units were sampled, randomised, or measured. For which test settles which statistical question, see `science-questions-and-tests.md`; for how a passed test can still be unsafe, see `science-false-safety.md`; for the sample and its size, see `science-protocol-and-sample.md`.

## Reading your situation

Read these axes off the research question before you open a family. Two situations that share the outcome type but differ on another axis usually need different methods.

- **Question type**: difference, equivalence or non-inferiority, association, agreement, prediction, trend over time.
- **Outcome type**: continuous, bounded or proportion, binary, ordinal, count, time-to-event, circular, composition, multivariate.
- **Dependence**: independent units, paired, repeated measures, nested or clustered, serial (time order), spatial. This axis is the one most often misread: observations that share a subject, litter, site, batch or seed are not independent.
- **Groups and factors**: two groups, several, crossed factors, a continuous exposure.
- **Covariates**: adjustment needed for confounding or for precision, and whether the effect may differ by covariate.
- **n and events**: total units, units per group, number of clusters, number of events (binary outcome, survival). Several rules below depend on the scarcer of these, not on the total.
- **The claim**: a difference, an equivalence within a margin, an association, a prediction on new data. The same data support different tests for different claims.

State the axes in the plan in one line each. A reader (or reviewer) who sees them can check that the family chosen matches.

## Location and scale

**Default: Welch's t-test (two groups), Welch's ANOVA (several groups).** Use Welch rather than Student's pooled test even when the variances look equal. Student's test is conservative when the larger variance goes with the larger group and liberal when it goes with the smaller one (nominal 0.05 became about 0.028 and 0.083 in the simulation reported), and tolerant only with equal group sizes. Welch holds near-nominal error from about 10 per group and loses little when the variances are equal. The choice is made by design, so no variance pretest is needed, and a Levene-type pretest has low power and makes the main test's error conditional on its result.
Source: Delacre, Lakens and Leys 2017, Int Rev Soc Psychol, doi:10.5334/irsp.82; for ANOVA, Delacre et al. 2019, doi:10.5334/irsp.198 (the Welch W test outperforms F when variances differ and is slightly less efficient when they are equal and the data non-normal).

**Alternatives and the property that favours each**

- **Mann-Whitney / Wilcoxon rank-sum** when the question is about stochastic ordering, P(X<Y) against P(Y<X), or the outcome is ordinal or heavily outlier-prone. It does not test medians, and it is not a safe replacement for Welch under unequal variances: it needs exchangeability under the null and for a medians reading it needs equal spread; its Type I error can be inflated even at large n when that fails. If you want the stochastic-ordering claim without the equal-spread requirement, use Brunner-Munzel (a permutation version is weakly favoured); its power is about that of Mann-Whitney, apart from skewed data with unequal n, where Mann-Whitney has a small advantage. Source: Karch 2021, Adv Methods Pract Psychol Sci, doi:10.1177/2515245921999602.
- **Wilcoxon signed-rank** for paired differences when the t-test's assumptions are doubtful. It assumes the differences are commensurable (a difference of 5 means the same anywhere on the scale) and continuous (not rounded to ties). When the paired t-test's assumptions do hold, signed-rank is less powerful. Source: Demsar 2006, JMLR 7:1-30.
- **Permutation test** when the design supplies exchangeability (random assignment) and the statistic you care about has no convenient null distribution. Count the observed arrangement among the permutations: a permutation p-value of exactly zero is never correct (use (b+1)/(m+1) or the exact count). Source: Phipson and Smyth 2010, Stat Appl Genet Mol Biol, arXiv:1603.05766.
- **Yuen's trimmed-mean test**: not a good default in the same simulation (Delacre 2017); choose it only when the claim is about trimmed means.

**Validity conditions and how to check**

| Condition | Check without a gatekeeping test |
|---|---|
| Independence of units (all families) | Argue from the design: how units were drawn or assigned. Repeated or clustered units go to the mixed-model family. |
| Approximate normality of the mean's sampling distribution (Welch) | Look at the sample (histogram, QQ-plot) for heavy tails or strong skew; with small n and strong skew, run a robustness simulation from a plausible skewed distribution at your n and group ratio. Do not run a Shapiro-Wilk test and then choose the test by its p-value: in a simulation, a pretest at alpha .10 on exponential data at n=30 moved the t test's conditional Type I error to 17.0% against 4.7%. Source: Rochon, Gondan and Kieser 2012, BMC Med Res Methodol 12:81, doi:10.1186/1471-2288-12-81 (the authors do not endorse the two-stage approach). |
| Equal variances (Student, classical F only) | Not needed for Welch. If you must use the pooled test, equal group sizes make it tolerant; otherwise switch. Levene and Brown-Forsythe are less sensitive to non-normality than Bartlett, but remain pretests (NIST/SEMATECH e-Handbook of Statistical Methods, section 1.3.5.10, Levene test). |
| Commensurable, untied differences (signed-rank) | Argue from the measurement scale; count ties. |
| Exchangeability under the null (rank-sum, permutation) | Argue from the randomisation. Without random assignment, say what exchangeability would mean and why it is plausible. |

A different outcome shape (ordinal with few levels, counts, proportions) belongs to the families below. What is the case here that the table does not name?

## Proportions and contingency

**Default (2x2 independent groups): the chi-squared test on the table, with expected counts read from the table, not a fixed cut-off of 5.** Compute the expected counts and look at them. A comparison of methods found the "N-1" chi-squared (the usual statistic scaled by (N-1)/N) acceptable whenever the smallest expected count is at least 1, and that the traditional "all expected counts at least 5" rule is arbitrary; below that threshold it recommends the Fisher-Irwin test (abstract-level claim). Source: Campbell 2007, Stat Med, doi:10.1002/sim.2832.

**Alternatives and the property that favours each**

- **Fisher's exact test** is not the safe fallback it appears. It conditions on both margins, which most designs do not fix, and is conservative. Lydersen, Fagerland and Laake conclude that unconditional tests and the mid-p version of Fisher's test are preferable and that the traditional Fisher test should hardly ever be used (abstract-level claim). Source: Stat Med 2009, doi:10.1002/sim.3531. Choose Fisher's exact test when both margins are fixed by design (the tea-tasting layout), and say so.
- **Confidence interval for the difference or ratio of proportions** when the claim is about size. Report an interval for the effect measure the question needs (risk difference, risk ratio, odds ratio); the test of a table and its interval can disagree in small samples, so choose the interval method for its coverage, with a source you opened.
- **Paired binary outcomes** (the same unit measured twice): McNemar's test on the discordant pairs; see "ML and benchmark comparisons" for the exact version and its use.
- **Ordered categories (more than two levels)**: use the ordinal model below, not the unordered chi-squared, which discards the order.
- **Larger tables**: the same expected-count reading applies; report standardised cell residuals to say where the association sits.

**Validity conditions and how to check**

| Condition | Check |
|---|---|
| Independent units, one count per unit | Argue from the design. Several observations per subject make the unit the subject; use a mixed model or GEE. |
| Adequate expected counts | Read the expected-count table (for example `expected_freq` returned by scipy's `chi2_contingency`, scipy documentation). Where the minimum falls below the source's threshold, switch method; do not drop cells. |
| Margins fixed or free (decides conditional vs unconditional test) | Read it off the design: what was fixed in advance. |

## Association and agreement

Agreement and association are different questions. A correlation of 0.95 can sit beside a systematic offset of one unit: correlation measures the linear relation, not agreement. Settle which claim you make first.

**Default for association between two continuous variables**: report the estimate with an interval and a scatter plot; pick Pearson (linear) or a rank correlation (monotone, or ordinal data) by the shape you expect from the mechanism. Condition checks are plots, not tests: look for outliers that drive r, curvature, and range restriction. Do not read r as agreement.

**Default for agreement between two methods on a continuous scale: Bland-Altman limits of agreement.** The limits are the interval that holds about 95% of the between-method differences. The method does not say whether the limits are acceptable: set the acceptable limit before collecting data, from the clinical or scientific purpose, then compare. Passing-Bablok and Deming regression are alternatives when the question is about a systematic or proportional difference between methods. Source: Giavarina 2015, Biochem Med, doi:10.11613/BM.2015.015, PMC4470095.

**Alternatives and the property that favours each**

- **Intraclass correlation (continuous ratings by several raters)**: ten forms exist, each with different assumptions (model, type, definition). Specify the form in the plan. A confidence interval, not the point estimate, decides the band (below 0.5 poor, 0.5-0.75 moderate, 0.75-0.9 good, above 0.9 excellent, per the cited guideline). Source: Koo and Li 2016, J Chiropr Med, doi:10.1016/j.jcm.2016.02.012 (abstract-level claim).
- **Cohen's kappa (two raters, categorical)**: corrects raw agreement for chance. Common benchmark tables are too lenient for health work; and kappa depends on category prevalence, so report the table and raw agreement too. Pearson r can over- or under-state agreement. Source: McHugh 2012, Biochem Med, PMC3900052.

**Validity conditions and how to check**

| Condition | Check |
|---|---|
| Bland-Altman: differences roughly constant in size across the measurement range | Plot differences against the mean of the two methods; a trend or a fan means the limits are not one number (log-transform or model the trend). |
| Bland-Altman: acceptable limits set a priori | Show the preregistered limit in the plan. |
| ICC form matches the design (raters fixed or sampled, single or mean of ratings) | Argue from the design and name the form. |
| Kappa: prevalence and rater marginals not extreme | Read the 2x2 or k x k table. |

Which agreement question in your study is none of these (agreement across many raters, within-subject repeatability, agreement of time-to-event predictions)? Search for it and cite.

## Regression and GLM (ordinal, count, zero-inflated)

**Default: pick the model by the outcome's type and its mean-variance link, then report effects with intervals.** Linear model for a continuous outcome with roughly constant spread; logistic for binary; Poisson for counts; Cox for time-to-event (see Survival). The default is a starting point whose assumptions you then examine.

**Binary outcomes and sample size.** "Ten events per variable" is a floor from one simulation, not a guarantee. In that simulation (logistic regression), coefficients were biased, intervals had poor coverage, and Wald tests were conservative under the null when events per variable fell below 10; at 10 or more no major problems appeared. Source: Peduzzi et al. 1996, J Clin Epidemiol, doi:10.1016/s0895-4356(96)00236-3 (abstract-level claim). For prediction-model development, events per variable is not an appropriate criterion; sample size should come from the expected shrinkage and precision targets. Sources: van Smeden et al. 2019, Stat Methods Med Res, doi:10.1177/0962280218784726, PMC6710621; Riley et al. 2019, Stat Med, doi:10.1002/sim.7992.

**Alternatives and the property that favours each**

- **Ordinal outcome: proportional odds model** (generalises Wilcoxon and Kruskal-Wallis to adjusted analysis). Its assumption is one common odds ratio across all cut-points. Check graphically, and show the impact by comparing predicted probabilities against a model that relaxes it (multinomial or partial proportional odds). Source: Harrell, Regression Modeling Strategies, ordinal chapter, https://hbiostat.org/rmsc/ordinal.html.
- **Counts: Poisson, then quasi-Poisson or sandwich errors, then negative binomial.** Poisson assumes variance equals the mean. When variance is larger (over-dispersion), the standard errors are too small: quasi-Poisson or sandwich covariance correct them without a new mean model; negative binomial changes the variance function and is the better fit when the dispersion grows with the mean.
- **Excess zeros: hurdle or zero-inflated model.** A hurdle model treats zero as a separate process from the positive counts; a zero-inflated model mixes a point mass at zero with a count distribution, so the zero-inflation is a latent class and needs a story from the mechanism. Both handle over-dispersion and excess zeros; compare the fitted zero count with the observed one. Source: Zeileis, Kleiber and Jackman 2008, J Stat Softw 27(8).
- **Offsets and exposure**: counts of events over unequal exposure need a log-exposure offset; this is a design fact, not a diagnostic outcome.

**Validity conditions and how to check**

| Condition | Check |
|---|---|
| Correct mean-variance relation | Simulation-based scaled residuals (DHARMa) detect over- or under-dispersion, zero-inflation and residual autocorrelation for GLMs and mixed GLMs (DHARMa package vignette). Compare observed and simulated zeros. |
| Linearity on the link scale | Partial-residual or spline plot against each continuous predictor. |
| Independence | Argue from the design; plot residuals against cluster, time or space. |
| Events per variable or sample size adequate | Compute from the sources above before collecting data, not after. |
| Proportional odds (ordinal) | Predicted-probability comparison with a relaxed model, as above. |
| Influence of single points | Leave-one-out change in the estimate; report if it matters. |

Does your outcome follow none of these (a bounded proportion, a semicontinuous cost, a multivariate response)? Describe it by its axes, search, and cite.

## Mixed models and GEE

**Default when units share a source (subjects, litters, sites, batches, seeds): a mixed model whose random effects mirror the design, fitted by REML, with small-sample degrees of freedom (Kenward-Roger or Satterthwaite).** Pseudoreplication, treating non-independent observations as independent, is a design error, not a modelling refinement: reporting n, the degrees of freedom and the test statistic makes it detectable, and mixed models are the preferred remedy (Lazic 2010, BMC Neurosci, doi:10.1186/1471-2202-11-5). A likelihood-ratio test or a t-as-z test is anti-conservative for small samples; REML with Kenward-Roger or Satterthwaite gave acceptable Type I error in the simulations reported (Luke 2017, Behav Res Methods, doi:10.3758/s13428-016-0809-y, abstract-level claim).

**Alternatives and the property that favours each**

- **Random-effects structure**: "keep it maximal", the maximal structure the design justifies, is one position (Barr et al. 2013, J Mem Lang, doi:10.1016/j.jml.2012.11.001, abstract-level claim). A maximal model may lose power, and a model chosen by a selection criterion gave more power without Type I inflation in another simulation (Matuschek et al. 2017, J Mem Lang, arXiv:1511.01864). Decide from the design and the data size, record the decision, and run the alternative structure as a sensitivity analysis; if the two disagree, say so.
- **GEE (population-average effects)** when the claim is about the average effect across the population rather than within a subject, when the correlation structure is a nuisance, and when there are many clusters. A mixed model estimates subject-specific effects; the two answer different questions, and for non-linear links their coefficients differ. One review argues mixed models rest on assumptions that cannot be verified (Hubbard et al. 2010, Epidemiology, doi:10.1097/ede.0b013e3181caeb90, abstract-level claim).
- **Few clusters make GEE's robust variance biased downward**; bias-reduced linearisation with a Satterthwaite approximation helps (Pustejovsky and Tipton, arXiv:1601.01981, abstract-level claim). With few clusters (single-digit), a cluster-level analysis or a mixed model with small-sample correction is safer.
- **Repeated measures ANOVA vs multilevel model**: sphericity violations are corrected in rANOVA by Greenhouse-Geisser or Huynh-Feldt; a multilevel model with an unstructured covariance matrix showed massive progressive bias at n=20 with six or more occasions, and suits larger n (Haverkamp and Beauducel 2017, arXiv:1704.07638, abstract-level claim). Choose the covariance structure from the design and n, not from a sphericity test.

**Validity conditions and how to check**

| Condition | Check |
|---|---|
| Random effects represent every source of non-independence in the design | Argue from the design: list the sampling levels; every level with replicates enters. |
| Enough clusters for the variance components and the inference | Count them. Few levels of a random factor gives an unstable variance estimate; treat it as fixed or use a correction. |
| Residual and random-effect distributions reasonable | QQ-plots of residuals and of conditional modes; simulated-residual diagnostics (see DHARMa above). |
| Small-sample inference corrected | State the df method in the plan. |
| Convergence and singular fit | Read the fit messages; a singular fit means the structure is more complex than the data support, so simplify by the design's logic, not by chasing p-values. |
| GEE: working correlation matters little, robust variance reliable | Many clusters; compare robust and model-based standard errors as a diagnostic. |

Which dependence in your design is neither nested, crossed nor serial? Search for it and cite.

## Survival

**Default: Kaplan-Meier curves with a Cox proportional-hazards model, reported as hazard ratios with intervals and the number of events.** Power depends on the number of events, not on the number of participants, and about 10 events per covariate is a floor from the literature (Bradburn et al. 2003, Part III, Br J Cancer, doi:10.1038/sj.bjc.6601120, PMC2376927).

**Alternatives and the property that favours each**

- **Restricted mean survival time (RMST)** when proportional hazards is in doubt or the claim is about time gained within a window. Fix the time horizon before the analysis. Source: Royston and Parmar 2013, BMC Med Res Methodol 13:152, doi:10.1186/1471-2288-13-152.
- **Competing risks (cumulative incidence function)** when another event prevents the one of interest (death before relapse). One minus Kaplan-Meier overestimates incidence there. Cause-specific hazards suit etiologic questions; models of the cumulative incidence suit absolute-risk questions. Conventional methods assume non-informative censoring. Source: Austin, Lee and Fine 2016, Circulation, doi:10.1161/CIRCULATIONAHA.115.017719, PMC4741409.
- **Time-dependent or non-proportional models** when the hazard ratio changes over time (fit a time-dependent coefficient or a non-PH model).

**Validity conditions and how to check**

| Condition | Check |
|---|---|
| Proportional hazards | Plot scaled Schoenfeld residuals against time; if the trend is not flat, fit a time-dependent or non-PH model or switch to RMST. |
| Non-informative censoring | Argue from the design: why would a participant's departure be unrelated to prognosis? Sensitivity analysis under bounding assumptions. |
| Enough events | Count events against the covariates (rule above); penalise or simplify if short. |
| Independence | Clustered units (centres, litters) need a frailty or robust-variance term. |
| Competing events handled | Name them in the plan and choose the estimand (cause-specific or cumulative incidence). |

What event-time structure in your study is not here (recurrent events, interval censoring, a cured fraction)? Search for it and cite.
