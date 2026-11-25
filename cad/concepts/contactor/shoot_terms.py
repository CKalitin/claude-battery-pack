"""Converter terminals + plug keep-outs (option A layout)."""
import json, os
from render import shot, OUT
key = "c1_module_gv14up"
meta = json.load(open(os.path.join(OUT, key, "meta.json")))
R = meta["roles"]
LF = [("term_chg_dc_tb", "charger DC terminal block V+/V−"), ("term_chg_sig", "charger DF11 signal"),
      ("term_inv_dc_pp45", "inverter DC TB1: Anderson PP45 pair"), ("term_inv_sig", "inverter remote CN301"),
      ("keepout_chg_dc", "keep-out: 8 AWG lead + bend (27 mm)"), ("keepout_inv_dc", "keep-out: PP75 plug + 6 AWG bend (42 mm)"),
      ("cable_charger", "charger + lead from 2151"), ("cable_inverter", "inverter + lead from 2151"), ("cable_neg_charger", "charger − lead"), ("cable_neg_inverter", "inverter − lead"),
      ("charger", "Charger NPB-450-12"), ("inverter", "Inverter NTS-400P-112"), ("sb175_housing", "SB175")]
LR = [("term_chg_ac_c14", "charger IEC C14 inlet"), ("term_inv_ac_cn500", "inverter AC out CN500 (JST VH)"),
      ("keepout_chg_ac", "keep-out: right-angle C13 (36 mm)"), ("keepout_inv_ac", "keep-out: VH plug + wires (20 mm)"),
      ("panel_inlet", "lid IEC C14 inlet (rear)"), ("panel_outlet", "lid NEMA 5-15 outlet (rear)"), ("cable_ac_in", "AC in"),
      ("cable_ac_out", "AC out"), ("fan_", "Noctua NF-A14 (rear)"), ("charger", "Charger NPB-450-12"), ("inverter", "Inverter NTS-400P-112")]
H = ("body_half_B", "ledboard_f", "ctrl_", "cap_", "lid", "tray2", "diffuser_f", "pipe_f")
print(shot(key, R, LF, "terms_dc_front.png", "DC ends face the power bay (front)",
           "terminal positions on each face UNCONFIRMED; blue = plug + cable-bend keep-outs, all clear", view=(0.55, 1.0, 0.55),
           focal=(40, 20, 270), dist=420, hide=H, ghost=("keepout_",)))
print(shot(key, R, LR, "terms_ac_rear.png", "AC ends face the rear; AC pass-throughs moved to the rear of the lid",
           "inside length 375 → 420 mm, all added at the rear; converters −27 mm", view=(-1.0, 0.75, 0.6),
           focal=(-200, 0, 280), dist=430, hide=H + ("plate_rear", "screws_r", "screws_fan"), ghost=("keepout_",)))
