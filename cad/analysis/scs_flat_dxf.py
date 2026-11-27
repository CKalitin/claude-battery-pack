"""DXF flats for SCS quoting of the flat parts that changed in v16.3 (run from cad/)."""
import sys; sys.path.insert(0, '.')
import flats15 as f, tower15 as m
parts = {"plate_front": (m.plate(True), "x"), "plate_rear": (m.plate(False), "x"),
         "module_endplate_1": (m.module_endplates()[0].solids()[0], "x"), "module_endplate_2": (m.module_endplates()[0].solids()[1], "x"),
         "mylar_top": (m.g10_top(), "z"),
         "mylar_spacer": (m.box(-m.G10_SPACER / 2, m.G10_SPACER / 2, -m.CELL_W / 2, m.CELL_W / 2, m.Z_CELL, m.Z_CBODY), "x")}
for n, (s, ax) in parts.items():
    print(n, f.flat_from_solid(n, s, ax))
