"""CH56 §1 FMIS와 MICS(TC) 사이 태스크 파일 세트 왕복 (light/dark PNG)."""
from _common import diagram


def lines(d, x, y, items, size=8.8, gap=2.6, color=None):
    for i, s in enumerate(items):
        d.text(x, y - i * gap, s, size=size, ha="left", color=color)


def draw(d):
    P = d.P
    # FMIS (office)
    d.box(2, 10, 21, 26, P["blue"])
    d.text(12.5, 30.5, "FMIS", size=13, weight="bold")
    d.text(12.5, 26.5, "농장 관리 소프트웨어", size=9)
    d.text(12.5, 23.8, "(사무실)", size=8.5, color=P["dim"])
    d.text(12.5, 18.0, "계획 작성", size=9)
    d.text(12.5, 15.4, "결과 분석", size=9)

    # MICS (tractor)
    d.box(77, 10, 21, 26, P["green"])
    d.text(87.5, 30.5, "MICS", size=13, weight="bold")
    d.text(87.5, 26.5, "TC가 든 차량 쪽 시스템", size=9)
    d.text(87.5, 23.8, "(트랙터)", size=8.5, color=P["dim"])
    d.text(87.5, 18.0, "처방대로 작업", size=9)
    d.text(87.5, 15.4, "결과 기록", size=9)

    # outbound file set
    d.box(29, 32.5, 42, 13.8, P["chip"])
    d.text(50, 44.0, "TASKDATA 파일 세트 (계획)", size=9.5, weight="bold")
    lines(d, 31.5, 41.0, ['DataTransferOrigin = "1"', 'TSK G = "1" (planned)',
                          "TASKDATA.XML + GRD00001.BIN"])
    d.arrow(23, 29.6, 77, 29.6)

    # inbound file set
    d.box(29, 0.8, 42, 17.0, P["chip"])
    d.text(50, 15.6, "TASKDATA 파일 세트 (결과)", size=9.5, weight="bold")
    lines(d, 31.5, 12.4, ['DataTransferOrigin = "2"', 'TSK G = "4" (completed)',
                          "+ DVC, TIM, DAN, TCC",
                          "+ TLG00001.XML, TLG00001.BIN"])
    d.arrow(77, 20.6, 23, 20.6)

    d.text(50, 25.1, "이동식 매체(예: USB 메모리) 또는 제조사 고유 전송 수단", size=8.5,
           color=P["orange"])


diagram("56-fmis-tc-roundtrip", draw, w=12, h=5.6, xmax=100, ymax=47)
