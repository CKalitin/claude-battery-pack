"""v16.1 signal-wiring renders (fast render, labels only on visible parts). python shoot_harness.py"""
import json, os
import render
from render import shot, OUT
render.SPECIAL.update({
    "sig_shunt": ("#FF8C1A", 0.3, 1), "sig_gnd": ("#151517", 0.3, 1), "sig_bplus": ("#E0262E", 0.3, 1), "sig_loadplus": ("#FF5C7A", 0.3, 1),
    "sig_coil": ("#9B59F0", 0.3, 1), "sig_chg_ctl": ("#2E86FF", 0.3, 1), "sig_inv_ctl": ("#2E86FF", 0.3, 1), "sig_conv": ("#2E86FF", 0.3, 1),
    "sig_fan": ("#8B5A2B", 0.3, 1), "sig_button": ("#F2F2F2", 0.3, 1), "sig_ac": ("#6E7076", 0.3, 1), "sig_coax": ("#D9D9D9", 0.3, 1),
    "plug_": ("#F1E6C8", 0.3, 1), "tie_": ("#101010", 0.2, 1), "fuse_inline": ("#B3262B", 0.3, 0.9), "ring_": ("#C9CCD1", 0.5, 1),
    "ctrl_j_": ("#2B2B2B", 0.3, 1), "cable_charger": ("#C0282E", 0.3, 1), "cable_inverter": ("#C0282E", 0.3, 1)})
render.CTX_KEEP = render.CTX_KEEP + ("ledboard_f", "tray2", "fan_nfa14", "plate_rear", "panel_pushbutton")
key = "c1_module_gv14up"
meta = json.load(open(os.path.join(OUT, key, "meta.json")))
R = meta["roles"]
L = [("sig_shunt", "Tesla shunt J1 → j_shunt (7 × 22 AWG)"), ("plug_shunt_j1", "J1 plug on the +x overhang (faces the board)"),
     ("sig_gnd", "GND from node A (18 AWG)"), ("sig_bplus", "B+ from the Z-strap foot"), ("fuse_inline_bplus", "B+ 2 A ATM inline fuse"),
     ("sig_loadplus", "LOAD+ from the inverter-fuse stud"), ("fuse_inline_loadplus", "LOAD+ 2 A ATM inline fuse"),
     ("sig_coil", "contactor coil leads"), ("sig_conv", "converter control (DF11 + CN301)"), ("sig_chg_ctl", "charger DF11 lead"),
     ("sig_inv_ctl", "inverter CN301 lead"), ("sig_fan", "NF-A14 fan lead"), ("sig_button", "lid push-button lead"),
     ("ctrl_j_", "board headers (Micro-Fit, top edge)"), ("plug_j_", "mated plugs"), ("tie_", "cable tie"),
     ("ring_gnd", "GND ring under the node-A nut"), ("ring_loadplus", "LOAD+ ring on the inverter lug"),
     ("strap_main", "Z-strap (service disconnect)"), ("contactor_gv141", "GV141BAX"), ("sb175_housing", "SB175"),
     ("bs2151_body", "Blue Sea 2151"), ("bs5191_fuse_0_body", "MRBF 250 A"), ("shunt_module", "Tesla shunt"),
     ("charger", "Charger"), ("inverter", "Inverter"), ("ledboard_f", "front board (back face)"), ("tray2", "tray 2"),
     ("sig_ac", "AC (mains, rear)"), ("cable_inverter", "inverter + lead"), ("cable_neg_inverter", "inverter − lead")]
SUB = "Claude battery pack v16.1 | signal + low-power wiring | fast render, lid removed"
H = ("body_half_B", "lid", "cap_", "diffuser_f", "pipe_f", "panel_outlet", "panel_inlet", "keepout_")
out = []
out.append(shot(key, R, L, "harness_iso.png", "Signal wiring: every lead routed, tied and plugged", SUB,
                view=(0.9, -0.75, 0.95), focal=(95, -5, 280), dist=470, hide=H + ("inverter", "tray2"), size=(1600, 1200)))
out.append(shot(key, R, L, "harness_top.png", "Top view: two runs to the board, both outside the Z-strap and fuse lift-out prisms", SUB,
                view=(0.0, 0.0, 1.0), focal=(95, -5, 280), dist=560, up=(1, 0, 0), hide=H + ("inverter", "tray2"), size=(1600, 1200)))
out.append(shot(key, R, L, "harness_shunt.png", "Tesla shunt: J1 on the +x overhang, wires straight up, then +y clear of the Z-strap", SUB,
                view=(0.6, -1.0, 0.75), focal=(98, -22, 270), dist=210, hide=H + ("body_half_A", "inverter", "tray2", "sig_fan", "sig_button", "charger"), size=(1600, 1200)))
out.append(shot(key, R, L, "harness_board.png", "Board end: headers on the top edge, plugs mate from above", SUB,
                view=(-0.9, -0.55, 0.75), focal=(160, -20, 292), dist=260, hide=H + ("inverter", "tray2"), size=(1600, 1200)))
out.append(shot(key, R, L, "harness_rear.png", "Fan lead: on tray 2 beside the inverter, two ties through tray-2 slots", SUB,
                view=(-0.6, 1.0, 0.8), focal=(-90, 40, 285), dist=420, hide=("body_half_A", "body_half_B", "lid", "cap_", "plate_rear"), size=(1600, 1200)))
print("\n".join(out))
