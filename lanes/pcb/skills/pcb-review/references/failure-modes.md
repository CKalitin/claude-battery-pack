# How design reviews go wrong, and the rule against each

*(Condensed and reworded from pierrejay/pcb-review-skills `pcb-verification/references/failure-modes.md` and `qualitative-rules.md`, MIT.)*

## Criteria and verdicts
- **Set the target before computing**, from the datasheet or layout guide. Never adjust it after seeing the result.
- **Compliance and effect are two answers.** A rule not met is a fail even when the effect is small. Put the effect in the comment; don't soften the verdict.
- **Only the designer accepts a deviation,** and an acceptance dies with the thing it accepted.
- **A reservation you can lift yourself is not a reservation.** Find and read the datasheet; judge at the pessimistic bound. If it still passes, it's a plain pass.
- **Label in-house thresholds as in-house,** and aim them at outliers. Don't present them as datasheet rules.
- **Selection range vs physical quantity.** A datasheet's recommended range ("L between x and y") is judged at the part's nominal value. A computed quantity (a voltage, time or margin) is judged at the tolerance corners.
- **DRC checks minimums, not intent.** Compare routed widths and gaps with what the net class intends.
- **State the stack-up in every impedance or thermal verdict.** Two 4-layer builds differ by 20–40 %.

## Measurements and models
- One definition per measurement (pad to pad, edge to edge, centre to centre), the same in every check.
- **Balance every extraction:** extracted length = routed length; power in = power placed + power leaving.
- **A capacitance in a calculation is its value at the working voltage,** from that part's curve. A 10 µF 50 V 0805 X5R keeps ≈ 2.8 µF at 12 V.
- **A simulated voltage exactly at a rating is the model clamping.** Rerun it without the clamp and read the current and energy.
- **Cross-check every new result by an independent method** (closed form, hand calculation) before announcing it.
- **A scenario is not a bound.** Say why a "worst case" covers the scope.
- **An unpublished value is estimated openly:** both bounds, verdict at the pessimistic one.
- **Read values from the board and the firmware,** not from memory or a typed table. A typed table outlives the change it describes.
- **Look at the whole event and both polarities.**
- **Placement is judged from every layer of the area,** not from package outlines.

## Toolchain
- After any change, re-run all checks and **explain every number that moved.**
- **The chain fails loudly:** no input silently skipped.
- **Describe a tool from its code, not its header.** A docstring that disagrees with the code is a bug.
- **Check whether the tool or the import made the defect** before blaming the design.
- **A DRC item set to "ignore" is a check not run.** Measure it independently.
- Compare multisets, not sets: two equal resistors in parallel are two parts.

## Reporting
- A recommendation gets built as written, so it must be complete and verified under the stress that triggered it.
- Give each margin a direction in words ("12 dB above the limit").
- Don't bring back a choice the designer has already dropped.
- Before listing what's left to decide, re-read the open points: an action already agreed is a to-do, not a decision.

## Rules without numbers ("no copper under…", "match lengths")
Judge them in three steps:
1. **Mechanism:** what effect the rule protects against, and for which kind of circuit.
2. **Applicability:** whether that mechanism exists on this board.
3. **Numbers:** the effect if the rule isn't followed, against the cost of following it.

A datasheet's *requirements* (abs max, "connect X to Y") are criteria. Its *layout guides and reference designs* are known-good starting points, not criteria by themselves.
