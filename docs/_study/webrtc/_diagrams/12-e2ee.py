"""CH12 §6 E2EE 경로 — 프레임 암호화(SFrame)와 홉 단위 SRTP의 이중 구조 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 송신 측
    d.box(2, 30, 60, 17, P["gray"])
    d.text(4, 44.8, "송신 측 (브라우저 / 디바이스)", size=9.5, weight="bold", ha="left")
    send = [(4, 11, "인코더", P["blue"]),
            (18, 14, "Encoded Transform\n(SFrame 암호화)", P["green"]),
            (35, 11, "RTP 패킷화", P["blue"]),
            (49, 11, "SRTP 암호화\n(홉 키)", P["brown"])]
    for x, w, lbl, fc in send:
        d.box(x, 33, w, 8, fc)
        d.text(x + w / 2, 37, lbl, size=8.4)
    for x1, x2 in [(15, 18), (32, 35), (46, 49)]:
        d.arrow(x1, 37, x2, 37, color=P["accent"])

    # 수신 측
    d.box(2, 3, 60, 17, P["gray"])
    d.text(4, 17.8, "수신 측 (브라우저)", size=9.5, weight="bold", ha="left")
    recv = [(49, 11, "SRTP 복호\n(홉 키)", P["brown"]),
            (35, 11, "역패킷화", P["blue"]),
            (18, 14, "Encoded Transform\n(SFrame 복호)", P["green"]),
            (4, 11, "디코더", P["blue"])]
    for x, w, lbl, fc in recv:
        d.box(x, 6, w, 8, fc)
        d.text(x + w / 2, 10, lbl, size=8.4)
    for x1, x2 in [(49, 46), (35, 32), (18, 15)]:
        d.arrow(x1, 10, x2, 10, color=P["accent"])

    # SFU
    d.box(70, 19, 27, 13, P["purple"], ec=P["accent"], lw=1.6)
    d.text(83.5, 29.2, "SFU", size=10.5, weight="bold")
    d.text(83.5, 24.2, "SRTP 복호 → 재암호화\n읽는 것: RTP 헤더·확장\n페이로드: SFrame 암호문",
           size=8, color=P["dim"])
    d.arrow(60, 37, 76, 32, color=P["accent"], rad=-0.15)
    d.arrow(76, 19, 60, 10, color=P["accent"], rad=-0.15)

    # E2E 키
    d.arrow(25, 33, 25, 14, color=P["violet"], lw=1.4, ls="--", style="<|-|>")
    d.text(26.5, 23.5, "같은 E2E 키\n(SFU는 모름)", size=8, color=P["violet"], ha="left")


diagram("12-e2ee", draw, w=13, h=6.2, ymax=48)
