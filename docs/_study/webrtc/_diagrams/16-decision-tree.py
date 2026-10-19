"""CH16 §4 AWS 관리형 WebRTC 서비스 선택 의사결정 트리 (light/dark PNG)."""
from matplotlib.patches import FancyBboxPatch

from _common import diagram


def draw(d):
    P = d.P

    def q(cx, cy, label, w=22, h=7):
        d.box(cx - w / 2, cy - h / 2, w, h, P["chip"], ec=P["accent"], lw=1.4)
        d.text(cx, cy, label, size=9)

    def leaf(cx, cy, label, fc, w=19, h=7.5, ls_dashed=False):
        if ls_dashed:
            d.ax.add_patch(FancyBboxPatch(
                (cx - w / 2, cy - h / 2), w, h,
                boxstyle="round,pad=0.02,rounding_size=0.6",
                linewidth=1.3, edgecolor=P["edge"], facecolor=fc,
                linestyle=(0, (4, 3))))
        else:
            d.box(cx - w / 2, cy - h / 2, w, h, fc)
        d.text(cx, cy, label, size=9, weight="bold")

    def edge(x1, y1, x2, y2, label, lx=None, ly=None, ha="center"):
        d.arrow(x1, y1, x2, y2, color=P["edge"], lw=1.4)
        d.text(lx if lx is not None else (x1 + x2) / 2,
               ly if ly is not None else (y1 + y2) / 2 + 1.2,
               label, size=8.5, color=P["orange"], ha=ha)

    # 루트
    q(50, 55, "송출원이 디바이스인가?\n(카메라·로봇·농기계)", w=26)
    # 2단
    q(27, 41, "채널당 동시 시청자가\n소수인가? (기본 10명)", w=25)
    q(75, 41, "모두가 송출하는\n다자 회의인가?", w=22)
    edge(42, 51.5, 31, 44.5, "예", lx=34.5, ly=49)
    edge(58, 51.5, 71, 44.5, "아니오", lx=67.5, ly=49)

    # 3단 (왼쪽)
    q(13, 27, "클라우드 녹화가\n필요한가?", w=20)
    leaf(41, 27, "IVS Real-Time\n(WHIP 송출)", P["brown"], w=19)
    edge(22, 37.5, 15, 30.5, "예", lx=16, ly=35)
    edge(32, 37.5, 39, 30.8, "아니오", lx=39.5, ly=35)

    # 3단 (오른쪽)
    leaf(66, 27, "Chime SDK\n(SFU 회의)", P["purple"], w=17)
    leaf(88, 27, "IVS Real-Time\n(소수 호스트 → 다수)", P["brown"], w=20)
    edge(72, 37.5, 67.5, 30.8, "예", lx=67.5, ly=35)
    edge(79, 37.5, 86, 30.8, "아니오", lx=86.5, ly=35)

    # 4단 (KVS)
    leaf(8, 11, "KVS WebRTC\n(P2P)", P["green"], w=15)
    leaf(27, 11, "KVS P2P + PutMedia\n또는 저장 세션", P["green"], w=19)
    edge(10, 23.5, 8.5, 14.8, "아니오", lx=5.5, ly=19.5)
    edge(16, 23.5, 25, 14.8, "예", lx=23, ly=19.5)

    # 공통 탈출구
    leaf(66, 9, "직접 구축\n(coturn + SFU)", P["gray"], w=19, h=7.5,
         ls_dashed=True)
    for sx, sy in [(41, 23.2), (66, 23.2), (88, 23.2)]:
        d.arrow(sx, sy, 66 + (sx - 66) * 0.25, 12.8, color=P["edge"], lw=1.1,
                ls="--")
    d.text(79, 15.5, "한도·망 제약·제어권\n요구가 넘칠 때", size=8,
           color=P["dim"], ha="left")


diagram("16-decision-tree", draw, w=13, h=7, ymax=60)
