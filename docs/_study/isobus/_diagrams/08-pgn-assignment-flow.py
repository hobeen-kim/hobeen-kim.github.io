"""CH08 §8 새 메시지의 PDU 형식·PF 구간 고르기 — Part 3 5.9 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    def node(x, y, w, h, label, kind):
        fc = {"start": P["chip"], "q": P["purple"], "ans": P["blue"],
              "prop": P["brown"], "zone": P["green"]}[kind]
        d.box(x, y, w, h, fc, ec=P["accent"] if kind == "start" else None)
        d.text(x + w / 2, y + h / 2, label, size=8.8)

    def lab(x, y, s, ha="center"):
        d.text(x, y, s, size=8.2, color=P["dim"], ha=ha)

    node(36, 59, 28, 5, "새 parameter group", "start")
    node(30, 48, 40, 6.4, "일반적 관심사인가?\n(제조사 독점 정보가 아닌가)", "q")
    node(2, 48, 22, 6.4, "목적지를 정해\n보내야 하나?", "q")
    node(2, 37, 22, 6.4, "Proprietary A·A2\nPF 239, PS = DA", "prop")
    node(2, 26, 22, 6.4, "Proprietary B\nPF 255, GE 자유", "prop")
    node(30, 37, 40, 6.4, "여러 CF 중 특정 CF를\n직접 제어(명령)하나?", "q")
    node(74, 37, 21, 6.4, "PDU1\nPS = DA", "ans")
    node(74, 26, 21, 6.4, "PDU2\nPS = GE", "ans")
    node(30, 15, 40, 6.4, "주기가 100 ms 이하인가?", "q")
    node(4, 1, 44, 7, "앞쪽 구간: PF 0 / PF 240·GE 0부터 증가\nmulti-packet 불가", "zone")
    node(52, 1, 46, 7, "뒤쪽 구간: PF 238 / PF 254·GE 255부터 감소\nmulti-packet 허용", "zone")

    d.arrow(50, 59, 50, 54.4)
    d.arrow(30, 51.2, 24, 51.2, color=P["orange"])
    lab(27, 53, "아니오")
    d.arrow(13, 48, 13, 43.4)
    lab(14.2, 45.7, "예", ha="left")
    d.ax.plot([2, 0.8, 0.8], [51.2, 51.2, 29.2], color=P["dim"], lw=1.6)
    d.arrow(0.8, 29.2, 2, 29.2, color=P["dim"])
    lab(2.2, 45.7, "아니오", ha="left")

    d.arrow(50, 48, 50, 43.4)
    lab(51.2, 45.7, "예", ha="left")
    d.arrow(70, 40.2, 74, 40.2)
    lab(72, 42, "예")
    d.ax.plot([70, 72, 72], [38.2, 38.2, 29.2], color=P["accent"], lw=1.8)
    d.arrow(72, 29.2, 74, 29.2)
    lab(72.8, 34, "아니오", ha="left")

    # PDU1·PDU2 -> 주기 질문
    d.ax.plot([95, 97.5, 97.5], [40.2, 40.2, 18.2], color=P["accent"], lw=1.8)
    d.ax.plot([95, 97.5], [29.2, 29.2], color=P["accent"], lw=1.8)
    d.arrow(97.5, 18.2, 70, 18.2)

    d.arrow(40, 15, 30, 8)
    lab(33, 12.5, "예")
    d.arrow(60, 15, 72, 8)
    lab(68.5, 12.5, "아니오")


diagram("08-pgn-assignment-flow", draw, w=11.5, h=6.6, xmax=100, ymax=66)
