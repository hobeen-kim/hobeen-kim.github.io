"""CH09 §2 PF 값으로 PDU1·PDU2를 가르고 PS를 읽는 흐름 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    def node(x, y, w, h, label, fc, ec=None, lw=1.4, size=9.6):
        d.box(x, y, w, h, fc, ec=ec, lw=lw)
        d.text(x + w / 2, y + h / 2, label, size=size)

    node(34, 55, 32, 7, "29비트 CAN ID 수신", P["chip"], ec=P["accent"], lw=1.8)
    node(34, 44, 32, 7, "PF 값 확인", P["gray"])
    node(36, 33, 28, 7, "PF < 240 ?", P["purple"])
    node(6, 18, 34, 8, "PDU1\n(Peer-to-Peer)", P["blue"])
    node(60, 18, 34, 8, "PDU2\n(Broadcast)", P["green"])
    node(2, 3, 42, 9, "PS = Destination Address\n특정 노드 또는 전역(DA=255)", P["chip"], size=9.2)
    node(56, 3, 42, 9, "PS = Group Extension\n모든 노드에게 전송", P["chip"], size=9.2)

    d.arrow(50, 55, 50, 51.4)
    d.arrow(50, 44, 50, 40.4)
    d.arrow(38, 34, 25, 26.4)
    d.text(26, 31.5, "예 (PF 0~239)", size=8.8, color=P["dim"])
    d.arrow(62, 34, 75, 26.4)
    d.text(76, 31.5, "아니오 (PF 240~255)", size=8.8, color=P["dim"])
    d.arrow(23, 18, 23, 12.4)
    d.arrow(77, 18, 77, 12.4)


diagram("09-pdu-format-decision", draw, w=9.5, h=6.2, xmax=100, ymax=64)
