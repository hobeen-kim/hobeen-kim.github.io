"""CH14 §CAN 커널 드라이버와 SocketCAN 경계 — 수신 경로와 가변/불변 구분 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 왼쪽 그룹 — 칩셋·보드 종속
    d.box(1, 8, 50, 26, P["gray"], ec=P["edge"])
    d.text(26, 31.5, "칩셋·보드 종속 — 보드가 바뀌면 교체", size=10, color=P["dim"])

    d.box(3, 14, 12, 10, P["chip"])
    d.text(9, 19, "CAN 버스\n(트랜시버)", size=10)

    d.box(19, 14, 14, 10, P["blue"])
    d.text(26, 19, "CAN 컨트롤러\n(mailbox 레지스터)", size=10)

    d.box(37, 14, 12, 10, P["blue"])
    d.text(43, 19, "드라이버\n(flexcan 등)", size=10)

    # 경계선 — can_frame
    d.arrow(53.5, 6, 53.5, 36, color=P["orange"], style="-", ls="--", lw=1.4)
    d.text(53.5, 38.5, "struct can_frame — 하드웨어 독립 경계", size=9.5, color=P["orange"])

    # 오른쪽 그룹 — 공통
    d.box(57, 8, 42, 26, P["gray"], ec=P["edge"])
    d.text(78, 31.5, "공통 — 어떤 보드에서도 동일", size=10, color=P["dim"])

    d.box(59, 14, 15, 10, P["green"])
    d.text(66.5, 19, "SocketCAN 코어\n(af_can, raw, j1939)", size=9.5)

    d.box(78, 14, 18, 10, P["purple"])
    d.text(87, 19, "agcand\nread(s, &frame, ...)", size=10)

    # 흐름 화살표
    d.arrow(15, 19, 19, 19)
    d.arrow(33, 19, 37, 19)
    d.text(35, 22.5, "IRQ", size=8.5, color=P["dim"])
    d.arrow(49, 19, 59, 19)
    d.text(54, 15.5, "netif_receive_skb()", size=8.5, color=P["dim"])
    d.arrow(74, 19, 78, 19)


diagram("14-can-rx-path", draw, w=13, h=5.2, ymax=42)
