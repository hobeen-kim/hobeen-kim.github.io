"""CH25 §4 녹화 방식 세 가지 — 저장 모드 / 로컬 링 버퍼 / Producer SDK 병행 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    def panel(x0, title):
        d.box(x0, 1.5, 31.5, 38, P["gray"], lw=1.2)
        d.text(x0 + 1.2, 37.4, title, size=9.5, weight="bold", ha="left",
               color=P["dim"])

    def chip(x, y, w, h, s, fc=None, hl=False):
        d.box(x, y, w, h, fc or P["chip"],
              ec=P["accent"] if hl else P["edge"], lw=1.5 if hl else 1.0)
        d.text(x + w / 2, y + h / 2, s, size=8.5)

    # A. storage mode
    a = 1
    panel(a, "A. 저장 모드 (JoinStorageSession)")
    chip(a + 2, 4, 11.5, 6, "농기계\n(MASTER)", P["green"])
    chip(a + 18, 4, 11.5, 6, "뷰어\n(최대 3명)", P["blue"])
    chip(a + 8, 17.5, 15.5, 6, "storage session\n(AWS)", hl=True)
    chip(a + 8, 28, 15.5, 5.5, "KVS Video Stream\n(HLS · DASH)")
    d.arrow(a + 8, 10.1, a + 11, 17.4, color=P["orange"])
    d.text(a + 6.2, 14.2, "relay", size=8, color=P["orange"])
    d.arrow(a + 20.5, 17.4, a + 23.5, 10.1, color=P["orange"])
    d.text(a + 25.6, 14.2, "relay", size=8, color=P["orange"])
    d.arrow(a + 15.75, 23.6, a + 15.75, 27.9, color=P["accent"])
    d.text(a + 15.75, 7, "P2P 없음", size=8.5, color=P["orange"],
           weight="bold")

    # B. local ring buffer + incident upload
    b = 34.25
    panel(b, "B. 로컬 링 버퍼 + 사건 업로드")
    chip(b + 2, 4, 11.5, 6, "농기계\n(MASTER)", P["green"])
    chip(b + 18, 4, 11.5, 6, "뷰어\n(1~3명)", P["blue"])
    chip(b + 2, 17.5, 11.5, 6, "링 버퍼\n(eMMC · SSD)")
    chip(b + 18, 28, 11.5, 5.5, "S3\n(사건 구간)")
    d.arrow(b + 13.6, 7, b + 17.9, 7, color=P["accent"], style="<|-|>", lw=2.2)
    d.text(b + 15.75, 8.9, "P2P", size=8.5, color=P["accent"], weight="bold")
    d.arrow(b + 7.75, 10.1, b + 7.75, 17.4, color=P["edge"], lw=1.4)
    d.text(b + 8.6, 13.8, "고화질 별도 인코딩", size=8, color=P["dim"], ha="left")
    d.arrow(b + 9, 23.6, b + 18, 30.5, color=P["orange"], ls="--")
    d.text(b + 7.5, 29.6, "사건 시\n업로드", size=8, color=P["orange"])

    # C. Producer SDK in parallel
    c = 67.5
    panel(c, "C. Producer SDK 병행")
    chip(c + 2, 4, 11.5, 6, "농기계\n(MASTER)", P["green"])
    chip(c + 18, 4, 11.5, 6, "뷰어\n(1~3명)", P["blue"])
    chip(c + 14, 28, 15.5, 5.5, "KVS Video Stream\n(HLS · DASH)")
    d.arrow(c + 13.6, 7, c + 17.9, 7, color=P["accent"], style="<|-|>", lw=2.2)
    d.text(c + 15.75, 8.9, "P2P", size=8.5, color=P["accent"], weight="bold")
    d.arrow(c + 7.75, 10.1, c + 15, 27.9, color=P["orange"], lw=2.0)
    d.text(c + 6.4, 21.5, "운용 중\n상시 PutMedia", size=8, color=P["orange"])


diagram("25-recording-options", draw, w=14, h=5.8, ymax=41)
