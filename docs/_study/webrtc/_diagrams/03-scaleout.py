"""CH03 §3 시그널링 서버 스케일아웃 — 노드 간 pub/sub 중계 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 클라이언트
    d.box(2, 30, 18, 7, P["green"])
    d.text(11, 33.5, "뷰어 v-7c\n(room tractor-17)", size=8.5)
    d.box(80, 30, 18, 7, P["blue"])
    d.text(89, 33.5, "디바이스 d-1a\n(room tractor-17)", size=8.5)

    # LB
    d.box(36, 40, 28, 6, P["chip"])
    d.text(50, 43, "로드밸런서 (WSS 종단 · idle timeout)", size=8.5)

    # 노드
    d.box(22, 20, 22, 9, P["brown"])
    d.text(33, 24.5, "시그널링 노드 A\n(v-7c 소켓 보유)", size=8.5)
    d.box(56, 20, 22, 9, P["brown"])
    d.text(67, 24.5, "시그널링 노드 B\n(d-1a 소켓 보유)", size=8.5)

    # pub/sub
    d.box(34, 4, 32, 8, P["purple"])
    d.text(50, 8, "Redis Pub/Sub · NATS 등\n(채널: peer:{peerId})", size=8.5)

    # 소켓 연결
    d.arrow(11, 37, 38, 40, color=P["edge"], lw=1.2, style="-")
    d.arrow(89, 37, 62, 40, color=P["edge"], lw=1.2, style="-")
    d.arrow(44, 40, 33, 29, color=P["edge"], lw=1.2, style="-")
    d.arrow(56, 40, 67, 29, color=P["edge"], lw=1.2, style="-")

    # 메시지 흐름
    d.arrow(15, 30, 24, 26, color=P["accent"])
    d.text(12.5, 26.5, "① offer\n(to: d-1a)", size=7.8, color=P["accent"])
    d.arrow(33, 20, 42, 12, color=P["orange"])
    d.text(31.5, 15, "② publish\npeer:d-1a", size=7.8, color=P["orange"])
    d.arrow(58, 12, 67, 20, color=P["orange"])
    d.text(70.5, 15, "③ 구독 중인\n노드가 수신", size=7.8, color=P["orange"])
    d.arrow(76, 26, 85, 30, color=P["accent"])
    d.text(88, 26.5, "④ offer\n(from: v-7c)", size=7.8, color=P["accent"])


diagram("03-scaleout", draw, w=12, h=5.6, ymax=48)
