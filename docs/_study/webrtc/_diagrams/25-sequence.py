"""CH25 §3 부팅 → 시청 → 제어 → 재연결 시퀀스 (light/dark PNG)."""
from _common import diagram
from matplotlib.lines import Line2D


def draw(d):
    P = d.P

    DEV, CP, KVS, BE, BR = 8, 27, 48, 69, 90
    actors = [
        (DEV, "농기계\n(KVS C SDK)", P["green"]),
        (CP, "IoT Credential\nProvider", P["gray"]),
        (KVS, "KVS 시그널링\n채널", P["gray"]),
        (BE, "백엔드", P["brown"]),
        (BR, "운영자 브라우저\n(JS SDK)", P["blue"]),
    ]

    # phase bands
    def band(y0, y1, label):
        d.box(0.6, y0, 98.8, y1 - y0, P["chip"], ec=P["edge"], lw=0.8,
              alpha=0.55)
        d.text(1.4, y1 - 1.3, label, size=8.5, color=P["accent"],
               style="italic", ha="left")

    band(57.5, 73, "① 부팅")
    band(20.5, 56.5, "② 시청 · 제어")
    band(2, 19.5, "③ loop: 약 40분마다 또는 GO_AWAY 수신 시")

    for x, name, col in actors:
        d.box(x - 8, 74.5, 16, 6, col)
        d.text(x, 77.5, name, size=9, weight="bold")
        d.ax.plot([x, x], [2, 74.5], color=P["edge"], ls=(0, (4, 3)),
                  lw=1.0, zorder=1)

    def hop(x1, x2, y, label, color, ls="-", style="-|>"):
        d.arrow(x1, y, x2, y, color=color, ls=ls, style=style)
        d.text((x1 + x2) / 2, y + 1.25, label, size=8, color=color)

    def note(x, y, s, w=20, h=4.2):
        d.box(x - w / 2, y - h / 2, w, h, P["bg"], lw=1.0)
        d.text(x, y, s, size=8)

    # ① boot
    note(DEV, 68.9, "시계 동기화\n(NTP · GNSS)", w=12, h=3.8)
    hop(DEV, CP, 64.6, "mTLS + thingname 헤더", P["violet"])
    hop(CP, DEV, 62.0, "임시 자격증명 (기본 1h)", P["violet"], ls="--")
    hop(DEV, KVS, 59.4, "Endpoint(MASTER) · IceServerConfig · ConnectAsMaster", P["accent"])

    # ② viewing
    hop(BR, BE, 53.2, "시청 요청 (OIDC 토큰)", P["orange"])
    note(BE, 48.6, "ACL · 시청 리스(≤3) 확인\nAssumeRole + 세션 정책", w=22, h=5)
    hop(BE, BR, 44.0, "VIEWER 자격증명 · clientId", P["orange"], ls="--")
    hop(BR, KVS, 40.6, "Endpoint(VIEWER) · IceServerConfig · ConnectAsViewer", P["accent"])
    hop(BR, KVS, 37.2, "SDP_OFFER", P["accent"])
    hop(KVS, DEV, 35.4, "SDP_OFFER", P["accent"])
    hop(DEV, KVS, 32.0, "SDP_ANSWER", P["accent"], ls="--")
    hop(KVS, BR, 30.2, "SDP_ANSWER", P["accent"], ls="--")
    d.arrow(DEV, 26.8, KVS, 26.8, color=P["violet"], ls="--", style="<|-|>")
    d.arrow(KVS, 26.8, BR, 26.8, color=P["violet"], ls="--", style="<|-|>")
    d.text(KVS, 28.1, "ICE_CANDIDATE (trickle)", size=8, color=P["violet"])
    d.ax.plot([DEV, BR], [22.6, 22.6], color=P["accent"], lw=3.4, zorder=3,
              solid_capstyle="round")
    d.text(58, 24.0, "P2P(srflx) 또는 TURN(relay) — 영상 + DataChannel 제어",
           size=8.5, color=P["accent"], weight="bold")

    # ③ refresh / reconnect
    hop(DEV, CP, 15.4, "자격증명 갱신", P["violet"])
    hop(DEV, KVS, 11.6, "ConnectAsMaster 재연결", P["accent"])
    hop(BR, BE, 15.4, "자격증명 재발급 (ACL 재확인)", P["orange"])
    hop(BR, KVS, 11.6, "ConnectAsViewer 재연결", P["accent"])
    note(KVS + 10, 6.0, "미디어는 유지를 시도, 끊겼으면 새 offer(ICE restart)",
         w=44, h=3.6)

    d.ax.legend(handles=[
        Line2D([0], [0], color=P["accent"], lw=2.2, label="KVS 시그널링"),
        Line2D([0], [0], color=P["violet"], lw=2.2, label="인증서 · 자격증명"),
        Line2D([0], [0], color=P["orange"], lw=2.2, label="백엔드 API"),
    ], loc="upper right", bbox_to_anchor=(0.995, 0.998), ncol=3,
        fontsize=8.5, framealpha=0.0, labelcolor=P["dim"])


diagram("25-sequence", draw, w=14, h=11.2, ymax=85)
