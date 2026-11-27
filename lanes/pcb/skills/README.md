# General PCB skills (pcb lane, 2026-11-27)

| Skill | Use |
|---|---|
| `pcb-design/` | Design a board end to end in KiCad 10, headless: intent → parts → area budget → wired schematic → nets/stack-up → placement → routing → silkscreen → PCBWay/NextPCB/JLC release |
| `pcb-review/` | Independent review at each gate, as a fresh-context subagent: protocol, briefs, checklist, failure modes |

Installed for every session on this VM as symlinks: `~/.claude/skills/pcb-design`, `~/.claude/skills/pcb-review` → this folder (the `pcb` clone). Edit them here and commit; they're general, not BMS-specific.

## How they were built
Twelve public Claude/agent PCB skill repos were cloned and read on 2026-11-27. The best and most relevant material was merged and rewritten, and checked against KiCad 10.0.8 on this VM. Picks:

| Source (commit, licence) | Taken | Not taken, and why |
|---|---|---|
| sequoia-hope/boardroom (717d809, MIT) | Phases and gates, review protocol, lessons list, net classes, release checks, silk policy | Its viewer, ultraroute and Circuit Composer: separate tools we don't run; JLC-only sourcing |
| Diode663/kicad-claude-skills (a9929f6, MIT) | **`schlib.py` vendored unmodified** (wired KiCad 10 schematics + netlist verify; smoke-tested here); drafting conventions | Windows-only paths (it found kicad-cli on Linux anyway); placement recipes |
| studio-edul/pcb-layout-skill (2026-10-17, MIT) | Occupancy bands, placement numbers B1–B24, edge and spacing targets | EasyEDA API notes |
| jvanderberg/kicad-skills (7837f97, MIT) | Review checklist structure, layout rules, part-selection discipline (exact suffix, dated stock, re-derive on swap) | JLCImport tooling (JLC-specific) |
| pierrejay/pcb-review-skills (2026-11-25, MIT) | Review failure modes, judging rules that come without numbers | EasyEDA import clean-up; per-check scripts |
| aklofas/kicad-happy (6b9767e, MIT) | PCBWay BOM/assembly notes (cross-checked against pcbway.com) | Not installed: large and still to be read and pinned. Candidate second reviewer |
| joseluu/kicad-skills (no licence) | Ideas only (label justification), restated in our own words | No text copied |
| Others read: Novin3dp, forstnernoqq, mash, bluzername, 1999AZZAR, SPREsxm, cjf00787, daishuge, alexchunlin | Nothing unique beyond the above | — |

Fab facts: pcbway.com assembly-capabilities, assembly-file-requirements, capabilities and multi-layer stack-up pages; nextpcb.com assembly capabilities and its file guide (all read 2026-11-27).

## Open
- Write `scripts/` for: sync check (schematic ↔ PCB ↔ BOM/CPL), PCBWay BOM/CPL formatter, nets.csv → net classes and DRU, a CPL rotation overlay. Build them on the BMS board as it's designed.
- Decide on kicad-happy as a second reviewer after reading its code.
