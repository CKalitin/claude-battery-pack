# Blog notes: designing a battery pack with Claude

> Working notes for a blog post. This is **not the post**. The post should be a set of insights in the style of Vannevar Bush's *Pieces of the Action*, not a play-by-play. Chris adds notes as the project goes; Claude adds supporting evidence from the repo.
>
> Tags: **[C]** is Chris's observation. **[Claude]** is Claude's suggestion or evidence, for Chris to accept or cut.

---

## 1. Thesis: taste is the bottleneck, not implementation

- **[C]** Biggest conclusion. Claude does the implementation; the human supplies taste. Good results came from Chris steering with good engineering taste. Without that taste (a field outside his expertise), he couldn't steer Claude toward something beautiful.
- **[C]** Most of what Chris did was give design guidance. Guidance fails when the design goes down a wrong branch of the design space. Example: a lot of empty space inside the pack. Claude is fine with empty space; Chris finds it ugly. That requirement was never stated explicitly.
- **[C]** Fix: make requirements clearer from the outset, and do everything else engineers do to have good taste about which designs to pursue and which not.
- **[Claude]** Evidence from the version history:
  - **v05 → v06:** cells laid on edge to narrow the box. Busbars ended up on the side, which was rejected ("busbars belong on top"). That was an unstated requirement, so a whole branch had to be thrown away.
  - **v08 → v09:** dead length in front of the cells was removed, but only once Chris saw it.
  - **v10 → v11 → v12:** converters went beside → end to end → stacked. v11 was 77 mm longer than v12.
- **[Claude]** Possible framing: an unstated aesthetic requirement *is* a requirement. "No dead volume", "busbars on top" and "tower proportions" behave exactly like "≤ 26 kg" once written down. They just only get written down after the first ugly design.
- **[Claude]** Corollary: taste works as a pruning function over the design tree. Claude explores and evaluates branches fast; the human decides which branches are worth exploring.

## 2. Division of labour: the human owns understanding

- **[C]** Hard requirement: Chris must be able to justify every decision in the project. Claude does the implementation work and is an excellent resource to consult when unsure, but in the end Chris has to understand everything.
- **[Claude]** The per-version READMEs (`versions/*/README.md`) are where that comes true. Every change is documented with its reason and a calculation. If Chris can't defend a line in v13's README, the design isn't finished.

## 3. Write the principles first

- **[C]** Chris gave Claude a set of design principles as extra notes in one of the prompts. Claude followed them for the rest of the project.
- **[C]** The original list, verbatim:

  > **Fundamental requirements**
  > * Minimal assembly time
  >    * Solar takes 6 man hours per module for 32 modules. I will not spend 200 hours doing assembly.
  >    * I enjoy using a wrench, a night of assembly is fine, but not 17 hours
  > * All parts machined / assembled by suppliers
  >    * If send cut send can't do it, you're likely incorrect
  > * 1 kWh
  > * One PCB for all contractors and shunt
  >    * BMS PCB slots on top of it
  >    * V5 BMS made early!
  > * 120 V in with charger built in, 120 V outlet.
  > * DC outlet also available
  >    * Anderson connector?
  > * Easily accessible debug info (wifi?)

- **[Claude]** How v13 tracks against the list:

  | Principle | v13 | |
  |---|---|---|
  | One night of assembly, not 200 h | PEM and captive hardware, one module, about 83 parts | ✓ |
  | Supplier-made parts | SendCutSend for every fabricated part | ✓ |
  | 1 kWh | 2.69 kWh | Changed: the target was raised at v10 (cost per Wh, then the sponsorship) |
  | One PCB for contactor and shunt | Contactor and Tesla shunt bolted at the control board | ✓ |
  | BMS PCB slots on top | BMS merged onto the same board (BQ76952 + ESP32) | **Deviates:** one board instead of two. Decide whether to keep the slot-in BMS board |
  | 120 V in, charger, 120 V out | NPB-450-24 + NTS-400P-124 | ✓ |
  | DC outlet (Anderson) | Lid Anderson | ✓ |
  | Debug over Wi-Fi | ESP32 | ✓ |

- **[Claude]** Insight candidate: "If SendCutSend can't do it, you're likely incorrect" is taste encoded as a manufacturability prior. It turned one supplier's design-rule sheet into the design-space boundary, and it is the reason v05's 3 × 30° corners exist.
- **[Claude]** Insight candidate: the principles came with numbers. "6 man-hours × 32 modules ≈ 200 h" turns "minimal assembly time" from a wish into a constraint Claude can check designs against.
- **[Claude]** Rules collected during the session, which read like that list grew in use:
  - Best part is no part.
  - Adding a part is a sin.
  - No parts that require emailing vendors.
  - No doubtful datasheets.
  - Buy links are required.
  - Busbars on top.
  - Every fabricated part from SendCutSend.
  - "Don't ask me to make checks, just make the checks."
  - "You have a web browser. Don't ask me to do this."
- **[Claude]** Insight candidate: principles written once beat corrections given repeatedly. Corrections fix one decision; principles fix the generator of decisions.

## 4. Let Claude pick its tools

- **[C]** Letting Claude use whatever tools it wanted was very useful. Claude proposed build123d for CAD on its own; Chris just said yes.
- **[Claude]** Stack that ended up in use, none of it specified by Chris:
  - build123d: parametric CAD, STEP/STL export.
  - Pairwise interference checks.
  - pyvista: physically based studio renders.
  - scikit-fem: Kirchhoff plate FE with Morley elements for the end plates.
  - matplotlib.
  - SendCutSend's published design-rule JSON.
  - git.
- **[C]** Everything ran in a VM on Anthropic's servers; Chris didn't need his own computer for most of it.

## 5. What Claude is good at (observed)

- **[C]** Math, optimization and calculations.
  - **[Claude]** Example: tie-rod placement. The beam optimum $a = (\sqrt2-1)/2\cdot h = 0.207h$ was checked with plate FE, and end-plate deflection went from 0.655 mm to 0.078 mm (8.4×).
- **[C]** CAD assemblies with no interference between parts.
- **[C]** When prompted, checking manufacturability against SendCutSend's design guidelines.
- **[Claude]** Note the qualifier "when prompted". Rule violations that stood until Chris asked:
  - The lid joggle needed a 1.7 mm offset; the SendCutSend minimum is 8.2 mm.
  - The v12 straps broke the U-channel rule.
  - Most telling: the tie-rod heights for the LF100MA cell (v05) were silently carried through v07–v12, 7 versions on a different cell.
  - Lesson: reusing parameters spreads stale assumptions. Checks need to be written as code that runs on every build, not as an occasional prompt.

## 6. Session length and autonomy

- **[C]** Over 10 hours of conversation in one session, and still going strong. Insane.
- **[C]** Claude pushes to GitHub correctly on its own, with no separate Claude Code setup.
- **[Claude]** Context did get compacted several times. Durable state lives in the repo (CAD scripts, docs, version folders), not in the conversation, which is why it survives compaction. That's a design rule for long agent projects: put the truth in files.

## 7. Browsers

- **[C]** Claude in Chrome was good: a capable browser with tabs. Signing in needed Claude in Chrome, because it's easier for Chris to sign in there.
- **[C]** Chris's impression: Claude in Chrome felt much more structured than Claude's built-in browser.
- **[Claude]** Claude's honest view (medium confidence):
  - On Claude's side the tools are close to equivalent: page text, accessibility tree with element refs, find, form input, tabs.
  - The real differences were Chris's sign-ins and that the tabs sat in his own browser where he could watch.
  - Most public reading (SendCutSend specs, datasheets) went through plain web fetch, not a browser at all.
  - The perceived structure is probably mostly on the human side.

## 8. Open threads, to resolve before writing

- [ ] Multiple Claude agents in parallel: one branch or worktree each, split by area (electronics, CAD, docs). Worth trying, and worth a paragraph either way.
- [ ] Obsidian access for Claude, so the principles list and notes are shared.
- [ ] The $2,000 SendCutSend sponsorship changed the objective: 8S over 4S on cost per Wh ($1.15 vs $1.94). Possible insight about how external constraints reshape the design space.
- [ ] Build and test results: the post is stronger with a pack that works.
