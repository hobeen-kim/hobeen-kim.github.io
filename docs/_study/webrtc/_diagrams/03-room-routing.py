"""CH03 §3 방 기반 라우팅 — rooms 맵과 to/from 중계 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 뷰어 클라이언트
    viewers = [(36, "v-7c"), (26, "v-9e"), (12, "v-31")]
    for y, pid in viewers:
        d.box(2, y, 14, 6, P["green"])
        d.text(9, y + 3, f"뷰어 {pid}", size=9)

    # 디바이스 클라이언트
    d.box(84, 30, 14, 6, P["blue"])
    d.text(91, 33, "디바이스 d-1a", size=9)
    d.box(84, 10, 14, 6, P["blue"])
    d.text(91, 13, "디바이스 d-55", size=9)

    # 서버
    d.box(26, 4, 48, 42, P["gray"], ec=P["accent"], lw=1.8)
    d.text(50, 43.8, "시그널링 서버 — rooms: Map<room, Map<peerId, peer>>",
           size=9, weight="bold", color=P["accent"])

    # room tractor-17
    d.box(29, 22, 42, 19, P["chip"])
    d.text(31, 39.3, 'room "tractor-17"', size=8.5, color=P["dim"], ha="left")
    d.text(69, 39.3, "device 1 · viewer ≤ N", size=7.8, color=P["dim"], ha="right")
    d.box(31, 29, 10, 5.5, P["green"])
    d.text(36, 31.75, "v-9e\n(viewer)", size=8)
    d.box(42.5, 29, 10, 5.5, P["green"])
    d.text(47.5, 31.75, "v-7c\n(viewer)", size=8)
    d.box(58, 29, 11, 5.5, P["blue"])
    d.text(63.5, 31.75, "d-1a\n(device)", size=8)
    d.arrow(52.5, 31.75, 58, 31.75, color=P["accent"], lw=1.4)
    d.text(55.3, 26.2, "to로 대상 조회\nfrom 기입", size=7.5, color=P["accent"])

    # room tractor-23
    d.box(29, 7, 42, 12, P["chip"])
    d.text(31, 16.8, 'room "tractor-23"', size=8.5, color=P["dim"], ha="left")
    d.box(31, 8.5, 10, 5.5, P["green"])
    d.text(36, 11.25, "v-31\n(viewer)", size=8)
    d.box(58, 8.5, 11, 5.5, P["blue"])
    d.text(63.5, 11.25, "d-55\n(device)", size=8)

    # 연결선 (소켓)
    for y, _ in viewers:
        d.ax.plot([16, 26], [y + 3, y + 3], color=P["edge"], lw=1.0, zorder=1)
    for y in (33, 13):
        d.ax.plot([74, 84], [y, y], color=P["edge"], lw=1.0, zorder=1)

    # 중계 흐름: v-7c → server → d-1a
    d.arrow(16, 37.5, 46, 34.6, color=P["orange"])
    d.text(4, 44.4, '① {"type":"offer","to":"d-1a"}', size=7.8,
           color=P["orange"], ha="left")
    d.arrow(69, 33.2, 84, 34.6, color=P["violet"])
    d.text(98, 41.4, '② {"type":"offer","from":"v-7c"}', size=7.8,
           color=P["violet"], ha="right")
    d.text(98, 38.8, "(from은 서버가 기입)", size=7.5, color=P["violet"],
           ha="right")


diagram("03-room-routing", draw, w=12, h=6.4, ymax=50)
