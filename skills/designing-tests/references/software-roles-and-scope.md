# Software tests: roles and scope

Every software test answers two independent questions. The **role** says why the test exists, and
so how long it lives and where it lives. The **scope** says how much of the system it exercises,
and so what it costs and how well it localizes a failure. Mixing the two up produces the failures
this skill exists to prevent: suites that only grow, tests that reassure without protecting, and
scaffolding left behind as if it were a cornerstone.

## Contents

- [Roles](#roles)
- [Scope](#scope)
- [Role x scope matrix](#role-x-scope-matrix)
- [Lifecycle](#lifecycle)
- [TDD flow](#tdd-flow)
- [Judging a case this page does not name](#judging-a-case-this-page-does-not-name)

## Roles

The role follows from one question: what would be lost if this test were deleted today, and for
how long would that loss matter?

| Role | Purpose | Lifetime | Where it lives |
|---|---|---|---|
| Guard | Defines an *expected behavior* of the software: a transformation or operation it is relied on to perform in its context, including the cornerstones of the design that everything else builds on | Until that behavior is deliberately changed | In the suite, permanently |
| Confirm | Checks that one step toward a guard did what was meant (a block behaves, a helper parses) | Until the step is done and a guard covers it | In the suite while the work is in progress, marked by the project's own means (marker, name, tag) so culling is mechanical |
| Probe | Answers a question during the work (does this library retry? which index is faster? what does this endpoint return on an empty page?) | Until it is answered | Outside the suite; the answer goes where decisions are recorded |

Say "expected behavior". Software changes; what a guard holds is not something
that never changes but something the software is relied on to do *now*, for a consumer, in a
context. When the behavior is deliberately changed, the guard is changed first and on purpose.
That is what separates a guard from a snapshot of whatever the code happens to do.

The roles differ in what they may know about the code. A guard speaks only the language of its
consumer, so it survives any refactor that keeps the behavior. A confirm may reach into
internals because it will be deleted. A probe knows whatever it needs and promises nothing.

## Scope

Scope stays unit, integration or end-to-end, and sets the cost, the speed, how precisely a
failure points at its cause, and which fixtures are needed.

A guard's scope is **where its behavior is observable to the consumer that relies on it**, never
the most convenient place to write it. If a caller relies on an ordering guarantee of a public
function, the guard is a unit test through that function. If it relies on two components handing
data over correctly, the behavior only exists at the seam, so the guard is an integration test.
If it relies on a user journey, the guard is end-to-end. Choosing a lower scope because it is
easier tests something nobody relies on; choosing a higher scope because it feels safer buys a
slow suite that fails far from its cause.

State the consumer and the reason with the scope. "Unit, because callers of `parse` see only its
return value" can be checked; "unit" alone cannot.

Confirms sit near the block being built and may touch internals. Probes take whatever scope their
question needs, including a throwaway script.

## Role x scope matrix

Each cell gives a typical use and the mistake that cell invites. It is a sample of what each
combination looks like in practice, not a list of the only cases.

| | Unit | Integration | End-to-end |
|---|---|---|---|
| **Guard** | *Use:* a pure transformation or rule consumers call directly (rounding, parsing, permission decision), asserted through its public interface. *Mistake:* a guard on a private helper, which is a confirm that was never culled and now blocks refactors | *Use:* the behavior of a seam: two components or our code and a database, queue or file format we depend on, exercised for real. *Mistake:* mocking one side of the seam, so the test checks the mock and the seam stays unguarded | *Use:* a journey a user or caller relies on, kept to the few cornerstones whose failure means the product does not work. *Mistake:* using it to cover behaviors that live lower, which makes the suite slow and each failure ambiguous |
| **Confirm** | *Use:* the baby step on a block under construction (this function handles the empty list), may inspect internals. *Mistake:* leaving it unmarked, so nobody can tell it from a guard and it is kept forever | *Use:* checking that two new blocks connect while the wiring is being built. *Mistake:* keeping it after the guard that covers the same seam exists, so one behavior is paid for twice | *Use:* rarely; a smoke check that the new pieces start together before any guard exists. *Mistake:* usually a missing guard: if the check matters after the step, write it as a guard at the scope where its behavior lives |
| **Probe** | *Use:* a few lines to learn what a library function returns at an edge. *Mistake:* committing it as a test, where it asserts a guess about code we do not own | *Use:* measuring how a real service or database behaves under the call pattern the design will use. *Mistake:* never recording the answer, so the next agent re-runs the experiment; or relying on the finding without turning it into a boundary guard | *Use:* checking feasibility of a whole path (can the deployed thing be reached at all?) before designing around it. *Mistake:* letting it linger in the suite as a flaky, slow test with no stated question |

## Lifecycle

**Probe.** Write the question and the decision it feeds before running it. When it answers, record
the answer where decisions are kept (the plan, the design note, a comment at the decision), then
delete the probe. If the design now relies on what the probe found about code we do not own, a
behavior of that code has become part of what must keep working. Rewrite the probe as a **boundary
guard** at the seam, under guard standards (see `software-writing.md`). An upgrade needs that
reliance; curiosity is not enough.

**Confirm.** It dies when the guard it serves passes, because from then on the guard covers the
step and the confirm only repeats it at higher maintenance cost. Cull it mechanically through its
mark. Promote a confirm only if, at cull time, it encodes a behavior worth guarding that no guard
covers, and then rewrite it to guard standards: public interface, independent expected value, a
name that states the behavior. A promoted confirm is a new guard that happens to have been
drafted early, not the old test kept.

**Guard.** It lives until the behavior is deliberately changed. Then it is edited or deleted in
the same change as the behavior, with the reason stated, never "fixed until green".

## TDD flow

1. Name the behavior and its consumer. Write the guard first, at the scope where the behavior is
   observable. Run it and **see it red**, for the right reason: it must fail because the behavior
   is missing, not because of a typo or a missing import. A guard never seen failing may be
   unable to fail (see `software-false-safety.md`).
2. Build toward it in baby steps. Each step may get a **confirm**: a small, marked check near the
   block that tells you the step did what you meant. Confirms exist because the guard stays red
   until the last step; they carry you there.
3. When the guard turns green, it is the only thing that counts as done. Run the suite.
4. **Cull the confirms** the guard now covers; promote any that earned it. Leave only guards.

If you notice yourself keeping confirms "just in case", the guard was too weak or too high to trust
alone. Strengthen the guard instead of keeping scaffolding.

## Judging a case this page does not name

Ask in this order. What decision does this test serve, and until when? (That gives the role.)
Who relies on the behavior, and through what interface? (That gives the scope.) What plausible
wrong implementation would make it fail? (If none does, it protects nothing.) What event ends its
life, and is that event marked so someone can act on it? Then look for the combination of role and
scope that none of the cells above describes, and apply the same questions to it.
