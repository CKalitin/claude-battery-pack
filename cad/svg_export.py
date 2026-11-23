"""Convert widget SVGs (c-* ramp classes, t/ts/th text classes) to standalone SVGs for GitHub."""
import sys, xml.etree.ElementTree as ET
NS = "http://www.w3.org/2000/svg"; ET.register_namespace("", NS)
R = {"gray": ("#F1EFE8", "#5F5E5A", "#2C2C2A", "#5F5E5A"), "teal": ("#E1F5EE", "#0F6E56", "#085041", "#0F6E56"),
     "coral": ("#FAECE7", "#993C1D", "#712B13", "#993C1D"), "red": ("#FCEBEB", "#A32D2D", "#791F1F", "#A32D2D"),
     "amber": ("#FAEEDA", "#854F0B", "#633806", "#854F0B"), "blue": ("#E6F1FB", "#185FA5", "#0C447C", "#185FA5")}
TXT = {"t": ("14", "400", "#2C2C2A"), "ts": ("12", "400", "#5F5E5A"), "th": ("14", "500", "#2C2C2A")}
def walk(e, ramp):
    cls = e.get("class", "")
    r = next((c[2:] for c in cls.split() if c.startswith("c-")), None) or ramp
    tag = e.tag.split("}")[1]
    if tag in ("rect", "circle") and r and not e.get("fill"):
        e.set("fill", R[r][0]); e.set("stroke", R[r][1])
    if tag == "text":
        k = next((c for c in cls.split() if c in TXT), "t"); size, w, col = TXT[k]
        if r: col = R[r][2] if k != "ts" else R[r][3]
        e.set("font-family", "Helvetica, Arial, sans-serif"); e.set("font-size", size); e.set("font-weight", w); e.set("fill", col)
    if cls: del e.attrib["class"]
    for c in e: walk(c, r)
for src, dst in zip(sys.argv[1::2], sys.argv[2::2]):
    root = ET.parse(src).getroot()
    vb = root.get("viewBox").split()
    for c in list(root): walk(c, None)
    bg = ET.Element(f"{{{NS}}}rect", {"x": "0", "y": "0", "width": vb[2], "height": vb[3], "fill": "#FFFFFF"})
    idx = 1 + next((i for i, c in enumerate(root) if c.tag.endswith("defs")), 0)
    root.insert(idx, bg); root.set("width", vb[2]); root.set("height", vb[3])
    s = ET.tostring(root, encoding="unicode").replace('var(--b)', '#888780')
    open(dst, "w").write(s)
    print(dst)
