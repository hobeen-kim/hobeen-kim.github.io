"""CH07 §4 시간제한 TURN credential(REST API 패턴) 발급·검증 흐름 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 클라이언트
    d.box(2, 18, 20, 12, P["blue"])
    d.text(12, 24, "브라우저 /\n디바이스", size=10)

    # 백엔드
    d.box(40, 32, 22, 12, P["green"])
    d.text(51, 38, "백엔드 API\n(secret 보관)", size=10)

    # coturn
    d.box(40, 4, 22, 12, P["purple"])
    d.text(51, 10, "coturn\n(같은 secret)", size=10)

    # secret 공유
    d.ax.plot([51, 51], [16, 32], color=P["edge"], ls=(0, (4, 3)), lw=1.2,
              zorder=1)
    d.text(52.5, 24, "static-auth-secret\n(사전 공유)", size=8, color=P["dim"],
           ha="left")

    # 1. 요청
    d.arrow(22, 28, 40, 38.5, color=P["accent"])
    d.text(25, 36, "① GET /turn-credentials\n(앱 인증 토큰)", size=8,
           color=P["accent"], ha="left")
    # 2. 응답
    d.arrow(40, 34.5, 22, 25.5, color=P["orange"], ls="--")
    d.text(31.5, 27.5, "②", size=8.5, color=P["orange"])

    # 응답 내용 칩
    d.box(68, 32, 30, 12, P["chip"], ec=P["orange"], lw=1.0)
    d.text(70, 38, "username = 1792414800:robot-17\n"
           "credential = base64(\n"
           "    HMAC-SHA1(secret, username))\n"
           "ttl = 3600", size=8, ha="left", color=P["orange"])
    d.arrow(68, 38, 62, 38, color=P["orange"], style="-", lw=1.0)

    # 3. Allocate
    d.arrow(22, 20, 40, 10, color=P["violet"])
    d.text(24, 11, "③ Allocate\nUSERNAME + MESSAGE-INTEGRITY", size=8,
           color=P["violet"], ha="left")

    # 4. 검증
    d.box(68, 4, 30, 12, P["chip"], ec=P["violet"], lw=1.0)
    d.text(70, 10, "④ HMAC 재계산해 비교\n"
           "username 앞 timestamp가\n"
           "현재보다 과거면 거부", size=8, ha="left", color=P["violet"])
    d.arrow(68, 10, 62, 10, color=P["violet"], style="-", lw=1.0)

diagram("07-credential-flow", draw, w=12, h=5.4, ymax=48)
