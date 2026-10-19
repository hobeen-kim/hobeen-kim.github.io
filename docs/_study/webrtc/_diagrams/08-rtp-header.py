"""CH08 §1 RTP 고정 헤더 비트 레이아웃 (RFC 3550) — (light/dark PNG)."""
from _common import diagram

X0, X1 = 14, 94
BW = (X1 - X0) / 32
RH = 5.6


def field(d, row_y, b0, b1, label, fc, size=9.5, sub=None, ls="-"):
    P = d.P
    x = X0 + BW * b0
    w = BW * (b1 - b0)
    d.box(x, row_y, w, RH, fc, lw=1.2, r=0.01)
    if ls != "-":
        d.ax.plot([x, x + w], [row_y, row_y], color=P["bg"], lw=1.6, zorder=3)
    if sub:
        d.text(x + w / 2, row_y + RH * 0.64, label, size=size, weight="bold")
        d.text(x + w / 2, row_y + RH * 0.28, sub, size=7.6, color=P["dim"])
    else:
        d.text(x + w / 2, row_y + RH / 2, label, size=size, weight="bold")


def draw(d):
    P = d.P

    # 비트 눈금
    for b in range(32):
        d.text(X0 + BW * (b + 0.5), 49.2, str(b % 10), size=7, color=P["dim"])
    for b in (0, 10, 20, 30):
        d.text(X0 + BW * (b + 0.5), 51.4, str(b // 10), size=7, color=P["dim"])

    rows = [42, 35.5, 29, 21, 14.5, 8, 1.5]

    # 1행: V P X CC M PT Sequence Number
    y = rows[0]
    field(d, y, 0, 2, "V=2", P["blue"], size=8.5)
    field(d, y, 2, 3, "P", P["blue"], size=8.5)
    field(d, y, 3, 4, "X", P["blue"], size=8.5)
    field(d, y, 4, 8, "CC", P["blue"], sub="CSRC 개수")
    field(d, y, 8, 9, "M", P["purple"], size=8.5)
    field(d, y, 9, 16, "PT", P["purple"], sub="페이로드 타입")
    field(d, y, 16, 32, "Sequence Number", P["green"], sub="16비트 · 패킷마다 +1")

    # 2행, 3행
    field(d, rows[1], 0, 32, "Timestamp", P["brown"],
          sub="32비트 · 미디어 클럭(비디오 90kHz, Opus 48kHz) · 같은 프레임의 패킷은 같은 값")
    field(d, rows[2], 0, 32, "SSRC", P["gray"],
          sub="32비트 · 동기화 소스(스트림) 식별자 · 무작위 생성")

    # 선택 영역
    field(d, rows[3], 0, 32, "CSRC 목록", P["chip"],
          sub="CC개 × 32비트 (믹서가 합친 원본 소스, WebRTC P2P에서는 보통 0개)")
    field(d, rows[4], 0, 16, "0xBEDE", P["chip"], sub="one-byte 확장 표식")
    field(d, rows[4], 16, 32, "length", P["chip"], sub="확장 길이(32비트 단위)")
    field(d, rows[5], 0, 32, "확장 요소들", P["chip"],
          sub="ID(4) · L(4) · 데이터 — mid, abs-send-time, transport-cc 등 (a=extmap)")
    field(d, rows[6], 0, 32, "페이로드", P["green"],
          sub="코덱 데이터 (H.264 NAL·FU-A, Opus 프레임) — SRTP가 이 부분을 암호화")

    # 왼쪽 그룹 라벨
    def bracket(y0, y1, label, color):
        x = X0 - 1.6
        d.ax.plot([x, x], [y0, y1], color=color, lw=1.6)
        d.ax.plot([x, x + 0.8], [y0, y0], color=color, lw=1.6)
        d.ax.plot([x, x + 0.8], [y1, y1], color=color, lw=1.6)
        d.text(x - 1.0, (y0 + y1) / 2, label, size=8.6, color=color,
               ha="right", weight="bold")

    bracket(rows[2], rows[0] + RH, "고정 헤더\n12바이트", P["accent"])
    bracket(rows[3], rows[3] + RH, "선택\n(CC>0)", P["dim"])
    bracket(rows[5], rows[4] + RH, "선택\n(X=1)", P["dim"])
    bracket(rows[6], rows[6] + RH, "본문", P["orange"])


diagram("08-rtp-header", draw, w=13, h=6.8, ymax=53)
