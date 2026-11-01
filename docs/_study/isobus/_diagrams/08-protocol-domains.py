"""CH08 §2 CAN 위 상위 프로토콜과 적용 도메인 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    def node(x, y, w, h, label, fc, ec=None, lw=1.4):
        d.box(x, y, w, h, fc, ec=ec, lw=lw)
        d.text(x + w / 2, y + h / 2, label, size=9.4)

    node(2, 19, 21, 12, "CAN\n물리·링크 계층", P["gray"])
    node(36, 36, 28, 12, "CANopen\n산업 자동화\n(PLC, 모터 제어)", P["blue"])
    node(36, 19, 28, 12, "DeviceNet\n공장 자동화\n(센서, 액추에이터 네트워크)", P["green"])
    node(36, 2, 28, 12, "SAE J1939\n대형 차량·농기계\n(트럭, 버스, 굴착기)", P["purple"])
    node(72, 2, 26, 12, "ISOBUS (ISO 11783)\n농기계 전용\n(트랙터-작업기 통신)", P["brown"],
         ec=P["accent"], lw=2.0)

    d.arrow(23, 27, 36, 42)
    d.arrow(23, 25, 36, 25)
    d.arrow(23, 23, 36, 8)
    d.arrow(64, 8, 72, 8)


diagram("08-protocol-domains", draw, w=10.5, h=5.0, xmax=100, ymax=50)
