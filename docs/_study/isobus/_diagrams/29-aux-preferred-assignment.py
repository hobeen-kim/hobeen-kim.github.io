"""CH29 AUX Preferred Assignment로 저장해 둔 할당을 복원하는 순서 (light/dark PNG)."""
from _common import diagram

AUX, VT, ECU = 15, 52, 88
TOP = 58


def draw(d):
    P = d.P
    for x, name, col in [(AUX, "AUX Input Unit\n(조이스틱)", P["brown"]),
                         (VT, "VT Server", P["blue"]),
                         (ECU, "작업기 ECU", P["green"])]:
        d.box(x - 10, TOP, 20, 6.6, col)
        d.text(x, TOP + 3.3, name, size=10, weight="bold")
        d.ax.plot([x, x], [3, TOP], color=P["edge"], ls=(0, (4, 3)), lw=1.0, zorder=1)

    def hop(x1, x2, y, label, color=None, ls="-"):
        color = color or P["accent"]
        d.arrow(x1, y, x2, y, color=color, ls=ls, lw=1.6)
        d.text((x1 + x2) / 2, y + 1.3, label, size=8.6, color=color)

    hop(AUX, VT, 52.5, "오브젝트 풀 업로드 (AUX Input 오브젝트 정의)")
    hop(ECU, VT, 47.5, "오브젝트 풀 업로드 (AUX Function 오브젝트 포함)")
    hop(ECU, VT, 42.5, "Preferred Assignment command (저장해 둔 선호 할당 전달)")

    d.box(VT - 17, 34.6, 34, 4.0, P["purple"], lw=1.1)
    d.text(VT, 36.6, "할당 검증 (기능-입력 타입 일치·충돌 확인)", size=8.6)

    hop(VT, AUX, 29.5, "AUX Input Status Enable (입력 상태 전송 활성화)")
    hop(VT, ECU, 24.5, "AUX Assignment command (할당 확정 통지)")

    d.box(4, 16.2, 92, 3.8, P["gray"], lw=1.0)
    d.text(50, 18.1, "매핑 완료: 조이스틱 조작 시 ECU 기능 실행", size=9, color=P["dim"])

    y = 10.0
    d.arrow(AUX, y, ECU, y, color=P["violet"], lw=1.8)
    d.ax.plot([VT], [y], marker="o", ms=5, color=P["violet"], zorder=6)
    d.ax.text((AUX + ECU) / 2, y + 1.9, "AUX Input Type 2 Status (전체 Working Set에 직접 브로드캐스트)",
              fontsize=8.6, color=P["violet"], ha="center", va="center", zorder=6,
              bbox=dict(boxstyle="square,pad=0.15", facecolor=P["bg"], edgecolor="none"))
    d.text(VT + 1.5, y - 2.2, "VT를 거치지 않음", size=8, color=P["dim"], ha="left")


diagram("29-aux-preferred-assignment", draw, w=12.5, h=7.6, xmax=100, ymax=66)
