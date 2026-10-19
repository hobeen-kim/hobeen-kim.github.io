"""CH25 §2 전체 아키텍처 — 디바이스·AWS·백엔드·운영자 브라우저 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    def group(x, y, w, h, label, fc):
        d.box(x, y, w, h, fc, lw=1.3)
        d.text(x + 1.2, y + h - 1.6, label, size=9.5, weight="bold",
               ha="left", color=P["dim"])

    def chip(x, y, w, h, s, hl=False):
        d.box(x, y, w, h, P["chip"], ec=P["accent"] if hl else P["edge"],
              lw=1.6 if hl else 1.0)
        d.text(x + w / 2, y + h / 2, s, size=8.5)

    # groups
    group(0.5, 3, 20, 51.5, "농기계 (LTE · CGNAT)", P["green"])
    group(28, 21.5, 44, 33, "AWS (ap-northeast-2)", P["gray"])
    group(28, 1, 44, 18, "백엔드", P["brown"])
    group(79.5, 3, 20, 51.5, "운영자 브라우저", P["blue"])

    # device chips
    chip(2, 43.5, 17, 6, "카메라 1~2대\n(V4L2 · CSI)")
    chip(2, 35.5, 17, 6, "HW 인코더\n(H.264)")
    chip(2, 27.5, 17, 6, "KVS C SDK\n(MASTER)", hl=True)
    chip(2, 19.5, 17, 6, "IoT 에이전트\n(MQTT · X.509)")
    chip(2, 11.5, 17, 6, "안전 컨트롤러\n(워치독 · CAN)")
    chip(2, 4, 17, 6, "로컬 녹화\n(링 버퍼 → S3)")
    d.arrow(10.5, 43.5, 10.5, 41.6, color=P["edge"], lw=1.2)
    d.arrow(10.5, 35.5, 10.5, 33.6, color=P["edge"], lw=1.2)

    # AWS chips
    chip(40, 45, 20, 6, "관리형 STUN/TURN\n(UDP · TCP · TLS 443)")
    chip(36, 36.5, 28, 6, "KVS 시그널링 채널\n(WSS · 채널명 = thingName)", hl=True)
    chip(29.5, 29, 19, 6, "IoT Credential Provider\n(role alias)")
    chip(51.5, 29, 19, 6, "S3\n(사건 영상)")
    chip(29.5, 22.5, 19, 5, "IoT Core (MQTT · Shadow)")

    # backend chips
    chip(29.5, 9.5, 19, 6, "채널 프로비저닝\n(CreateSignalingChannel)")
    chip(51.5, 9.5, 19, 6, "권한 · 시청 리스\n(ACL · 동시 3명)")
    chip(29.5, 2.5, 19, 5.5, "STS 자격증명 발급\n(세션 정책)")
    chip(51.5, 2.5, 19, 5.5, "명령 · 사건 API")

    # browser chips
    chip(81, 43.5, 17, 6, "웹 콘솔\n(OIDC 로그인)")
    chip(81, 33, 17, 6, "KVS JS SDK\n(VIEWER)", hl=True)
    chip(81, 22.5, 17, 6, "RTCPeerConnection\n(영상 · DataChannel)")
    chip(81, 11.5, 17, 6, "녹화 재생\n(presigned URL)")

    # media path: P2P (solid) and TURN relay (dashed)
    d.ax.plot([7, 7, 93, 93], [54.5, 60, 60, 54.5], color=P["accent"],
              lw=3.0, zorder=3, solid_capstyle="round")
    d.text(50, 61.3, "미디어 + DataChannel — P2P 직결 (DTLS-SRTP)", size=9,
           color=P["accent"], weight="bold")
    d.ax.plot([14, 14, 45], [54.5, 57.2, 57.2], color=P["orange"], lw=1.6,
              ls=(0, (5, 3)), zorder=3)
    d.arrow(45, 57.2, 45, 51.2, color=P["orange"], lw=1.6, ls="--")
    d.ax.plot([55, 55, 86], [51, 57.2, 57.2], color=P["orange"], lw=1.6,
              ls=(0, (5, 3)), zorder=3)
    d.arrow(86, 57.2, 86, 54.6, color=P["orange"], lw=1.6, ls="--")
    d.text(70.5, 58.4, "직결 실패 시 TURN 릴레이", size=8.5, color=P["orange"])

    # device -> AWS
    d.arrow(19.1, 31.5, 36, 39.2, color=P["accent"], style="<|-|>")
    d.text(24.2, 37.4, "WSS", size=8.5, color=P["accent"])
    d.arrow(19.1, 30, 29.4, 31.5, color=P["violet"])
    d.text(24.6, 29.2, "mTLS", size=8.5, color=P["violet"])
    d.arrow(19.1, 22.5, 29.4, 25, color=P["orange"], style="<|-|>")
    d.text(23.8, 21.6, "MQTT", size=8.5, color=P["orange"])

    # browser <-> AWS / backend
    d.arrow(81, 36, 64.1, 39.5, color=P["accent"], style="<|-|>")
    d.text(75.2, 39.6, "WSS", size=8.5, color=P["accent"])
    d.arrow(79.4, 9.5, 72.1, 9.5, color=P["violet"], style="<|-|>")
    d.text(75.8, 11.1, "HTTPS", size=8.5, color=P["violet"])
    d.arrow(70.6, 30, 81, 15.5, color=P["dim"], lw=1.4, ls="--")
    d.text(77.6, 25.6, "재생", size=8.5, color=P["dim"])

    # backend <-> IoT Core
    d.arrow(39, 15.6, 39, 22.4, color=P["orange"], style="<|-|>")
    d.text(40, 17.4, "명령 publish · 규칙", size=8.5, color=P["orange"],
           ha="left")


diagram("25-architecture", draw, w=14, h=8.8, ymax=63)
