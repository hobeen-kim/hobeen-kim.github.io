"""CH03 주소 클레임 — NAME이 주소에 묶이는 과정 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    steps = [
        ("NAME 준비", "제조사·기능·시리얼로\n64비트 NAME 구성", P["blue"]),
        ("희망 주소 클레임", "NULL(0xFE)에서 출발해\n원하는 주소를 브로드캐스트", P["gray"]),
        ("충돌 중재", "같은 주소를 원하면\nNAME 값이 작은 쪽이 이긴다", P["brown"]),
        ("주소 확정", "이긴 CF가 주소를 점유\n진 CF는 다른 주소 재시도", P["green"]),
    ]

    for i, (title, body, fc) in enumerate(steps):
        x = 3 + i * 24.5
        d.box(x, 16, 21, 16, fc)
        d.text(x + 10.5, 28.2, title, size=10.5, weight="bold")
        d.text(x + 10.5, 21.6, body, size=8.2, color=P["dim"])
        if i < len(steps) - 1:
            d.arrow(x + 21, 24, x + 24.5, 24, color=P["accent"], lw=1.6)

    d.box(3, 3, 91.5, 9, P["chip"])
    d.text(48.7, 9.2, "라이브러리가 전 과정을 자동 처리한다", size=10,
           weight="bold", color=P["accent"])
    d.text(48.7, 5.4, "애플리케이션은 NAME만 채워 넣고, 주소가 바뀌어도 "
                      "ControlFunction 포인터를 그대로 쓴다",
           size=8.4, color=P["dim"])

    d.arrow(48.7, 16, 48.7, 12.4, color=P["accent"], lw=1.4)


diagram("03-address-claiming", draw, w=11.5, h=4.2, ymax=35)
