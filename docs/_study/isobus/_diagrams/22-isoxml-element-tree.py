"""CH22 §5 TASKDATA.XML 주요 요소 계층 — coding data와 task data (light/dark PNG)."""
from _common import diagram

IDREFS = [
    "TSK   C, D, E, F  ->  CTR, FRM, PFD, WKR",
    "PDV   C -> PDT    D -> DET    E -> VPN",
    "DLV   C -> DET    DLT   H -> DET",
    "DAN   C -> DVC    OTP   A -> CPC",
]


def node(d, cx, cy, label, fc, w=7.0, h=3.6, size=9.5):
    d.box(cx - w / 2, cy - h / 2, w, h, fc)
    d.text(cx, cy, label, size=size)


def link(d, x1, y1, x2, y2):
    d.arrow(x1, y1, x2, y2, color=d.P["edge"], lw=1.2, style="-")


def draw(d):
    P = d.P
    node(d, 50, 53, "ISO11783_TaskData", P["chip"], w=22, h=3.8, size=10)

    d.box(1.5, 1.5, 46, 46, P["gray"], ec=P["accent"])
    d.text(3.5, 45.2, "루트 바로 아래 (TSK 제외)", size=10, weight="bold", ha="left", color=P["accent"])
    d.box(52.5, 1.5, 46, 46, P["gray"], ec=P["accent"])
    d.text(54.5, 45.2, "TSK와 그 아래", size=10, weight="bold", ha="left", color=P["accent"])
    d.box(29, 7.6, 3, 2.2, P["blue"], r=0.005)
    d.text(33, 8.7, "coding data (Table 2)", size=8.5, ha="left", color=P["dim"])
    d.box(29, 3.9, 3, 2.2, P["chip"], r=0.005)
    d.text(33, 5.0, "그 밖 (task data)", size=8.5, ha="left", color=P["dim"])
    link(d, 44, 51.1, 24.5, 47.5)
    link(d, 56, 51.1, 75.5, 47.5)

    for i, tag in enumerate(["CTR", "FRM", "PDT", "VPN", "WKR", "CPC"]):
        node(d, 7.5 + i * 7.2, 39.5, tag, P["blue"], w=6.2)

    node(d, 10, 30, "PFD", P["blue"])
    for cy, tag in [(23, "PLN"), (16, "LSG"), (9, "PNT")]:
        node(d, 10, cy, tag, P["chip"])
        link(d, 10, cy + 5.2, 10, cy + 1.8)

    node(d, 33, 30, "DVC", P["blue"])
    for cx, tag in [(22, "DET"), (29.5, "DPD"), (37, "DPT"), (44, "DVP")]:
        node(d, cx, 21, tag, P["blue"], w=6.2)
        link(d, 33, 28.2, cx, 22.8)
    node(d, 22, 12, "DOR", P["blue"], w=6.2)
    link(d, 22, 19.2, 22, 13.8)

    node(d, 75.5, 39.5, "TSK", P["chip"], w=9)
    kids = [(57.5, "TZN"), (63.5, "TIM"), (69.5, "OTP"), (75.5, "DAN"),
            (81.5, "DLT"), (87.5, "TLG"), (93.5, "GRD")]
    for cx, tag in kids:
        node(d, cx, 30, tag, P["chip"], w=5.4)
        link(d, 75.5, 37.7, cx, 31.8)
    for cx, px, tag in [(56.5, 57.5, "PDV"), (62.8, 63.5, "PTN"), (69.1, 63.5, "DLV"),
                        (75.5, 75.5, "ASP")]:
        node(d, cx, 21, tag, P["chip"], w=5.4)
        link(d, px, 28.2, cx, 22.8)

    ref = P["orange"]
    d.text(56, 15.2, "IDREF", size=9, weight="bold", color=ref, ha="left")
    for i, line in enumerate(IDREFS):
        d.text(56, 12.3 - i * 2.7, line, size=8.5, color=ref, ha="left")


diagram("22-isoxml-element-tree", draw, w=13, h=7, xmax=100, ymax=56)
