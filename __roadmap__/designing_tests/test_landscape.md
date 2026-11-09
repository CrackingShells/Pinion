# Statistical test landscape

**Goal**: Research and write a situation-family map of statistical methods, past the textbook core, that teaches an agent to choose by the properties that discriminate between methods and to prove each method's validity conditions.
**Pre-conditions**:
- [ ] Working in a worktree on `task/designing-tests-test_landscape`, cut from `claude/test-design-skill-03d1cc`; every command below runs from the worktree root
- [ ] R01 §1c and §5 step 3 read in full, with the appendix's "Test choice" comment
- [ ] Web search and the arXiv tools are reachable (search once; if they are not, stop and report)
**Success Gates**:
- ⬜ `skills/designing-tests/references/science-test-landscape.md` opens with a `## Contents` list and a statement that it is a sample, not a menu, inviting a better-fitting method confirmed by a search and cited
- ⬜ Every method entry has fit, discriminating properties, validity conditions with how to check each, and a primary source the implementer actually opened
- ⬜ Every family names its usual default first, then alternatives with the property that would make each the better fit
- ⬜ The family list of R01 §5 step 3 is covered, including LASSO and elastic net with the warning that inference after selection needs selective inference or sample splitting
- ⬜ The standalone and banned-word grep over `skills/designing-tests` prints nothing
**References**: [R01 §5 step 3](../../__reports__/designing_tests/00-architecture_designing_tests_v0.md) — scope, entry format, core corrections

## Step 1: Frame and core families
**Goal**: Fix the map's frame and write the families most studies meet.
**Implementation Logic**:
Open with: what the map is for, that it is a sample and not a menu, and how to go beyond it (the agent's own knowledge, confirmed by a web or paper search, cited in the plan; a method from memory without that check is not acceptable). Then the discriminating axes the agent should read off its situation before opening a family: question type, outcome type, dependence structure (paired, repeated, nested, clustered), number of groups and factors, covariates, n and events, the claim (difference, equivalence, association, prediction).
Families in this step: location and scale; proportions and contingency; association and agreement; regression and GLM (including ordinal, count and zero-inflated); mixed models and GEE; survival.
Entry format, the same everywhere: when it fits; what distinguishes it from its neighbours; validity conditions, each with how to check it without a gatekeeping significance test on the same data (argument from the design, diagnostic, robustness simulation, cited result); a primary source (paper, textbook chapter or software documentation with a DOI or URL) that you opened and that says what the entry claims. Keep the core corrections explicit (for example Mann-Whitney tests stochastic dominance, not medians; Welch over Student by default; χ² expected counts; events per variable).
Research, do not recall: every source is one you read in this session. Keep each entry tight; the reader is a strong model that needs the discriminators and the conditions, not a tutorial.
**Deliverables**: `skills/designing-tests/references/science-test-landscape.md` (sections: Contents, how to use this map, reading your situation, location and scale, proportions and contingency, association and agreement, regression and GLM, mixed models and GEE, survival)
**Consistency Checks**: `p=skills/designing-tests/references/science-test-landscape.md; test -f $p && grep -q '^## Contents' $p && grep -qi 'not a menu' $p` (expected: PASS)
**Consistency Checks**: `! grep -riE 'writing-reports|managing-roadmaps|writing-history|writing-release|plumage|playbook|skill-creator|dataviz|waiting-on-processes|spawning-agent-plugins|invariant|deviation' skills/designing-tests` (expected: PASS)
**Commit**: `feat(designing-tests): map the core families of statistical tests`

## Step 2: Extended families
**Goal**: Extend the map to the less familiar situations.
**Implementation Logic**:
Same entry format and the same rule on sources. Families in this step: time series and autocorrelation; circular data; compositional data; high-dimensional data (LASSO and elastic net, with selective inference or sample splitting for inference after selection); equivalence and non-inferiority (TOST and its margins); Bayesian alternatives (Bayes factors, posterior intervals, and what their validity rests on: prior sensitivity, model adequacy); multiple testing (Holm, Benjamini–Hochberg and its dependence assumption, hierarchical or gatekeeping procedures); meta-analysis (fixed versus random effects, heterogeneity); ML and benchmark comparisons (pairing by seed or fold, the corrected resampled t-test, McNemar, multi-dataset comparison in the style of Demšar). End the file with what to do when no family fits: describe the situation by its axes, search, cite, and record the validity evidence in the plan.
**Deliverables**: `skills/designing-tests/references/science-test-landscape.md` (added sections: time series, circular, compositional, high-dimensional, equivalence, Bayesian, multiple testing, meta-analysis, ML and benchmark comparisons, when nothing fits)
**Consistency Checks**: `p=skills/designing-tests/references/science-test-landscape.md; for k in 'LASSO' 'elastic net' 'selective inference' 'TOST' 'Holm' 'Benjamini' 'meta-analysis' 'McNemar' 'compositional' 'circular' 'GEE' 'zero-inflated'; do grep -qi "$k" $p || { echo "missing $k"; exit 1; }; done` (expected: PASS)
**Consistency Checks**: `! grep -riE 'writing-reports|managing-roadmaps|writing-history|writing-release|plumage|playbook|skill-creator|dataviz|waiting-on-processes|spawning-agent-plugins|invariant|deviation' skills/designing-tests` (expected: PASS)
**Commit**: `feat(designing-tests): extend the test landscape to less familiar situations`
