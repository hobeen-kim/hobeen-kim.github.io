"""CH29 버전 적응 예: v5로 설계한 ECU가 v4 VT에 맞춰 동작 범위를 낮춘다 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P
    boxes = [
        (2, "VT\nVersion 4 지원", "blue"),
        (39, "ECU\nVersion 5 설계", "green"),
        (76, "동작\nVersion 4 기능 범위", "purple"),
    ]
    for x, label, color in boxes:
        d.box(x, 3, 22, 11, P[color], ec=P["accent"] if color == "purple" else None)
        d.text(x + 11, 8.5, label, size=10.5)

    d.arrow(24, 8.5, 39, 8.5, color=P["accent"])
    d.text(31.5, 19.0, "Get Memory\nresponse로\n버전 4 보고", size=9, color=P["accent"])
    d.arrow(61, 8.5, 76, 8.5, color=P["accent"])
    d.text(68.5, 19.0, "풀·커맨드를\nv4에 맞게\n조정", size=9, color=P["accent"])


diagram("29-version-adaptation", draw, w=11, h=3.0, xmax=100, ymax=26)
