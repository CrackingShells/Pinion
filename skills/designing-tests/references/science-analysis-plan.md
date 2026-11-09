# The analysis plan

Open this when writing, reviewing or updating the document that holds a study's design. There is
no template: a template would push every study toward the same shape, and the studies differ. The
plan is defined by the categories below, each by what it must establish and why. Write each in the
form this study needs, in the order that reads best, and add a category if the study needs one.

## Contents

- The categories
- Where it lives
- The evolution log

## The categories

Treat each as a question the plan must be able to answer, not a box to fill.

- **Research questions and hypotheses.** Establishes what the study is for and what would count as
  an answer. Without it a result cannot be judged relevant, and later analyses cannot be told
  apart from the planned ones. Includes H0 and H1 per statistical question and the one- or
  two-sided choice with its reason.
- **From the questions to the battery.** Establishes that these tests, together, answer the
  questions, and what each pattern of results means (support, evidence against, inconclusive). It
  is where sufficiency is argued, and it is the part of the plan a reader can check against the
  results afterwards. See [science-questions-and-tests.md](science-questions-and-tests.md).
- **Test choices with alternatives considered.** Establishes that each test was chosen, not
  defaulted to: the nearest alternatives and the property of this situation that rules each out.
  Also the fallback per test, and the multiplicity decision across the battery.
- **Validity conditions, each with the evidence that it was checked.** Establishes that the error
  rates claimed hold. Each entry says what the condition protects, how it was checked (argument
  from the design, simulation, diagnostic, cited result), and what the check showed. A plan that
  lists conditions without evidence has only moved the assumption.
- **Protocol and cohort.** Establishes what was done to whom and why the data can answer the
  question: unit, replicates, pairing and blocking, randomization, blinding, controls, inclusion
  and exclusion, allocation. It is where the validity of the tests is rooted. See
  [science-protocol-and-sample.md](science-protocol-and-sample.md).
- **Sample size, budget and their assumptions, with who agreed them.** Establishes that the study
  can answer the question at the cost agreed. Includes the effect it is powered for, the
  variance and its source, attrition, design effect, the sensitivity curve or the minimum
  detectable effect, the cost, and for each assumption its source and who agreed it. A guess that
  nobody agreed is marked as one.
- **The known-truth validation.** Establishes that the battery, run as the pipeline will run it,
  holds its false-positive rate under H0, has the planned power, and recovers a planted effect.
  Includes how many runs and the Monte Carlo error, and the robustness runs behind the validity
  evidence.
- **The data contract.** Establishes that the datasets are in a shape the battery can run on and
  that a swapped-in dataset can be told to fit or not: the study contract, the data dictionary,
  the manifest's location. See [science-data.md](science-data.md).
- **The planned figures.** Establishes what the results will look like before they exist: which
  figure answers which question, the decision lines drawn, the figures rendered on the
  simulations. See [science-showing-and-explaining.md](science-showing-and-explaining.md).
- **Probes.** Establishes which analyses are exploratory (pilots, variance estimates, looking at
  the data for ideas), what decision each feeds, and that they are labelled as such wherever they
  appear.
- **The evolution log.** Establishes how the plan changed and why (below), so that the plan
  that was followed is knowable.

Is there something a reader of the plan would need to judge this study that none of these
categories carries? Add it, with the reason.

## Where it lives

Follow the project's own convention first: its plan or docs folder, the roadmap task, the
description of the pull request. If the project has no convention, put it inline in the plan or
task being written, or ask where it belongs. Create a separate file only when the study is big
enough that the plan would drown the document that holds it. Do not create a folder or a
naming scheme the project does not already use.

The plan lives as long as the research question it serves and the battery attached to it: when a
dataset is swapped in, the plan is what says which tests to run and what they mean.

## The evolution log

Plans change: a condition fails when the data arrive, a variance turns out larger, a control
reveals a problem with the assay, the user revises what effect matters. The evolution log is the
record of how the plan changed. It is neutral: it records what happened and why, without saying
that change is good or bad, because the same change can be a sound correction in one case and a
route to a convenient result in another, and only the record lets a reader tell.

Each entry says:

- **what changed** (the old and the new content, concretely);
- **when and at what stage**: before any data were seen, after a pilot or a simulation, after
  the data of this study were seen;
- **why**, in terms of what was learned;
- **who agreed** (the user, the parent agent, the dispatched agent that supplied the number);
- **what it does to the claim**: which results remain confirmatory, and which become exploratory.

The stage matters because a change made after seeing the data of the study can no longer be
confirmatory for the result it concerns, however well justified: the result is reported as
exploratory and labelled so in the figures, and confirming it needs fresh data. A change made before
data, from a simulation or a pilot, usually leaves the claim intact. Write that distinction in the
entry instead of leaving it for a reader to infer.

The log also keeps fallbacks honest: a switch to a fallback test that had been named in advance
is an entry with the check that triggered it; a switch to a test nobody had named is an entry
that says the reason, the stage, and the changed status. Contract changes (a variable added, a unit
changed) go in the log too, with the version.
