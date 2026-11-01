"""41장 TC의 역할: FMIS → TC → 작업기 → 기록 → FMIS 순환과 현장 감독 비유 (light/dark PNG)."""
from _common import diagram

W, H = 22, 13


def node(d, x, y, title, sub, analogy, color):
    P = d.P
    d.box(x, y, W, H, P[color])
    d.text(x + W / 2, y + H / 2 + 3.4, title, size=12.5, weight="bold")
    d.text(x + W / 2, y + H / 2 + 0.1, sub, size=9.5)
    d.text(x + W / 2, y + H / 2 - 3.6, analogy, size=9.5, color=P["violet"], weight="bold")


def draw(d):
    P = d.P
    node(d, 2, 27, "FMIS", "농장 관리 소프트웨어", "비유: 농장 사무실", "gray")
    node(d, 39, 27, "TC", "Task Controller", "비유: 현장 감독", "green")
    node(d, 76, 27, "작업기 ECU", "TC-Client", "비유: 일하는 기계", "blue")
    node(d, 39, 2, "작업 로그", "As-Applied", "비유: 작업 일지", "brown")

    d.arrow(24.2, 33.5, 38.8, 33.5)
    d.text(31.5, 38.3, "처방 맵", size=9.5, color=P["accent"], weight="bold")
    d.text(31.5, 36.2, "(Prescription Map)", size=8)
    d.text(31.5, 30.6, "작업 지시서", size=9, color=P["violet"])

    d.arrow(61.2, 36.5, 75.8, 36.5)
    d.text(68.5, 41.6, "설정값 전달", size=9.5, color=P["accent"], weight="bold")
    d.text(68.5, 39.4, "(Setpoint)", size=8.5)

    d.arrow(75.8, 30.5, 61.2, 30.5)
    d.text(68.5, 27.8, "측정값 보고", size=9.5, color=P["accent"], weight="bold")
    d.text(68.5, 25.6, "(Measurement)", size=8.5)

    d.arrow(50, 26.8, 50, 15.2)
    d.text(52, 21, "작업 결과 기록", size=9.5, color=P["accent"], weight="bold", ha="left")

    d.arrow(38.8, 8.5, 13, 26.8, rad=-0.32)
    d.text(13.5, 11.5, "작업 데이터 업로드", size=9.5, color=P["accent"], weight="bold")


diagram("41-tc-role-flow", draw, w=12, h=5.6, xmax=100, ymax=46)
