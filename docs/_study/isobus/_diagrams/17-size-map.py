"""17장 1절: 데이터 크기에 따라 단일 프레임, TP, ETP 중 무엇을 쓰는지 나타낸 띠 (light/dark PNG, 길이는 비율이 아님)."""
from _common import diagram


def draw(d):
    P = d.P
    y, h = 14, 8
    bands = [
        (3, 22, "gray", "CAN 프레임 1개", "0~8 byte", "프레임 1개", "엔진 회전수 같은 값"),
        (25, 58, "blue", "TP (BAM 또는 CMDT)", "9~1,785 byte", "패킷 2~255개", "DM1, 제품 식별 정보"),
        (58, 97, "green", "ETP (1:1 연결만)", "1,786~117,440,505 byte", "패킷 256개 이상", "VT 오브젝트 풀, 펌웨어"),
    ]
    for x0, x1, color, name, size, packets, example in bands:
        d.box(x0, y, x1 - x0, h, P[color])
        d.text((x0 + x1) / 2, y + h / 2 + 1.3, name, size=10.5, weight="bold")
        d.text((x0 + x1) / 2, y + h / 2 - 1.7, size, size=9)
        d.text((x0 + x1) / 2, y + h + 2.6, packets, size=8.8, color=P["dim"])
        d.text((x0 + x1) / 2, y - 3.0, example, size=8.8, color=P["dim"])

    for x, label in ((23.5, "8 | 9"), (58, "1,785 | 1,786")):
        d.ax.plot([x, x], [y - 6.2, y - 5.0], color=P["edge"], lw=1.2)
        d.text(x, y - 7.6, label, size=8.4, color=P["dim"])
    d.arrow(3, 4.0, 97, 4.0, color=P["edge"], lw=1.2)
    d.text(97, 1.8, "데이터 크기", size=8.4, color=P["dim"], ha="right")


diagram("17-size-map", draw, w=12, h=3.4, xmax=100, ymax=28)
