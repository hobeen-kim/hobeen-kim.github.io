"""CH03 §4 하이브리드 시그널링 — 브라우저는 WebSocket, 디바이스는 MQTT (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    d.box(2, 26, 18, 9, P["green"])
    d.text(11, 30.5, "운영자 브라우저", size=9.5)

    d.box(30, 26, 20, 9, P["brown"])
    d.text(40, 30.5, "시그널링 백엔드\n(인증 · 인가 · 라우팅)", size=9)

    d.box(60, 26, 16, 9, P["purple"])
    d.text(68, 30.5, "MQTT 브로커\n(AWS IoT Core 등)", size=9)

    d.box(84, 26, 14, 9, P["blue"])
    d.text(91, 30.5, "농기계\n디바이스", size=9.5)

    # 시그널링 구간
    d.arrow(20, 30.5, 30, 30.5, color=P["accent"], style="<|-|>")
    d.text(25, 33, "WSS", size=8, color=P["accent"])
    d.arrow(50, 30.5, 60, 30.5, color=P["orange"], style="<|-|>")
    d.text(55, 33, "pub/sub", size=8, color=P["orange"])
    d.arrow(76, 30.5, 84, 30.5, color=P["orange"], style="<|-|>")
    d.text(80, 33, "MQTT\n(mTLS)", size=8, color=P["orange"])

    # 토픽
    d.text(68, 22.6, "signaling/{deviceId}/in", size=7.8, color=P["dim"])
    d.text(68, 20.2, "signaling/{deviceId}/out", size=7.8, color=P["dim"])

    # 미디어
    d.arrow(11, 26, 11, 10, color=P["violet"], style="-", lw=2.4)
    d.arrow(91, 26, 91, 10, color=P["violet"], style="-", lw=2.4)
    d.arrow(11, 10, 91, 10, color=P["violet"], lw=2.4, style="<|-|>")
    d.text(51, 11.8, "미디어 · DataChannel — 시그널링 경로와 무관하게 직접(또는 TURN)",
           size=8.2, color=P["violet"])

    d.text(25, 39, "브라우저 친화", size=8, color=P["dim"])
    d.text(76, 39, "디바이스는 기존 MQTT 연결 재사용", size=8, color=P["dim"])


diagram("03-transport-bridge", draw, w=12, h=4.6, ymax=44)
