"""CH11 §4 TP.DT 메시지(8 byte) 바이트 레이아웃 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P
    n = 8
    x0, gap = 2, 0.4
    w = 3.2
    y, h = 8, 5

    x = x0
    for i in range(n):
        if i == 0:
            color = P["blue"]
            inner = "Seq No\n(1~255)"
        else:
            color = P["gray"]
            inner = f"Payload\nbyte {i}"
        d.box(x, y, w, h, color)
        d.text(x + w / 2, y + h + 1.2, f"Byte {i + 1}", size=9.5, weight="bold")
        d.text(x + w / 2, y + h / 2, inner, size=8.5)
        x += w + gap
    x_end = x - gap
    last_x = x - gap - w  # byte 8 박스 시작 x

    # Byte 2~8 구간 표시 (묶음 괄호 + 설명)
    x2 = x0 + (w + gap)  # byte2 시작
    bracket_y = y - 1.2
    d.arrow(x2, bracket_y, x_end, bracket_y, color=P["dim"], lw=1.2, style="-")
    d.arrow(x2, bracket_y, x2, bracket_y + 0.6, color=P["dim"], lw=1.2, style="-")
    d.arrow(x_end, bracket_y, x_end, bracket_y + 0.6, color=P["dim"], lw=1.2, style="-")
    d.text((x2 + x_end) / 2, bracket_y - 1.4, "페이로드 7바이트", size=9, color=P["dim"])

    # 마지막 패킷 패딩 안내 (byte 8 박스를 가리키는 화살표)
    note_x, note_y = x_end - 1.5, 2.2
    d.text(note_x, note_y, "마지막 패킷의 남는 자리는\n0xFF로 패딩", size=8.5, color=P["orange"], ha="right")
    d.arrow(note_x + 0.3, note_y + 0.7, last_x + w / 2, y - 0.3, color=P["orange"], lw=1.2, rad=-0.2)


diagram("11-tpdt-layout", draw, w=12, h=6, xmax=32, ymax=16)
