import json, os
from render import shot, OUT
key = "c1_module_gv14up"; meta = json.load(open(os.path.join(OUT, key, "meta.json")))
L = [("lug_neg_inverter", "inverter − lug (90°, barrel up)"), ("shunt_module", "Tesla shunt sense board"),
     ("cable_neg_inverter", "inverter − lead, 10 AWG"), ("hw_nut_neg_inverter", "M8 nut"), ("lug_neg_charger", "charger − lug"),
     ("shunt_bar", "shunt bar (node B end)")]
H = ("body_half_A", "body_half_B", "plate_front", "screws_", "module_endplates", "so_", "bs5191", "strap_main", "hw_nut_main", "hw_m10nut", "ledboard_f", "ctrl_", "cap_", "lid", "tray2", "inverter", "charger", "contactor", "sb175", "g10_sb_cheek", "cable_inverter", "cable_charger", "keepout_")
print(shot(key, meta["roles"], L, "issue_inv_neg_lug.png", "Open issue: inverter − lug barrel 1.25 mm from the shunt sense board",
           "both at pack − potential; gap is mechanical (lug barrel vs board edge components / conformal coat)", view=(0.25, -0.55, 1.0),
           focal=(78, -8, 248), dist=110, hide=H))
