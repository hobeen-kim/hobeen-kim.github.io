"""CH03 NAME 64비트 — 9개 구성요소와 비트 폭 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    d.text(3, 47.5, "NAME — 64비트 (구성요소 9개 + 예약 1비트)", size=11,
           weight="bold", color=P["accent"], ha="left")

    cards = [
        ("Identity Number", "21 bit", "보통 일련번호\n같은 NAME끼리 구분", P["blue"]),
        ("Manufacturer Code", "11 bit", "누가 만들었나\nisobus.net 등록 목록", P["blue"]),
        ("ECU Instance", "3 bit", "비슷한 CF 사이의\nNAME 서열", P["green"]),
        ("Function", "8 bit", "이 CF가 무슨 일을 하나\nISO 11783 정의 목록", P["green"]),
        ("Function Instance", "5 bit", "기능의 인스턴스 번호\n(VT 번호와 유사)", P["green"]),
        ("Device Class", "7 bit", "장치 종류\nJ1939의 vehicle system", P["brown"]),
        ("Device Class Instance", "4 bit", "같은 장치 종류 사이의\n서열", P["brown"]),
        ("Industry Group", "3 bit", "산업 분류\n예: 농업", P["purple"]),
        ("Arbitrary Address\nCapable", "1 bit", "주소 중재를\n지원하는가", P["purple"]),
    ]

    for i, (name, bits, sub, fc) in enumerate(cards):
        col = i % 3
        row = i // 3
        x = 3 + col * 32
        y = 31 - row * 15
        d.box(x, y, 30, 13, fc)
        d.text(x + 15, y + 10, name, size=10, weight="bold")
        d.text(x + 15, y + 6.4, bits, size=8.6, color=P["accent"], weight="bold")
        d.text(x + 15, y + 2.9, sub, size=8, color=P["dim"])


diagram("03-name-fields", draw, w=12, h=6.2, ymax=50)
