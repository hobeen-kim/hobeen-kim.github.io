"""CH21 §3.2 SCM 상태 머신 — ISO 11783-14 Figure 4 재구성 (light/dark PNG)."""
from _common import diagram


def node(d, cx, cy, w, h, label, fc):
    d.box(cx - w / 2, cy - h / 2, w, h, fc)
    d.text(cx, cy, label, size=10.5, weight="bold")


def draw(d):
    P = d.P

    # Active 그룹 (Ready ~ Abort)
    d.box(3, 3, 94, 41, P["gray"], ec=P["accent"], lw=1.2)
    d.text(5, 41.6, "Active 상태: SCMasterStatus 연속 송신", size=9, color=P["dim"], ha="left")

    # 시동 → Inactive
    d.ax.plot([22], [54], marker="o", markersize=9, color=P["text"])
    d.arrow(23.2, 54, 40.5, 54)
    d.text(31.5, 56.2, "Initialization 1회", size=8.5, color=P["dim"])
    node(d, 50, 54, 18, 5.5, "Inactive", P["chip"])

    node(d, 50, 31, 18, 6, "Ready", P["blue"])
    node(d, 15, 31, 20, 6, "Recording", P["green"])
    node(d, 15, 9.5, 22, 6, "Recording\nCompletion", P["green"])
    node(d, 85, 31, 20, 6, "Play Back", P["brown"])
    node(d, 85, 9.5, 20, 6, "Abort", P["purple"])

    # Inactive <-> Ready
    d.arrow(47, 51.2, 47, 34.1)
    d.text(45.5, 47, "SCM_A", size=8.5, ha="right")
    d.arrow(53, 34.1, 53, 51.2)
    d.text(54.5, 47, "SCM_B", size=8.5, ha="left")

    # Ready <-> Recording
    d.arrow(40.9, 32.5, 25.1, 32.5)
    d.text(33, 34.4, "SCM_C", size=8.5)
    d.arrow(25.1, 29.5, 40.9, 29.5)
    d.text(33, 27.4, "SCM_D / I / E* / F*", size=8.5)

    # Recording -> Recording Completion
    d.arrow(15, 27.9, 15, 12.6)
    d.text(16.5, 20, "SCM_G", size=8.5, ha="left")

    # Recording Completion -> Ready
    d.arrow(26.1, 11, 46, 27.9)
    d.text(38.5, 16.5, "SCM_H / I / E* / F*", size=8.5, ha="left")

    # Ready <-> Play Back
    d.arrow(59.1, 32.5, 74.9, 32.5)
    d.text(67, 34.4, "SCM_K", size=8.5)
    d.arrow(74.9, 29.5, 59.1, 29.5)
    d.text(67, 27.4, "SCM_L", size=8.5)

    # Play Back -> Abort
    d.arrow(85, 27.9, 85, 12.6)
    d.text(86.5, 20, "SCM_M / N\nR* / P* / F*", size=8.5, ha="left")

    # Abort -> Ready
    d.arrow(74.9, 11, 54, 27.9)
    d.text(63.5, 16.5, "SCM_T", size=8.5, ha="right")

    d.text(95.5, 4.6, "* 선택(optional) 천이", size=8, color=P["dim"], ha="right")


diagram("21-scm-state-machine", draw, w=12, h=6.6, xmax=100, ymax=60)
