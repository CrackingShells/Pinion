# Software tests: writing each role

How a test is written follows from its role. Rules that hold for every test come first; then what
changes for a guard, a confirm and a probe; then fixtures, trust boundaries and the must-run set.

## Contents

- [Rules for every test](#rules-for-every-test)
- [Guards](#guards)
- [Confirms](#confirms)
- [Probes](#probes)
- [Fixtures and trust boundaries](#fixtures-and-trust-boundaries)
- [The must-run set](#the-must-run-set)

## Rules for every test

Each rule exists so that a red test tells the truth and a green one means something.

- **The name states the behavior**, as a sentence a consumer would recognize:
  `rejects_a_refund_larger_than_the_payment`, not `test_refund_2`. When the behavior changes, the
  name is the first thing that must change, which is how a stale test gets noticed.
- **Derive the expected value independently of the code under test**: by hand from the
  specification, from a trusted oracle (a reference implementation, a known published value), or
  as a property that must hold for any input (sorting twice equals sorting once; decoding an
  encoding returns the original). An expected value computed by the code being tested, or by a
  copy of its logic, cannot disagree with it.
- **No logic in tests.** No loops deciding what to assert, no branches, no recomputing the
  answer. Logic in a test needs its own test, and a bug in it hides a bug in the code. Data tables
  are fine; computation is not.
- **One behavior per test.** A test that checks three things reports only the first failure and
  has no honest name. Several assertions are fine when they describe one behavior.
- **A failure message names what broke**: the behavior, the input and the expected versus actual
  value, so the reader can act without opening the test. `assert result` tells nobody anything.
- **Use the real thing at boundaries we own; mock only what we do not own.** A mock of our own
  module makes the test describe the mock's script, and the code can break behind it. Fake what is
  slow, nondeterministic or outside our control (the network, the clock, a third party), and
  keep that fake faithful to the real behavior.
- **Deterministic.** Fix seeds, clocks and ordering; avoid sleeps; isolate shared state. A flaky
  test trains everyone to ignore red, which destroys the value of every other test.

## Guards

A guard must survive refactors that keep the behavior, and fail on changes that break it.

- **Go through the consumer's interface**: public functions, the CLI, the HTTP surface, the file a
  downstream reads. Never assert on private fields, call order of internals or intermediate data
  structures, because those change when the design improves.
- **Assert the outcome, not the route.** Check what the caller can observe: return value, state
  change, emitted message, written file. A guard that verifies "method X was called" fails when
  the implementation is improved and passes when the result is wrong.
- **Be seen red.** Before relying on a guard, see it fail for the right reason, by writing it first
  or by breaking the code on purpose (see `software-false-safety.md`).
- **Say what it guards.** The name and a short comment give the behavior, the consumer relying on
  it and the bug it catches, so a later reader can decide whether to keep it after a change.
- **Keep it to the scope where the behavior lives.** A guard dragged to a higher scope than needed
  is slow and ambiguous; one at a lower scope than the consumer sees misses the seam.
- **Change it only with the behavior.** If a refactor turns a guard red, either the refactor
  changed the behavior (change the guard deliberately and say so) or the guard was coupled to
  internals (rewrite it to go through the interface).

## Confirms

A confirm is scaffolding. Its writing rules are about making it easy to remove.

- **Mark it with the project's own means**: a test marker or tag, a name prefix, a dedicated
  directory, a comment the suite's tooling already respects. Use whatever the project has before
  inventing something. The mark must be something a command can select, because culling must be
  mechanical, not a matter of remembering.
- **Name the guard it serves** in the mark or the name. A confirm that serves no guard has no
  reason to exist; that is a prompt to write the guard.
- **Keep it cheap and local.** It may poke at internals and use throwaway data. Do not invest in
  making it elegant.
- **Cull at the end of the task**: run the selection for the mark, delete what the passing guard
  now covers, and promote the rare one that encodes a worthwhile behavior by rewriting it to guard
  standards. A suite with no marked confirms after the task is the normal finished state.

## Probes

A probe is an experiment, so it is written to be thrown away and its result kept.

- **It stays outside the suite**: a scratch script, a notebook, a REPL session. Inside the suite it
  becomes a test with no role, runs forever, and asserts a guess about code we do not own.
- **Write the question and the decision first.** "Does the client retry on 429? Decides whether we
  add our own backoff." Without the decision, the probe is not needed.
- **Record the answer where decisions are recorded**: the plan, a design note, a comment beside
  the decision it affects. Then delete the probe.
- **If the design now relies on the answer**, write a boundary guard at the seam under the rules
  above, with a fake or a recorded response faithful to what the probe observed.

## Fixtures and trust boundaries

- **Build data from the behavior's classes**, not from a copy of production. A fixture states
  which equivalence class each record represents, so a reader knows what it stands for and which
  rows are redundant.
- **Make each test own its data**, or share only read-only data. Hidden coupling through shared
  mutable fixtures is the usual source of order-dependent failures.
- **Draw the trust boundary explicitly**: what is exercised for real (code and storage we own), what
  is faked (network, clock, randomness, third-party services) and why. Write that down once in
  the plan; tests then follow it, and a mock of something we own is visibly a violation.
- **Keep fakes honest.** A fake that is more forgiving than the real service lets the guard pass
  while production fails. Check recorded or faked behavior against the real thing occasionally,
  through a probe, and update the fake when it drifts.
- **Test the boundary where our code meets the outside**: malformed input, timeouts, partial
  responses, permission errors. These are the cases where the outside differs from our assumptions.

## The must-run set

Some guards are the ones whose failure means the software cannot be trusted at all: the
cornerstones, and the few journeys that prove the whole thing starts and works. Identify that set
and make it cheap to run on every change, before anything slower. It is a subset chosen by
consequence, not by speed alone: a fast test of something trivial does not belong in it, and a
slow cornerstone guard may.

Run the full suite at the cadence the project can afford, and the must-run set always. If the
must-run set is turning slow or grows large, that is a sign of a suite problem (too many guards at
too high a scope), not a reason to run it less often. Then ask which expected behavior of this
software the list above does not cover, and write the test that fits it.
