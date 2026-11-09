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
- Time series and autocorrelation
- Circular data
- Compositional data
- High-dimensional data (LASSO, elastic net, inference after selection)
- Equivalence and non-inferiority
- Bayesian alternatives
- Multiple testing
- Meta-analysis
- ML and benchmark comparisons
- When nothing fits

## How to use this map

This file is a sample, not a menu. It names the families most studies meet, and for each one the usual default, the properties that make an alternative fit better, and the validity conditions with a way to check each. A situation outside the sample is normal, not a failure.

Go beyond the map when your situation calls for it:

1. Use what you know. A method you remember is a candidate, never a decision.
2. Confirm it by search (web or paper search): find a primary source that states the method's validity conditions and that fits your situation's axes (next section).
3. Cite what you read in the plan, next to the validity evidence. A method taken from memory without that check is not acceptable, because the failure is silent: the test runs and returns a p-value either way.

A source marked "(abstract only)" supports the claim as its abstract states it; open the paper before relying on details the abstract does not give.

Every entry follows one shape: when it fits, what separates it from its neighbours, validity conditions each with how to check it, and a source. Prove validity by an argument from the design, a diagnostic, a robustness simulation, or a cited result. Do not prove it with a significance test run on the same data you are about to analyse: the pretest has its own error rates, and the main test's error rates become conditional on it passing (see the normality row in the validity table under Location and scale). A diagnostic you read as a plot or an estimate (expected counts, a residual plot, an intraclass correlation) is not a gatekeeping test.

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
- **Missing data mechanism**: complete-case analysis and GEE (with an independence or simple working correlation) are valid when data are missing completely at random (MCAR); likelihood-based mixed models are valid when data are missing at random given the modelled covariates and outcomes (MAR). Argue the mechanism from the design (why a value is absent) and run a sensitivity analysis under a departure from it. The data alone cannot distinguish MAR from missing not at random.

State the axes in the plan in one line each. A reader who sees them can check that the family chosen matches.

## Location and scale

**Default: Welch's t-test (two groups), Welch's ANOVA (several groups).** Use Welch rather than Student's pooled test even when the variances look equal. Student's test is conservative when the larger variance goes with the larger group and liberal when it goes with the smaller one (nominal 0.05 became about 0.028 and 0.083 in the simulation reported), and tolerant only with equal group sizes. Welch holds near-nominal error from about 10 per group and loses little when the variances are equal. The choice is made by design, so no variance pretest is needed, and a Levene-type pretest has low power and makes the main test's error conditional on its result.
Source: Delacre, Lakens and Leys 2017, Int Rev Soc Psychol, doi:10.5334/irsp.82; for ANOVA, Delacre et al. 2019, doi:10.5334/irsp.198 (the Welch W test outperforms F when variances differ and is slightly less efficient when they are equal and the data non-normal).

**Alternatives and the property that favours each**

- **Mann-Whitney / Wilcoxon rank-sum** when the question is about stochastic ordering, P(X<Y) against P(Y<X), or the outcome is ordinal or heavily outlier-prone. It does not test medians, and it is not a safe replacement for Welch under unequal variances: it needs exchangeability under the null and for a medians reading it needs equal spread; its Type I error can be inflated even at large n when that fails. If you want the stochastic-ordering claim without the equal-spread requirement, use Brunner-Munzel (a permutation version is weakly favoured); its power is about that of Mann-Whitney, apart from skewed data with unequal n, where Mann-Whitney has a small advantage. Source: Karch 2021, Adv Methods Pract Psychol Sci, doi:10.1177/2515245921999602.
- **Wilcoxon signed-rank** for paired differences when the t-test's assumptions are doubtful. It assumes the differences are commensurable (a difference of 5 means the same anywhere on the scale) and continuous (not rounded to ties), and under the null they are symmetric about zero. When the paired t-test's assumptions do hold, signed-rank is less powerful. Source: Demšar 2006, JMLR 7:1-30.
- **Permutation test** when the design supplies exchangeability (random assignment) and the statistic you care about has no convenient null distribution. Count the observed arrangement among the permutations: a permutation p-value of exactly zero is never correct (use (b+1)/(m+1) or the exact count). Source: Phipson and Smyth 2010, Stat Appl Genet Mol Biol, arXiv:1603.05766.
- **Yuen's trimmed-mean test**: not a good default in the same simulation (Delacre 2017); choose it only when the claim is about trimmed means.

**Validity conditions and how to check**

| Condition | Check without a gatekeeping test |
|---|---|
| Independence of units (all families) | Argue from the design: how units were drawn or assigned. Repeated or clustered units go to the mixed-model family. |
| Approximate normality of the mean's sampling distribution (Welch) | Look at the sample (histogram, QQ-plot) for heavy tails or strong skew; with small n and strong skew, run a robustness simulation from a plausible skewed distribution at your n and group ratio. Do not run a Shapiro-Wilk test and then choose the test by its p-value: in one simulation (pooled t test after a Shapiro-Wilk pretest at alpha .10, exponential data, n=30 per group) the t test's conditional Type I error was 17.0% against 4.7% without the pretest. The overall Type I error of the whole two-stage procedure stayed near nominal, so the damage is to the conditional error of the test you report, and the authors still do not endorse the two-stage approach. Source: Rochon, Gondan and Kieser 2012, BMC Med Res Methodol 12:81, doi:10.1186/1471-2288-12-81. |
| Equal variances (Student, classical F only) | Not needed for Welch. If you must use the pooled test, equal group sizes make it tolerant; otherwise switch. Levene and Brown-Forsythe are less sensitive to non-normality than Bartlett, but remain pretests (NIST/SEMATECH e-Handbook of Statistical Methods, section 1.3.5.10, Levene test). |
| Commensurable, untied, symmetric differences (signed-rank) | Argue from the measurement scale; count ties; plot the differences (histogram or QQ-plot) to read their symmetry. |
| Exchangeability under the null (rank-sum, permutation) | Argue from the randomisation. Without random assignment, say what exchangeability would mean and why it is plausible. |

A different outcome shape (ordinal with few levels, counts, proportions) belongs to the families below. What is the case here that the table does not name?

## Proportions and contingency

**Default (2x2 independent groups): the chi-squared test on the table, with expected counts read from the table, not a fixed cut-off of 5.** Compute the expected counts and look at them. A comparison of methods found the "N-1" chi-squared (the usual statistic scaled by (N-1)/N) acceptable whenever the smallest expected count is at least 1, and that the traditional "all expected counts at least 5" rule is arbitrary; below that threshold it recommends the Fisher-Irwin test (abstract only). Source: Campbell 2007, Stat Med, doi:10.1002/sim.2832.

**Alternatives and the property that favours each**

- **Fisher's exact test** is not the safe fallback it appears. It conditions on both margins, which most designs do not fix, and is conservative. Lydersen, Fagerland and Laake conclude that unconditional tests and the mid-p version of Fisher's test are preferable and that the traditional Fisher test should hardly ever be used (abstract only). Source: Stat Med 2009, doi:10.1002/sim.3531. Choose Fisher's exact test when both margins are fixed by design (the tea-tasting layout), and say so.
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

Which table in your study is none of these (sparse many-category tables, matched sets, tables with structural zeros)? Describe it by its axes, search, and cite.

## Association and agreement

Agreement and association are different questions. A correlation of 0.95 can sit beside a systematic offset of one unit: correlation measures the linear relation, not agreement. Settle which claim you make first.

**Default for association between two continuous variables**: report the estimate with an interval and a scatter plot; pick Pearson (linear) or a rank correlation (monotone, or ordinal data) by the shape you expect from the mechanism. Condition checks are plots, not tests: look for outliers that drive r, curvature, and range restriction. Do not read r as agreement.

**Default for agreement between two methods on a continuous scale: Bland-Altman limits of agreement.** The limits are the interval that holds about 95% of the between-method differences. The method does not say whether the limits are acceptable: set the acceptable limit before collecting data, from the clinical or scientific purpose, then compare. Passing-Bablok and Deming regression are alternatives when the question is about a systematic or proportional difference between methods. Source: Giavarina 2015, Biochem Med, doi:10.11613/BM.2015.015, PMC4470095.

**Alternatives and the property that favours each**

- **Intraclass correlation (continuous ratings by several raters)**: ten forms exist, each with different assumptions (model, type, definition). Specify the form in the plan. A confidence interval, not the point estimate, decides the band (below 0.5 poor, 0.5-0.75 moderate, 0.75-0.9 good, above 0.9 excellent, per the cited guideline). Source: Koo and Li 2016, J Chiropr Med, doi:10.1016/j.jcm.2016.02.012 (abstract only).
- **Cohen's kappa (two raters, categorical)**: corrects raw agreement for chance. Common benchmark tables are too lenient for health work; and kappa depends on category prevalence, so report the table and raw agreement too. Pearson r can over- or under-state agreement. Source: McHugh 2012, Biochem Med, PMC3900052.

**Validity conditions and how to check**

| Condition | Check |
|---|---|
| Bland-Altman: differences roughly constant in size across the measurement range | Plot differences against the mean of the two methods; a trend or a fan means the limits are not one number (log-transform or model the trend). |
| Bland-Altman: differences approximately normal (the 95% interval reading rests on it) | QQ-plot or histogram of the differences, read as a diagnostic, not as a gate. |
| Bland-Altman: limits estimated with their uncertainty | Report a confidence interval for each limit of agreement, and compare the outer ends, not the point estimates, with the acceptable limit. |
| Bland-Altman: acceptable limits set a priori | Show the preregistered limit in the plan. |
| ICC form matches the design (raters fixed or sampled, single or mean of ratings) | Argue from the design and name the form. |
| Kappa: prevalence and rater marginals not extreme | Read the 2x2 or k x k table. |

Which agreement question in your study is none of these (agreement across many raters, within-subject repeatability, agreement of time-to-event predictions)? Search for it and cite.

## Regression and GLM (ordinal, count, zero-inflated)

**Default: pick the model by the outcome's type and its mean-variance link, then report effects with intervals.** Linear model for a continuous outcome with roughly constant spread; logistic for binary; Poisson for counts; Cox for time-to-event (see Survival). The default is a starting point whose assumptions you then examine.

**Binary outcomes and sample size.** "Ten events per variable" is a floor from one simulation, not a guarantee. In that simulation (logistic regression), coefficients were biased, intervals had poor coverage, and Wald tests were conservative under the null when events per variable fell below 10; at 10 or more no major problems appeared. Source: Peduzzi et al. 1996, J Clin Epidemiol, doi:10.1016/s0895-4356(96)00236-3 (abstract only). For prediction-model development, events per variable is not an appropriate criterion; sample size should come from the expected shrinkage and precision targets. Sources: van Smeden et al. 2019, Stat Methods Med Res, doi:10.1177/0962280218784726, PMC6710621; Riley et al. 2019, Stat Med, doi:10.1002/sim.7992.

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

**Default when units share a source (subjects, litters, sites, batches, seeds): a mixed model whose random effects mirror the design, fitted by REML for a linear mixed model, with small-sample degrees of freedom (Kenward-Roger or Satterthwaite).** Pseudoreplication, treating non-independent observations as independent, is a design error, not a modelling refinement: reporting n, the degrees of freedom and the test statistic makes it detectable, and mixed models are the preferred remedy (Lazic 2010, BMC Neurosci, doi:10.1186/1471-2202-11-5). A likelihood-ratio test or a t-as-z test is anti-conservative for small samples; REML with Kenward-Roger or Satterthwaite gave acceptable Type I error in the simulations reported (Luke 2017, Behav Res Methods, doi:10.3758/s13428-016-0809-y, abstract only). Those corrections are for linear mixed models. A likelihood-ratio comparison of models that differ in fixed effects needs ML fits, because REML likelihoods of models with different fixed effects are not comparable. For a generalised linear mixed model (GLMM) the Kenward-Roger adjustment is an ad hoc procedure outside its derivation (informally found accurate), `glmer`-type fits are not REML, and the options are a likelihood-ratio test, a parametric bootstrap (simulate from the reduced model, refit both, and compare the deviance differences) or a profile or bootstrap interval. Source: Bolker et al., GLMM FAQ, https://bbolker.github.io/mixedmodels-misc/glmmFAQ.html.

**Alternatives and the property that favours each**

- **Random-effects structure**: "keep it maximal", the maximal structure the design justifies, is one position (Barr et al. 2013, J Mem Lang, doi:10.1016/j.jml.2012.11.001, abstract only). A maximal model may lose power, and a model chosen by a selection criterion gave more power without Type I inflation in another simulation (Matuschek et al. 2017, J Mem Lang, arXiv:1511.01864). Decide from the design and the data size, record the decision, and run the alternative structure as a sensitivity analysis; if the two disagree, say so.
- **GEE (population-average effects)** when the claim is about the average effect across the population rather than within a subject, when the correlation structure is a nuisance, and when there are many clusters. A mixed model estimates subject-specific effects; the two answer different questions, and for non-linear links their coefficients differ. One review argues mixed models rest on assumptions that cannot be verified (Hubbard et al. 2010, Epidemiology, doi:10.1097/ede.0b013e3181caeb90, abstract only).
- **Few clusters make GEE's robust variance biased downward**; bias-reduced linearisation with a Satterthwaite approximation helps (Pustejovsky and Tipton, arXiv:1601.01981, abstract only). With few clusters (single-digit), a cluster-level analysis or a mixed model with small-sample correction is safer.
- **Repeated measures ANOVA vs multilevel model**: sphericity violations are corrected in rANOVA by Greenhouse-Geisser or Huynh-Feldt; a multilevel model with an unstructured covariance matrix showed massive progressive bias at n=20 with six or more occasions, and suits larger n (Haverkamp and Beauducel 2017, arXiv:1704.07638, abstract only). Choose the covariance structure from the design and n, not from a sphericity test.

**Validity conditions and how to check**

| Condition | Check |
|---|---|
| Random effects represent every source of non-independence in the design | Argue from the design: list the sampling levels; every level with replicates enters. |
| Enough clusters for the variance components and the inference | Count them. Few levels of a random factor gives an unstable variance estimate; treat it as fixed or use a correction. |
| Residual and random-effect distributions reasonable | QQ-plots of residuals and of conditional modes; simulated-residual diagnostics (see DHARMa above). |
| Small-sample inference corrected | State the df method in the plan; for a GLMM name the method (parametric bootstrap, likelihood ratio) and why it holds at your number of clusters. |
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

## Time series and autocorrelation

**Default: model the serial structure, then check that the residuals carry none.** For forecasting-style models, innovation residuals should be uncorrelated: read the autocorrelation plot and add a portmanteau test (Box-Pierce or Ljung-Box) as a summary, with lag 10 for non-seasonal data, 2m for seasonal data of period m, capped at T/5. Here the test is a diagnostic on a fitted model, not a gate before choosing it. Source: Hyndman and Athanasopoulos, Forecasting: Principles and Practice (3rd ed.), section on residual diagnostics, https://otexts.com/fpp3/diagnostics.html.

**Alternatives and the property that favours each**

- **Interrupted time series (segmented regression)** when an intervention starts at a known time and the claim is a change in level or slope. Propose the impact model (immediate, delayed, slope change) before looking at the data; there is no fixed minimum number of points, so argue from the expected effect and the noise. Autocorrelation is checked by residual plot, partial autocorrelation and the Breusch-Godfrey test, and handled by a Prais-type correction or ARIMA errors. A control series or a multiple-baseline design addresses time-varying confounders that a single series cannot. Source: Bernal, Cummins and Gasparrini 2017, Int J Epidemiol, doi:10.1093/ije/dyw098.
- **Heteroskedasticity- and autocorrelation-consistent (HAC) covariance** when the mean model is right and only the standard errors are the problem. It corrects inference, not a misspecified mean. Source: Zeileis 2004, J Stat Softw 11(10).
- **Ordinary regression on serial data** fails because the nominal sample size overstates the information: neighbouring points repeat each other. That is why the residual check matters.

**Validity conditions and how to check**

| Condition | Check |
|---|---|
| Stationarity or an explicit trend/seasonal model | Plot the series and the ACF; difference or model the trend by argument from the mechanism, not by a unit-root pretest alone. |
| Uncorrelated innovations | ACF plot of residuals, then the portmanteau summary at the lags above. |
| Impact model specified in advance (ITS) | The plan states it before data are seen. |
| No concurrent event at the break | Argue from the design; add a control series where one exists. |

Which temporal feature of your data is not here (irregular sampling, structural breaks, long memory)? Search for it and cite.

## Circular data

**Default: Rayleigh test for a unimodal departure from uniformity with an unknown mean direction.** Use the V-test only when the direction is specified before the data. In simulations of circular tests, Rao's spacing test performed worst for unimodal alternatives; for multimodal departures the Hermans-Rasson test performed well, but with symmetric multiple modes all tests perform poorly, and doubling the angles helps only for perfect f-fold symmetry. Source: Landler, Ruxton and Malkemper 2018, Behav Ecol Sociobiol, doi:10.1007/s00265-018-2538-y.

**Why a linear test fails here**: angles have no origin (359 degrees is near 1 degree), so a linear mean or standard deviation (SD) of angles describes nothing. Use circular summaries (mean resultant length, circular mean).

| Condition | Check |
|---|---|
| Alternative is unimodal (Rayleigh) | Plot the data on the circle; if it looks bimodal, use a test aimed at multimodal departures. |
| Direction prespecified (V-test) | The plan fixes it before data. |
| Independent angles | Argue from the design: repeated trials of one animal are not independent. |

Is your circular question a comparison of groups or a regression on angles? That needs its own source: search and cite.

## Compositional data

**Default: analyse log-ratios, not raw proportions.** Parts of a whole sum to a constant, so raw components show a negative correlation bias and spurious correlation, and the apparent correlation changes when you subset the parts. Differential-abundance questions must account for compositionality; the centred log-ratio (clr) transformation is one standard tool. Source: Gloor et al. 2017, Front Microbiol, doi:10.3389/fmicb.2017.02224.

**Alternatives and the property that favours each**

- **Pairwise or additive log-ratios** when a stable reference part exists and the claim is about the ratio to it.
- **Power transformations** when many exact zeros make log-ratios awkward; the work on Aitchison's approach argues that subcompositional coherence (quasi-coherence) is what matters, that power transformations allow zeros, and that isometric log-ratios are not a prerequisite. Source: Greenacre et al., arXiv:2201.05197 (abstract only).

| Condition | Check |
|---|---|
| Zeros handled by a stated, justified rule | Count zeros per part; report how they were treated and run the analysis under a second treatment as sensitivity. |
| Question stated for ratios, not absolute amounts | Argue from the design: relative data cannot support a claim about absolute change without an external anchor. |

What composition in your study is not a simple sum-to-one (spatial, multi-level)? Search and cite.

## High-dimensional data (LASSO, elastic net, inference after selection)

**Default for prediction with many predictors: penalised regression with the penalty chosen by cross-validation, with performance estimated on data that played no part in the selection.** The elastic net is the usual choice over LASSO when predictors are correlated: the LASSO selects at most n variables when p exceeds n and tends to keep one of a group of highly correlated predictors, while the elastic net has a grouping effect (Zou and Hastie 2005, J R Stat Soc B, https://hastie.su.domains/Papers/elasticnet.pdf).

**The warning that decides everything: inference after selection.** A p-value or interval computed as if the selected model had been chosen in advance has none of the classical guarantees, because the data chose the hypothesis. Valid routes:

- **Sample splitting**: select on one part, test on the other. Valid conditional on the model selected on the first half, at the cost of power; one split is a "p-value lottery", so aggregate across splits (Meinshausen, Meier and Buhlmann 2009, arXiv:0811.2177); or screen, cross-validate, then test on held-out data (Wasserman and Roeder 2009, arXiv:0704.1139).
- **Selective inference**: exact inference for the LASSO conditioned on the selection event (Lee, Sun, Sun and Taylor 2016, arXiv:1311.6238).
- **Simultaneous inference over all submodels** (PoSI): valid, and conservative (Berk et al., arXiv:1306.1059, abstract only). A review of the options: Dezeure et al., arXiv:1408.4026 (abstract only).

**Selection also biases performance estimates.** Tuning and choosing the model on the same folds you report over-fits the selection criterion; use nested cross-validation or a held-out set (Cawley and Talbot 2010, JMLR 11, abstract only).

| Condition | Check |
|---|---|
| The inference claim and the selection are separated | The plan names which data select and which data test, or which selective method is used. |
| Penalty tuned without leaking test information | Nested resampling or a held-out set; read the code path. |
| Sparsity plausible (LASSO), or grouped signal (elastic net) | Argue from the mechanism; compare selection stability across resamples. |

Does your goal differ (causal effect with many confounders, structured sparsity)? Search and cite.

## Equivalence and non-inferiority

**Default: two one-sided tests (TOST) against margins set from the smallest effect size of interest (SESOI).** Equivalence is concluded if the 90% confidence interval for the difference lies inside the bounds, which is the same decision as two one-sided tests at the 5% level. A non-significant difference test is not evidence of equivalence. Source: Lakens 2017, Soc Psychol Personal Sci, doi:10.1177/1948550617697177 (PMC5502906).

- **Welch version of TOST** when variances differ (the Welch argument above applies). **Non-inferiority** is a single one-sided test against one margin, used when only one direction matters.
- **Power**: plan the sample size for the equivalence test, with the true effect possibly not zero; the cited paper gives power tables and the iteration needed.
- **The margin is the scientific decision.** It comes from the smallest effect that would matter, argued from the field, not from the sample's own spread. A margin chosen after seeing the data defeats the test.

| Condition | Check |
|---|---|
| Margins justified and set before analysis | The plan cites the reasoning for the SESOI. |
| Interval method valid for the data | Same conditions as the underlying difference test; apply that family's checks. |
| Equivalence on the right scale | State the margin on the scale of the claim (raw units, ratio). |

Which margin question here has no accepted SESOI? Say so in the plan and cite the nearest argument.

## Bayesian alternatives

**Default: posterior estimates with credible intervals, reported with the prior and a sensitivity analysis.** Bayes factors compare models and are sensitive to the prior in ways the posterior of a parameter is not: they depend heavily on prior assumptions, and are even more sensitive to them than within-model posteriors. Source: Schad et al. 2022, Workflow techniques for the robust use of Bayes factors, arXiv:2103.08744.

**Validity rests on**

- **Prior sensitivity**: refit under alternative reasonable priors, or use a static sensitivity analysis (perturbation of the prior without refit). If the conclusion flips, report the dependence, not one number. Source: Gelman et al. 2020, Bayesian workflow, arXiv:2011.01808.
- **Prior predictive checks**: simulate data from the prior to see that it does not rule out or overwhelm plausible data (same source; Schad et al.).
- **Model adequacy**: posterior predictive checks compare simulated replications with the data; a Bayes factor between two inadequate models still ranks them (same sources).
- **Computation**: run at least four chains, require the rank-normalised R-hat below 1.01 (the older 1.1 threshold can be met well before convergence), and require bulk and tail effective sample sizes above 400 (bulk-ESS resolves the centre of the distribution, tail-ESS the interval endpoints). Source: Vehtari et al., arXiv:1903.08008.
- **Calibration of the procedure**: simulation-based calibration checks that the sampler and the model recover the prior (Schad et al.).

A Bayesian analysis is not freed from error control: say what decision it supports and what rule you would use before the data arrive. Which part of your Bayesian model has no standard check? Search and cite.

## Multiple testing

**Default (confirmatory family of tests): Holm.** It is valid under arbitrary dependence and dominates Bonferroni. Hochberg and Hommel need independence or non-negative association among the tests. Source: R `p.adjust` documentation.

**Alternatives and the property that favours each**

- **Benjamini-Hochberg (BH)** when the goal is to control the false discovery rate among many exploratory findings rather than any false claim. BH controls the FDR under positive regression dependency on the true nulls (PRDS); for other dependence use the conservative Benjamini-Yekutieli procedure or a modification. Source: Benjamini and Yekutieli 2001, Ann Stat 29:1165. Choose the error rate the claim needs: familywise for each claim standing alone, FDR for a list of leads (Goeman and Solari 2014, Stat Med, doi:10.1002/sim.6082, abstract only).
- **Hierarchical, fixed-sequence or gatekeeping procedures** when endpoints are ordered by importance or structured (a primary before secondaries); graphical approaches allocate and pass on the error budget (Bretz et al. 2009, Stat Med, doi:10.1002/sim.3495, abstract only).

| Condition | Check |
|---|---|
| Family defined before looking at results | The plan lists the tests in the family and the error rate. |
| Dependence structure fits the procedure | Argue from the design: are tests positively related (same units, same direction) or arbitrary? If unsure, choose the procedure valid under arbitrary dependence. |
| Order or hierarchy set a priori (gatekeeping) | State the order in the plan. |

A set of tests that does not form one family (several studies, several aims)? Say how you drew the line and cite.

## Meta-analysis

**Default: a random-effects model with the Hartung-Knapp-Sidik-Jonkman (HKSJ) interval, a stated tau-squared estimator (REML or Paule-Mandel), and a prediction interval.** A fixed-effect analysis is valid if all estimates estimate one common effect; otherwise its estimate may describe no real population and its interval is too narrow. A random-effects analysis assumes study effects are different but related, following a normal distribution, and must be read carefully. In simulations, the DerSimonian-Laird (DL) interval had Type I error rates that could exceed 30% when the nominal level was 5%, while HKSJ at most doubled them; extra caution is needed with 5 or fewer studies of very unequal sizes. The Cochrane chapter notes that several simulation studies recommend the Paule-Mandel estimator, that a later comprehensive simulation recommended REML with no single approach universally preferable, and that I-squared and tau-squared are very uncertain with few studies. Name the estimator in the plan. Sources: IntHout et al. 2014, BMC Med Res Methodol 14:25, doi:10.1186/1471-2288-14-25; Deeks et al., Cochrane Handbook for Systematic Reviews of Interventions, chapter 10.

**Heterogeneity.** Report tau-squared and a prediction interval (the range of true effects in a new setting). I-squared is ambiguous: a high value need not mean widely dispersed effects, because it depends on the studies' sizes. Estimates of I-squared and tau-squared are very uncertain with few studies. Source: IntHout et al. 2016, BMJ Open, doi:10.1136/bmjopen-2015-010247.

| Condition | Check |
|---|---|
| Studies comparable enough to pool | Argue from the question and the study designs; explain sources of heterogeneity in advance (subgroups, meta-regression), not after the forest plot. |
| Independent effect estimates | One estimate per participant group; handle multiple arms or outcomes by a stated rule. |
| Small-study effects and publication bias | Search the Cochrane chapter's guidance for your outcome type and cite what you apply; do not rely on one plot. |

Does your synthesis have dependent effects (many outcomes per study) or a network of treatments? Search and cite.

## ML and benchmark comparisons

**Default for comparing two models on one dataset: pair by seed, fold or example, and use a variance estimate that accounts for overlapping training sets.** The usual paired t-test on cross-validation results is miscalibrated because folds overlap; the correlation between the results of different folds cannot be estimated without bias (Nadeau and Bengio), so their corrected resampled t-test uses a heuristic: with J resamples (n in Benavoli's notation), the variance of the mean difference is estimated as sigma-squared times (1/J + n_te/n_tr), n_te and n_tr being the test and training sizes. Applied to k-fold cross-validation the correction remains a heuristic, so treat its p-value as approximate. Benavoli et al. recommend Bayesian correlated alternatives, and hierarchical ones across datasets. Source: Benavoli et al. 2017, JMLR 18, http://jmlr.org/papers/v18/16-305.html. In Dietterich's comparison, the difference-of-proportions test and the resampled paired t had high Type I error and 10-fold CV t was somewhat elevated; McNemar's test had low Type I error and suits algorithms run once, and 5x2cv is advised when ten runs are affordable (Dietterich 1998, Neural Comput, doi:10.1162/089976698300017197, abstract only).

**Alternatives and the property that favours each**

- **McNemar's test** when each model runs once on a test set: it uses only the discordant pairs (one right, other wrong). Use an exact binomial version when the discordant counts are small, but note that the exact conditional test is conservative: the mid-p version performed well in a comparison across 9595 scenarios, and the continuity-corrected asymptotic test did not (Fagerland, Lydersen and Laake 2013, BMC Med Res Methodol 13:91, doi:10.1186/1471-2288-13-91, abstract only). Source for the discordant-cell logic: Raschka 2018, arXiv:1811.12808.
- **Several datasets**: treat datasets as the independent units. Wilcoxon signed-rank for two classifiers, Friedman with post-hoc tests for more (Iman-Davenport correction makes it less conservative); resampling error within a dataset is not the issue there. The signed-rank test needs commensurable score differences across datasets. Source: Demšar 2006, JMLR 7:1-30.
- **Seed runs on one dataset**: the unit is one full training run (one seed), so n is the number of seeds, not the number of test examples or epochs. Pairing by seed is valid only if the seed fixes the same initialisation and data order for both methods; if it fixes one but not the other, treat the runs as unpaired (Welch). The inference concerns the training procedure on this data, not generalisation to other datasets: for that, use datasets as units (next entry). Sources: Colas et al. 2018, arXiv:1806.08295 (number of seeds, power, Welch when variances differ); Demšar 2006, JMLR 7:1-30 (datasets as the independent units).
- **Reinforcement-learning and few-run settings**: report interval estimates and the interquartile mean rather than a point estimate (Agarwal et al. 2021, arXiv:2108.13264, abstract only); the number of seeds determines power, and Welch's t-test applies when variances differ (Colas et al. 2018, arXiv:1806.08295).

| Condition | Check |
|---|---|
| Same splits, seeds or examples for both models | Read the experiment code; pairing is a design property. |
| Test data not used for tuning | Argue from the pipeline; separate tuning from testing. |
| Datasets chosen independently of the result | State the selection rule. |
| Run-to-run variance included | Repeat training with different seeds; report the spread. |

What comparison here has no test above (generative models, human evaluation, non-iid test streams)? Search and cite.

## When nothing fits

If no family matches, do not stretch the nearest one.

1. **Describe the situation by its axes** (question, outcome, dependence, groups, covariates, n and events, claim), in the plan's words, with the feature that made the families above fail.
2. **Search** with those axes as the query: textbooks, method papers, software documentation, a simulation study of the candidate method.
3. **Cite** what you opened. Prefer the paper that states the validity conditions over the one that introduces the name.
4. **Record the validity evidence in the plan**: the conditions, and for each the argument, diagnostic, simulation or cited result that shows it holds here. Where it cannot be shown, run a known-truth run on simulated data shaped like yours and report how the method behaved.
5. **Ask what would make the method wrong**, then look for that in the data you have before the confirmatory run.

A new situation usually combines axes seen above (clustered, zero-heavy, time-ordered). Start from the nearest family's validity table and ask which row no longer holds.
