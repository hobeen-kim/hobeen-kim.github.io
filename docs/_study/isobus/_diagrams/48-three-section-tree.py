"""48장 4절: 3섹션 붐 살포기 연습 예제의 DDOP 계층, Object ID 0~16 (light/dark PNG)."""
from _common import diagram

TYPE_COLOR = {"DVC": "purple", "DET": "blue", "DPD": "green", "DPT": "brown", "DVP": "gray"}
H = 7.4


def draw(d):
    P = d.P

    def node(x, y, w, kind, label, size=6.9):
        d.box(x, y, w, H, P[TYPE_COLOR[kind]])
        d.text(x + w / 2, y + H - 1.6, kind, size=8.0, weight="bold")
        d.text(x + w / 2, y + (H - 2.4) / 2, label, size=size)
        return (x + w / 2, y + H), (x + w / 2, y)

    def link(a, b, color=None):
        d.arrow(a[0], a[1], b[0], b[1], color=color or P["dim"], lw=1.1)

    dvc_t, dvc_b = node(39, 53.5, 22, "DVC", "Obj 0\n3섹션 붐 살포기")
    root_t, root_b = node(39, 41.0, 22, "DET", "Obj 2, El 0\ntype Device (루트)")
    link(dvc_b, root_t)

    # 루트가 참조하는 DPT
    d.box(72, 41.0, 20, H, P[TYPE_COLOR["DPT"]])
    d.text(82, 41.0 + H - 1.6, "DPT", size=8.0, weight="bold")
    d.text(82, 41.0 + (H - 2.4) / 2, "Obj 6\n작업 폭 9 m", size=6.9)
    d.arrow(61, 41.0 + H / 2, 72, 41.0 + H / 2, color=P["dim"], lw=1.1)

    groups = [(1.5, "Obj 3, El 1\nSection 1 (좌, 3 m)", 7),
              (34.3, "Obj 4, El 2\nSection 2 (중, 3 m)", 10),
              (67.1, "Obj 5, El 3\nSection 3 (우, 3 m)", 13)]
    bw, gap = 9.6, 1.0
    gw = 3 * bw + 2 * gap
    dvp_x, dvp_w, dvp_y = 40, 20, 2.0
    dvp_top = (dvp_x + dvp_w / 2, dvp_y + H)
    for gx, label, first in groups:
        s_t, s_b = node(gx + gw / 2 - 12, 28.0, 24, "DET", label)
        link(root_b, s_t)
        for j, (ddi, name) in enumerate((("DDI 1", "Setpoint"), ("DDI 2", "Measurement"),
                                         ("DDI 289", "Work State"))):
            x = gx + j * (bw + gap)
            p_t, p_b = node(x, 15.0, bw, "DPD", f"Obj {first + j}\n{ddi}\n{name}", size=6.2)
            link(s_b, p_t)
            if j < 2:
                d.arrow(p_b[0], p_b[1], dvp_top[0] + (x - 50) * 0.12, dvp_top[1],
                        color=P["violet"], lw=0.9)
    node(dvp_x, dvp_y, dvp_w, "DVP", "Obj 16\nL/ha, Scale 0.0001")


diagram("48-three-section-tree", draw, w=12.5, h=7.6, xmax=100, ymax=62)
