"""CH15 §12 Working Set Maintenance 끊김 때 VT의 경보 판정 흐름 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P
    cx, qw, qh = 20, 30, 6.0

    def node(y, label, color, w=qw, x=cx, ec=None):
        d.box(x - w / 2, y - qh / 2, w, qh, P[color], ec=ec)
        d.text(x, y, label, size=9)

    node(46.5, "Maintenance 3초 끊김 또는\nInitiating 재수신", "chip", ec=P["accent"])
    node(36.5, "Delete Object Pool 뒤에\n송신이 멈췄나?", "blue")
    node(26.5, "키 off가 감지됐나?", "blue")
    node(16.5, "휘발성 메모리에\n그 WS의 풀이 없나?", "blue")
    node(5.0, "운전자 경보 → 풀 삭제\n→ AUX 할당 제거·VT Status 갱신", "brown", w=34)

    rx, rw = 62, 20
    d.box(rx - rw / 2, 13.5, rw, 26, P["green"], ec=P["accent"])
    d.text(rx, 26.5, "경보 없음", size=10, weight="bold")

    nx, nw = 76, 34
    d.box(nx - nw / 2, 5.0 - qh / 2, nw, qh, P["gray"])
    d.text(nx, 5.0, "이후 Initiating 없는 Maintenance\n→ Acknowledgement NACK", size=9)

    d.arrow(cx, 43.5, cx, 39.5)
    for y_from, y_to in ((33.5, 29.5), (23.5, 19.5), (13.5, 8.0)):
        d.arrow(cx, y_from, cx, y_to)
        d.text(cx + 3.2, (y_from + y_to) / 2, "아니오", size=8, color=P["dim"])
    for y in (36.5, 26.5, 16.5):
        d.arrow(cx + qw / 2, y, rx - rw / 2, y)
        d.text((cx + qw / 2 + rx - rw / 2) / 2, y + 1.3, "예", size=8, color=P["dim"])
    d.arrow(cx + 17, 5.0, nx - nw / 2, 5.0, color=P["orange"], ls="--")


diagram("15-shutdown-alert", draw, w=11, h=6.2, xmax=95, ymax=51)
