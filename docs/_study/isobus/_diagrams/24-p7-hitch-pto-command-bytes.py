"""CH24 Hitch and PTO commands: 제어하지 않는 필드를 FF로 채운 프레임과 0으로 초기화한 프레임 비교 (light/dark PNG)."""
from _common import diagram

NAMES = ["Byte 1", "Byte 2", "Byte 3", "Byte 4", "Byte 5", "Byte 6", "Byte 7", "Byte 8"]
FIELDS = [(0, 0, "전방 히치"), (1, 1, "후방 히치"), (2, 3, "전방 PTO 회전수"),
          (4, 5, "후방 PTO 회전수"), (6, 6, "PTO 체결"), (7, 7, "모드·이코노미")]

GOOD = ["FF", "A0", "FF", "FF", "FF", "FF", "FF", "FF"]
BAD = ["00", "A0", "00", "00", "00", "00", "00", "00"]

GOOD_NOTES = [(0, 0, "요청 없음"), (1, 1, "64 %"), (2, 3, "요청 없음"), (4, 5, "요청 없음"),
              (6, 6, "상관없음"), (7, 7, "상관없음")]
BAD_NOTES = [(0, 0, "0 %: 끝까지\n내려라", True), (1, 1, "64 %", False),
             (2, 3, "0 r/min 설정", False), (4, 5, "0 r/min 설정", False),
             (6, 6, "전·후방\nPTO 분리", True), (7, 7, "540 모드,\n이코노미 해제", False)]


def draw(d):
    P = d.P
    x0, w, gap = 17, 9.4, 0.9
    xs = [x0 + i * (w + gap) for i in range(8)]
    yg, yb, h = 33, 12, 6.5

    for i, name in enumerate(NAMES):
        d.text(xs[i] + w / 2, 47.5, name, size=8.6, color=P["dim"])
    for a, b, label in FIELDS:
        d.text((xs[a] + xs[b] + w) / 2, 44.6, label, size=8.4, weight="bold")

    def row(y, vals, fill, title):
        for i, v in enumerate(vals):
            d.box(xs[i], y, w, h, fill(i), lw=1.1, r=0.005)
            d.text(xs[i] + w / 2, y + h / 2, v, size=12, weight="bold")
        d.text(1.5, y + h / 2, title, size=10, weight="bold", ha="left")

    row(yg, GOOD, lambda i: P["blue"] if i == 1 else P["green"], "FF로 채움")
    row(yb, BAD, lambda i: P["blue"] if i == 1 else (P["brown"] if i in (0, 6) else P["gray"]),
        "0으로 초기화")

    for a, b, note in GOOD_NOTES:
        d.text((xs[a] + xs[b] + w) / 2, yg - 2.4, note, size=8.4, color=P["accent"])
    for a, b, note, danger in BAD_NOTES:
        d.text((xs[a] + xs[b] + w) / 2, yb - 3.4, note, size=8.4,
               color=P["orange"] if danger else P["dim"],
               weight="bold" if danger else "normal")


diagram("24-p7-hitch-pto-command-bytes", draw, w=12, h=5.2, xmax=100, ymax=50)
