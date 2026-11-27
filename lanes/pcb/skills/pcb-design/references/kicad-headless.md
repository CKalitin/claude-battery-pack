# KiCad 10 headless: commands and traps (verified on KiCad 10.0.8, Ubuntu 26.04, 2026-11-27)

## Install
```bash
sudo apt-get install -y software-properties-common
sudo add-apt-repository -y ppa:kicad/kicad-10.0-releases && sudo apt-get update
sudo apt-get install -y --no-install-recommends kicad kicad-footprints kicad-symbols poppler-utils
mkdir -p ~/.config/kicad/10.0 && for t in sym-lib-table fp-lib-table; do
  [ -f ~/.config/kicad/10.0/$t ] || cp /usr/share/kicad/template/$t ~/.config/kicad/10.0/$t; done
```
- Ubuntu's own `kicad` package is 9.x: use the PPA.
- The nightly (10.99 / KiCad 11) drops SWIG `pcbnew` and changes the file format. Don't use it for production until 11.0 ships (expected ≈ Feb 2027).
- **Without the global lib tables**, ERC reports a `lib_symbol_issues` / `footprint_link_issues` warning on every symbol. Copy them as above.
- If apt or a download fails on DNS or network, retry once, then report. Don't loop.

## kicad-cli (most-used)
```bash
kicad-cli sch erc --format json --severity-all -o erc.json board.kicad_sch
kicad-cli sch export netlist --format kicadxml -o net.xml board.kicad_sch
kicad-cli sch export pdf -o sch.pdf board.kicad_sch && pdftoppm -r 110 -png sch.pdf page
kicad-cli pcb drc --format json --severity-all --schematic-parity --refill-zones --exit-code-violations -o drc.json board.kicad_pcb
kicad-cli pcb render --side top --width 1600 --height 1000 --quality basic -o top.png board.kicad_pcb   # works headless (no xvfb needed for basic)
kicad-cli pcb export svg --layers Edge.Cuts,F.CrtYd,F.Fab,F.Cu --mode-single --exclude-drawing-sheet --fit-page-to-board -o f.svg board.kicad_pcb
kicad-cli fp export svg --footprint NAME -o out/ /usr/share/kicad/footprints/LIB.pretty   # check a land pattern
```
Exports: `gerbers, drill, pos, ipcd356, ipc2581, odb, step, glb, stats` (see `fab-release.md`). `hpgl` is gone in 10.0.

## pcbnew Python (SWIG, still in 10.x)
```python
import pcbnew
fp = pcbnew.FootprintLoad("/usr/share/kicad/footprints/Package_QFP.pretty", "TQFP-48_7x7mm_P0.5mm")
b = pcbnew.BOARD(); b.Add(fp)
fp.SetPosition(pcbnew.VECTOR2I(pcbnew.FromMM(x), pcbnew.FromMM(y))); fp.SetOrientationDegrees(90)
bb = fp.GetCourtyard(pcbnew.F_CrtYd).BBox()          # courtyard bbox, IU (nm)
pcbnew.SaveBoard("out.kicad_pcb", b)
```
Traps:
- `pad.GetLayer()` returns F.Cu even for a flipped part. Use `pad.IsOnLayer(pcbnew.B_Cu)`.
- Scripted `ZONE()` keeps a 0.5 mm default clearance. Set clearance and min width explicitly, and after `ZONE_FILLER(b).Fill(b.Zones())` check each zone's area and piece count.
- Deleting footprint graphics with `fp.Remove(g)` has segfaulted (KiCad 9 report). Move them to a Fab layer instead.
- Courtyard parsing straight from `.kicad_mod` (`courtyards.py`) and `GetCourtyard()` agree to a few %. Rotated parts differ slightly.
- The library footprint's 3D model may be missing. Renders still work; check heights from datasheets.

## Schematic generation
`scripts/vendor_diode663/schlib.py` (MIT, unmodified). Put it on `sys.path`; don't run Python from inside a downloaded folder. It writes KiCad 10 native files (format `20260306`) and calls `kicad-cli` for verify, ERC and render. Smoke test (LDO + ESP32-S3 + I²C + LED): netlist matched the spec, 0 text collisions, A3 render clean. Its ERC flagged a missing PWR_FLAG, which is correct.
