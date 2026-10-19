"""CH05 §2 매핑 동작 — EIM vs APDM(symmetric)에서 목적지별 외부 포트 (light/dark PNG)."""
from _common import diagram


def panel(d, ox, title, port_s, port_p, diff):
    P = d.P
    d.box(ox + 1, 2, 47, 42, P["gray"], ec=P["edge"], lw=1.2)
    d.text(ox + 24.5, 41, title, size=9.8, color=P["accent"])

    d.box(ox + 3, 18.5, 11, 8, P["green"])
    d.text(ox + 8.5, 22.5, "호스트\n10.0.0.2:5000", size=8.5)

    d.box(ox + 17, 6, 12, 30, P["brown"], ec=P["accent"], lw=1.5)
    d.text(ox + 23, 21, "NAT\n(203.0.113.7)", size=8.5)
    d.arrow(ox + 14, 22.5, ox + 17, 22.5, lw=1.5)

    d.box(ox + 36, 27, 10.5, 8, P["chip"])
    d.text(ox + 41.25, 31, "STUN 서버\nS:3478", size=8.5)
    d.box(ox + 36, 8, 10.5, 8, P["chip"])
    d.text(ox + 41.25, 12, "피어\nB:50000", size=8.5)

    d.arrow(ox + 29, 29, ox + 36, 31, color=P["accent"])
    d.text(ox + 32.5, 32.6, port_s, size=9, color=P["accent"])
    col = P["orange"] if diff else P["accent"]
    d.arrow(ox + 29, 14, ox + 36, 12, color=col)
    d.text(ox + 32.5, 15.4, port_p, size=9, color=col)
    if diff:
        d.text(ox + 41.25, 5.2, "STUN이 본 포트와 다름", size=8.3, color=P["orange"])
    else:
        d.text(ox + 41.25, 5.2, "STUN이 본 포트와 같음", size=8.3, color=P["dim"])


def draw(d):
    panel(d, 0, "EIM (Endpoint-Independent Mapping)", ":40001", ":40001", False)
    panel(d, 51, "APDM (Address and Port-Dependent)", ":40001", ":40002", True)


diagram("05-mapping-behavior", draw, w=12.5, h=5.4, ymax=46)
