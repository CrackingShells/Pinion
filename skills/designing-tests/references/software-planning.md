# Software tests: planning which guards exist

A suite stays small and useful when each test earns its place by a reason, not when it is held to
a number. This page says where guard candidates come from, what stops them from multiplying, how
bugs feed back without overfitting, what a software test plan must establish, and how to put tests
inside a larger plan.

## Contents

- [Where guards come from](#where-guards-come-from)
- [The distinct-failure rule](#the-distinct-failure-rule)
- [Bugs go to behaviors](#bugs-go-to-behaviors)
- [The test plan's categories](#the-test-plans-categories)
- [Tests inside a larger plan](#tests-inside-a-larger-plan)

## Where guards come from

Start from risk, not from functions. Walking the function list produces one test per function,
which is a map of the code and says nothing about what must keep working. Three sources give
candidates worth a guard:

1. **Behaviors consumers rely on.** For each consumer (a caller, a user, another service, a
   future maintainer reading the interface), ask what they would notice if it broke. Each
   answer is an expected behavior. Test only what we own: a framework's or language's behavior is
   its maintainers' to guard.
2. **Design cornerstones.** The decisions everything else rests on: the data model's shape, the
   ordering or atomicity promise, the contract between layers. When a cornerstone breaks, many
   features break quietly. These are the guards that matter most, and they are few and
   high-value. Find them by asking "if this stopped holding, how many other things would be wrong
   without any of their own tests noticing?"
3. **Seams with code we do not own.** The places where our code assumes something about a database,
   an API, a file format, another team's service. Our code's correctness depends on that
   assumption, so the assumption gets a boundary guard, usually at integration scope, exercised
   against the real thing or a faithful recorded one.

Observable behavior beats internals: a candidate that can only be stated in terms of private
structure is a confirm candidate, not a guard.

## The distinct-failure rule

A **second test on the same behavior must catch a plausible bug the first misses.** That one rule
replaces every count, ratio and per-function quota. It is a question about the code, so it scales
from a script to a large system: a large application has many behaviors, not many tests per
behavior.

The means of applying it:

- **Equivalence classes.** Inputs the software must treat alike form one class; one representative
  covers it, because a bug that breaks one member almost always breaks the class. A second
  representative is justified only if you can name the bug that distinguishes them.
- **Boundaries.** Bugs cluster where classes meet (off-by-one, empty, maximum, just past a limit).
  One test at each edge of an ordered range is a distinct failure from one in the middle.
- **Pairwise coverage.** When several independent inputs interact, the full product explodes.
  Most interaction bugs involve two parameters, so cover every pair of values once instead of
  every combination. Add a full combination only where a specific higher-order interaction is a
  named risk.
- **Parameterization.** When tests share setup and assertion and differ only in data, they are
  one behavior seen at several points: write one parameterized test, whose rows are the classes
  and boundaries. Each row still passes the distinct-failure rule; a row that cannot be justified
  is deleted.

Ask the rule aloud for any proposed test: *which wrong implementation does this catch that the
tests already planned would let through?* If you cannot name one, do not write it.

## Bugs go to behaviors

A bug is evidence that some behavior had no guard, or a weak one. It is not a test to add. A suite
that records each incident as its own test overfits to the past: it protects against the bug that
happened and not against the class it belongs to, and it grows without bound. The sequence:

1. **Find the behavior** the bug violated, and the consumer who relied on it. The bug means this
   behavior had no guard or a weak one.
2. **Reproduce the bug as a confirm** for the fix step: a marked test that is red now and green
   when the fix lands. It tells you the step worked.
3. **Strengthen or add the guard for the behavior**, at the scope where it is observable, so
   that it covers the class of bug and not only this input.
4. **The reproduction joins that guard only if it is a distinct equivalence class** (a case the
   guard's inputs did not already represent). Otherwise it is culled with the other confirms.
5. **Read the suite's history as a signal.** If tests keep being added one per incident, the
   behaviors they violate belong to something architectural nobody guards: look for the missing
   cornerstone guard and write that instead.

Example of the difference: a report says export crashes on a name containing an apostrophe. The
confirm reproduces that name. The behavior is "export writes any valid name faithfully"; the
guard becomes a parameterized one over the classes of name (quotes, separators, non-ASCII, empty)
and the apostrophe row stays only if the existing rows did not cover its class.

## The test plan's categories

A software test plan is defined by what it must establish, not by a template. Write it in the
form the project already uses and make sure each of these is answered:

- **What must keep working: the guards.** Each with its expected behavior, its scope with the
  consumer that justifies the scope, and the failure it catches (the plausible bug that turns it
  red).
- **Open questions: the probes.** Each with the question and the decision it will feed. A probe
  without a decision is curiosity and does not belong in the plan.
- **Trust boundaries and fixtures.** What is real, what is faked or recorded and why, which
  data the tests need and how it is built (see `software-writing.md`).
- **What was deliberately not tested, and why.** Restraint made visible: code we do not own,
  behavior nobody relies on, cases covered by a lower or higher guard, internals expected to
  change. This section is what lets a reviewer tell a gap from a decision.
- **Done-criteria.** Every guard has been seen failing before it passed; confirms are culled or
  promoted; probes are answered, their answers recorded, and their tests deleted.

The plan does not list confirms. They are working scaffolding chosen in the moment, and
enumerating them in advance both wastes effort and invites keeping them.

## Tests inside a larger plan

When you plan a feature, an implementation or a roadmap, tests are part of each task, not a
final phase:

- Each task names **the guards it introduces**: the behavior, the scope, the failure it catches,
  written first.
- **Probes are their own steps**, each with a question and the decision it feeds, placed before
  the task that needs the answer.
- **Confirms are not enumerated.** The task says guards first and leaves baby steps to whoever
  implements.
- **Done means** each guard was seen failing, and confirms are culled or promoted.
- **A bug fix's plan is one line**: the behavior that lacked a guard, and the guard that now
  covers it. If the fix needs more than that in the plan, the behavior is not yet understood.

For a large build from scratch, put most of the planning effort into the cornerstones (the few
guards that the rest of the design leans on) and into the seams. Features built on a guarded
cornerstone need fewer tests of their own, not more.

Before finalizing any plan, ask: which expected behavior would I be most upset to see break
unnoticed, and does a guard in this plan catch it? Then look for the source of guards this page
does not list.
