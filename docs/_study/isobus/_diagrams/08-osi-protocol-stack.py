"""CH08 §2 OSI 7계층과 CAN 기반 프로토콜 스택 (light/dark PNG)."""
from _common import diagram

LAYERS = ["1 물리 (Physical)", "2 데이터 링크 (Data Link)", "3 네트워크 (Network)",
          "4 전송 (Transport)", "5 세션 (Session)", "6 표현 (Presentation)",
          "7 응용 (Application)"]


def draw(d):
    P = d.P
    h, gap, y0 = 6.4, 1.0, 2.0

    def ly(i):
        return y0 + i * (h + gap)

    d.text(16, ly(7) + 2.2, "OSI 7계층", size=10, weight="bold")
    for i, name in enumerate(LAYERS):
        d.box(2, ly(i), 28, h, P["gray"])
        d.text(16, ly(i) + h / 2, name, size=9.2)

    top = ly(6) + h
    d.text(67, ly(7) + 2.2, "CAN 기반 프로토콜 스택", size=10, weight="bold")

    upper_y = ly(2)
    d.box(36, upper_y, 62, top - upper_y, P["chip"])
    d.text(67, top - 3.0, "상위 프로토콜 (3~7계층)", size=9.6, color=P["dim"])
    chips = [
        (39, "CANopen\n산업 자동화", P["blue"], None),
        (68, "DeviceNet\n공장 자동화", P["green"], None),
    ]
    chips2 = [
        (39, "SAE J1939\n대형 차량·농기계", P["purple"], None),
        (68, "ISOBUS (ISO 11783)\n농기계 전용", P["brown"], P["accent"]),
    ]
    cw, ch = 27, 11.5
    for x, label, fc, ec in chips:
        d.box(x, upper_y + 17.5, cw, ch, fc, ec=ec)
        d.text(x + cw / 2, upper_y + 17.5 + ch / 2, label, size=9.4)
    for x, label, fc, ec in chips2:
        d.box(x, upper_y + 3.0, cw, ch, fc, ec=ec, lw=1.4 if ec is None else 2.0)
        d.text(x + cw / 2, upper_y + 3.0 + ch / 2, label, size=9.4)

    lower_top = ly(1) + h
    d.box(36, ly(0), 62, lower_top - ly(0), P["blue"])
    d.text(67, (ly(0) + lower_top) / 2, "CAN 2.0B\n(데이터 링크 + 물리)", size=9.8)

    for yy in (upper_y, top):
        d.ax.plot([31, 35], [yy, yy], color=P["edge"], lw=0.9, ls=":")
    for yy in (ly(0), lower_top):
        d.ax.plot([31, 35], [yy, yy], color=P["edge"], lw=0.9, ls=":")


diagram("08-osi-protocol-stack", draw, w=10.5, h=6.2, xmax=100, ymax=59)
