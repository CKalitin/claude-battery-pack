# BMS board toolchain: proposal (2026-11-27, awaiting Chris)

**Update 2026-11-27 (later):** KiCad 10.0.8 installed and verified headless; the general skills are in `lanes/pcb/skills/` (see its README). Still open: kicad-happy (not installed), Freerouting + Java (not installed), ngspice (not installed). Facts come from web search / page summaries ⚠️ unless marked.

## Requirements
| # | Requirement | From |
|---|---|---|
| R1 | pcb designs the board autonomously: minor part selection (ESP32 and BQ76952 fixed), schematic, routing | Chris 2026-11-27 |
| R2 | Human-readable schematic: parts actually wired, not net labels only | Chris 2026-11-27 |
| R3 | BMS board entirely PCBA by **PCBWay** (replaces "NextPCB, PCBWay second"); front/LED board by NextPCB | Chris 2026-11-27, relayed by main-battery; owner-requirements §6 |
| R4 | Meets the standard of an experienced PCB designer (UBC Solar) | Chris 2026-11-27 |

## Candidates
| Choice | Proposal | Lost, and why |
|---|---|---|
| CAD | KiCad 10.0.8 from `ppa:kicad/kicad-10.0-releases` | Ubuntu's 9.0.8: old. Nightly 10.99: new file format, SWIG `pcbnew` removed, schematic IPC API still changing; KiCad 11 expected ≈ Feb 2027 |
| Schematic | Own Python writer of `.kicad_sch` with explicit placement and wires; netlist compared with a separate connectivity spec | SKiDL / atopile / tscircuit: extra source of truth, readability unproven. MCP servers: no benefit over files + `kicad-cli` |
| Routing | Placement and critical nets scripted; Freerouting 2.6.0 for leftover low-speed nets, then reviewed | Freerouting alone: no design intent. DeepPCB (paid), Quilter (free tier trains on designs): cloud |
| Review | kicad-happy (MIT, 1774 stars, pushed 2026-11-24 ✓ GitHub API), pinned and read before running | — |
| Reference only | Diode663/kicad-claude-skills (MIT, 2 stars ✓; Windows-only tested, one fabricated board) | Not a dependency |
| Sim | ngspice 45.2 (apt) | LTspice: Windows GUI |
| Parts | DigiKey + Mouser APIs; BMS parts checked against PCBWay's sourcing ⚠️ (NextPCB matches BOMs against DigiKey, Mouser, HQ Online) | LCSC not named in NextPCB sources |

## NextPCB inputs (front/LED board)
- Gerber + drill zip; BOM with Manufacturer Part Number, Designator, Quantity (optional Customer Supply); CPL with designator, X, Y, rotation, side.
- Assembles SMT, through-hole and flex; passives 01005, fine pitch 0.38 mm (vendor page).
- ⚠️ PCBWay (now the BMS fab): capabilities, parts library, BOM/CPL format not researched. Do this before part selection.

## Sources
- kicad.org/blog/2026/10/KiCad-10.0.8-Release/ ; launchpad.net/~kicad/+archive/ubuntu/kicad-10.0-releases
- forum.kicad.info/t/post-v10-new-features-and-development-news/66611
- github.com/aklofas/kicad-happy ; github.com/Diode663/kicad-claude-skills ; github.com/freerouting/freerouting
- nextpcb.com/pcb-assembly-capabilities ; support.nextpcb.com/portal/en/kb/articles/1-pcb-assembly-files-explanation

## Open
- Chris: one reference schematic and layout that meets the bar; DigiKey/Mouser API keys; permission for review subagents.
- BMS is a paid PCBWay order unless a sponsorship is agreed (main-battery has asked Chris).
