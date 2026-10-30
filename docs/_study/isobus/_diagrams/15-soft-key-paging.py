"""CH15 §7 가상 Soft Key 페이지 넘김 예 — 물리 6개·내비게이션 1개 (light/dark PNG)."""
from _common import diagram

ENTRIES = ["K1", "K2", None, "K3", "K4", "K5", "K6", "K7", None, "K8", "K9", None, None]
TRAILING_FROM = 11  # 0-based index where trailing NULLs start

PAGES = [
    ["K1", "K2", None, "K3", "K4"],
    ["K5", "K6", "K7", None, "K8"],
    ["K9", "", "", "", ""],
]


def bracket(d, x1, x2, y, label):
    P = d.P
    d.arrow(x1, y, x2, y, color=P["dim"], lw=1.2, style="-")
    d.arrow(x1, y, x1, y + 0.7, color=P["dim"], lw=1.2, style="-")
    d.arrow(x2, y, x2, y + 0.7, color=P["dim"], lw=1.2, style="-")
    d.text((x1 + x2) / 2, y - 1.9, label, size=8.5, color=P["dim"])


def draw(d):
    P = d.P
    cw, cg, cx0, cy, ch = 6.4, 0.6, 5.0, 41.0, 4.5
    cxs = [cx0 + i * (cw + cg) for i in range(len(ENTRIES))]
    for i, (x, key) in enumerate(zip(cxs, ENTRIES)):
        if key:
            d.box(x, cy, cw, ch, P["blue"])
            d.text(x + cw / 2, cy + ch / 2, key, size=8.5)
        elif i < TRAILING_FROM:
            d.box(x, cy, cw, ch, P["gray"])
            d.text(x + cw / 2, cy + ch / 2, "NULL", size=8)
        else:
            d.box(x, cy, cw, ch, P["chip"])
            d.text(x + cw / 2, cy + ch / 2, "NULL", size=8, color=P["dim"])
        d.text(x + cw / 2, cy + ch + 1.4, str(i + 1), size=7.5, color=P["dim"])

    by = 39.6
    bracket(d, cxs[0], cxs[4] + cw, by, "1쪽")
    bracket(d, cxs[5], cxs[9] + cw, by, "2쪽")
    bracket(d, cxs[10], cxs[10] + cw, by, "3쪽")
    bracket(d, cxs[11], cxs[12] + cw, by, "끝 NULL: 자리 예약 안 함")

    px0s = [12, 43, 74]
    pw, kw, kh = 18, 16, 3.4

    def key_y(i):
        return 3 + (6 - i) * 4.0

    for page_no, (px, keys) in enumerate(zip(px0s, PAGES), start=1):
        d.box(px, 2, pw, 25.4, P["gray"], ec=P["edge"], lw=1.0)
        d.text(px + pw / 2, 29.6, f"{page_no}쪽", size=9.5, weight="bold")
        for slot in range(1, 7):
            x, y = px + 1, key_y(slot)
            if slot == 6:
                d.box(x, y, kw, kh, P["green"], ec=P["accent"])
                d.text(x + kw / 2, y + kh / 2, "다음 그룹(내비게이션)", size=8)
                continue
            key = keys[slot - 1]
            if key:
                d.box(x, y, kw, kh, P["blue"])
                d.text(x + kw / 2, y + kh / 2, key, size=8.5)
            elif key is None:
                d.box(x, y, kw, kh, P["chip"])
                d.text(x + kw / 2, y + kh / 2, "빈 자리(NULL)", size=8, color=P["dim"])
            else:
                d.box(x, y, kw, kh, P["chip"], alpha=0.5)
                d.text(x + kw / 2, y + kh / 2, "미사용", size=8, color=P["dim"])

    for slot in range(1, 7):
        d.text(7.2, key_y(slot) + kh / 2, f"키 {slot}", size=8, color=P["dim"])

    ny = key_y(6) + kh / 2
    for a, b in ((px0s[0], px0s[1]), (px0s[1], px0s[2])):
        d.arrow(a + 1 + kw + 0.3, ny, b - 0.3, ny, color=P["orange"])
        d.text((a + 1 + kw + b) / 2, ny + 1.6, "누름", size=8, color=P["dim"])


diagram("15-soft-key-paging", draw, w=12, h=6.6, xmax=100, ymax=50)
