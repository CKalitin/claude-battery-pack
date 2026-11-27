"""Export v15 parts that every contactor concept shares (cells, walls, lid, converters, front PCB...) as BREP."""
import os, sys, time
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..")))
import tower15 as t5
from build123d import export_brep
t0 = time.time()
parts = t5.build()
BAY = ("bus_pack_pos", "bus_pack_neg", "bus_link", "bus_neg_out", "bus_pos_out", "mrbf", "contactor", "shunt",
       "sb175", "g10_sb_bracket", "tray1_g10", "cable_")
n = 0
for k, v in parts.items():
    if k.startswith(BAY):
        continue
    export_brep(v, os.path.join(HERE, "ctx", f"{k}.brep")); n += 1
print(f"exported {n} context parts in {time.time()-t0:.0f}s")
