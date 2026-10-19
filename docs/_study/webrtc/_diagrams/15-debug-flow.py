"""CH15 §5 디버깅 플로 — 계층별로 위에서 아래로 좁혀 가는 판단 순서 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    def label(x, y, s, color):
        d.ax.text(x, y, s, fontsize=8.5, color=color, ha="center",
                  va="center", zorder=6,
                  bbox=dict(facecolor=P["bg"], edgecolor="none", pad=1.2))

    steps = [
        ("① 시그널링 완료?\n(signalingState stable)",
         "시그널링 서버 로그 · offer/answer 순서 · 인증"),
        ("② ICE 연결?\n(iceConnectionState connected)",
         "후보 종류 · TURN 도달성 · UDP 차단"),
        ("③ DTLS 연결?\n(transport.dtlsState connected)",
         "fingerprint 불일치 · setup 역할 · 패킷 차단"),
        ("④ 패킷 수신?\n(inbound bytesReceived 증가)",
         "transceiver 방향 · 트랙 누락 · SFU 구독"),
        ("⑤ 디코딩?\n(framesDecoded 증가)",
         "키프레임 부재(PLI) · 코덱 불일치 · 재생 정책"),
        ("⑥ 품질 정상?\n(손실 · RTT · qualityLimitationReason)",
         "혼잡 · 비트레이트 · CPU · 지터 버퍼"),
    ]

    top = 55.5
    gap = 9.4
    h = 6.6
    for i, (q, cause) in enumerate(steps):
        y = top - i * gap
        last = i == len(steps) - 1
        d.box(4, y - h / 2, 40, h, P["blue"],
              ec=P["accent"] if i == 0 else None, lw=1.6)
        d.text(24, y, q, size=9.5)
        cause_fc = P["purple"] if last else P["brown"]
        d.box(57, y - h / 2, 40, h, cause_fc)
        d.text(77, y, cause, size=9.5)
        d.arrow(44, y, 57, y, color=P["orange"])
        label(50.5, y + 1.6, "아니오" if not last else "아니오 → 튜닝",
              P["orange"])
        if not last:
            d.arrow(24, y - h / 2, 24, y - gap + h / 2, color=P["accent"])
            label(27, y - gap / 2, "예", P["accent"])


diagram("15-debug-flow", draw, w=12, h=8.2, ymax=60)
