# Showing results and explaining the design

Open this when planning the figures (before data), when producing them, and when writing what you
hand back to whoever ordered the analysis. Two aims: a result is visible whether it is good or bad,
and the design is understood by its recipient, not only reported to them.

## Contents

- Showing results
- Non-negotiables
- Explaining the design

## Showing results

These are guidelines about what a figure must make visible, not a list of plot types. Choose the
form that shows the data of this study; the procedure below says what it has to do, in the order to
do it.

1. **Fix the decision lines.** From the pattern-of-outcomes table
   ([science-questions-and-tests.md](science-questions-and-tests.md)), list the values that change
   the reading of a result: zero, the SESOI, the equivalence margins, a threshold of practical
   consequence. These become reference lines in the figures.
2. **Pre-specify the primary figures.** Say, in the analysis plan
   ([science-analysis-plan.md](science-analysis-plan.md)), which figure answers each statistical
   question and what it will show, before the data exist.
3. **Render them first on simulations.** Run the figure code on the known-truth datasets under H0
   and under the effect that matters ([science-protocol-and-sample.md](science-protocol-and-sample.md)).
   Everyone then knows what a null and a hit look like in this figure, and the code is debugged on
   data where the right picture is known. A figure whose null and effect versions look alike is
   the wrong figure.
4. **Show every unit.** Draw each unit (each animal, participant, run, seed) behind the summary:
   points, a strip or a beeswarm, a connected line per pair, small multiples when there are many.
   Summaries alone (a bar of means, a line with an error bar) can show the same picture for very
   different distributions (Weissgerber et al. 2015, PLOS Biology 13:e1002128, doi:10.1371/journal.pbio.1002128).
5. **Plot the effect with its uncertainty against the lines from step 1.** The estimate and its
   interval, on the scale of the estimand, with the lines drawn. An inconclusive result then looks
   inconclusive: the interval spans a line that decides. Say in the caption what the interval is
   (confidence level, method, the unit it is over).
6. **Show every pre-specified outcome**, nulls and failures included, in the order of the plan.
7. **Render the real data** with the same code, and compare with the simulated versions of step 3.
8. **Read it as a skeptic.** What could a reader take from this that the data do not support?
   Redraw until the wrong reading is hard to reach.

## Non-negotiables

Each is here because breaking it hides something the reader needs; the signal says how to notice.

- **Every unit is visible behind the estimate.** Reason: the estimate cannot show outliers,
  clusters, floor effects or a split population. Signal: a figure whose only marks are summaries.
- **The effect carries its uncertainty and the deciding lines.** Reason: without the interval a
  difference looks certain; without the lines the reader cannot tell whether it matters. Signal: a
  p-value or a star standing in for the estimate.
- **Every pre-specified outcome is shown.** Reason: showing only what worked turns the figures
  into a selection. Signal: the plan lists more outcomes than the figures show.
- **Shared axes across panels that are meant to be compared.** Reason: separate axes make a
  small effect and a large one look the same. Signal: panels with different limits that sit side by
  side. If different axes are unavoidable, say so on the panels.
- **The nesting is visible.** Reason: the reader must see which points are replicates of the same
  unit, or the apparent sample size misleads (pseudoreplication). Signal: many points per unit
  drawn as if independent. Color or connect by unit, or draw at the level of the unit.
- **Exploratory results are labelled in the figure.** Reason: a result found by looking, or by
  an analysis added after the data, has a different standing, and a caption is easily lost.
  Signal: a panel that came from a probe (exploratory analysis) with the same look as a
  confirmatory one.
- **Adjusted or unadjusted is stated** when the battery uses a multiplicity correction. Reason: the
  same result reads differently on either. Signal: p-values or intervals with no mention of which.

What would make a bad result look good, or a good one look bad, in your figures, and is it on this
list? If not, add it to the plan.

## Explaining the design

Explain the design to whoever ordered it: the human, in the chat; another agent, in the
hand-off report. This is not optional for science. Statistical choices and their
justifications are widely misunderstood, so a summary of results by an expert, however accurate,
leaves the recipient unable to judge the design or defend it.

For each choice (each test, the sample size, the protocol decisions that matter, the figures), the
explanation says:

- **What was chosen.**
- **Why it fits this situation**, in terms of the data and the question, not of the method's
  reputation.
- **Why the alternatives do not**: the nearest ones, and the property of this study that rules each
  out.
- **Which assumptions it rests on and who agreed them**, including the evidence that each
  validity condition holds.
- **What each possible outcome would mean**, taken from the pattern-of-outcomes table: what the
  recipient may conclude if the result is positive, negative or inconclusive, and what they may not.

How to write it:

- **Plain terms, defined at first use.** A term of the field is allowed and expected; it is
  explained the first time it appears (what a confidence interval says and does not say, what
  power is, what multiplicity costs), in a sentence, with the study's own numbers where possible.
- **To the recipient's level and to the form of the recipient.** The human gets the explanation
  in the chat, in the order of the choices, so they can interrupt or disagree. An agent gets it in
  the hand-off report, complete enough that the next agent can act without asking, and with the
  analysis plan's location.
- **Say what is unsettled.** Assumptions that nobody agreed, conditions whose evidence is weak,
  decisions the recipient still owns. Hiding them leaves a plan that looks more certain than it
  is.
- **Explain bad results as carefully as good ones.** A null, an inconclusive interval, a failed
  control is explained with the same structure: what it shows, what it does not, what the next
  decision is.

Is there a choice in this design that you could not explain in plain terms to the person who
ordered it? That choice is not yet understood, by you or by them.
