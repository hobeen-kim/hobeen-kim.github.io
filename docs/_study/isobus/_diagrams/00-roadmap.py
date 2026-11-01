"""README 학습 로드맵: 57장을 9개 묶음의 흐름으로 (light/dark PNG)."""
from matplotlib.patches import Patch

from _common import diagram

BW, BH = 22, 12


def group(d, x, y, title, chapters, keywords, fc):
    P = d.P
    d.box(x, y, BW, BH, fc)
    cx = x + BW / 2
    d.text(cx, y + BH - 3.2, title, size=10.5, weight="bold")
    d.text(cx, y + BH / 2 - 0.4, chapters, size=10, color=P["accent"], weight="bold")
    d.text(cx, y + 2.6, keywords, size=8.8, color=P["dim"])


def draw(d):
    P = d.P
    base, common, feature, practice = P["blue"], P["green"], P["purple"], P["brown"]

    top = 42
    xs = [1.5, 26.5, 51.5, 76.5]
    group(d, xs[0], top, "1. 통신과 CAN 기초", "1~7장", "신호, 프레임, 중재, 에러", base)
    group(d, xs[1], top, "2. SAE J1939", "8~17장", "PGN, 주소, 긴 데이터 전송", base)
    group(d, xs[2], top, "3. ISOBUS 개요와 네트워크", "18~21장", "파트 구성, 커넥터, NIU", common)
    group(d, xs[3], top, "4. 트랙터와 작업기 메시지", "22~25장", "TECU, 속도, 히치, PTO", common)
    for a, b in zip(xs, xs[1:]):
        d.arrow(a + BW + 0.3, top + BH / 2, b - 0.3, top + BH / 2)

    mgmt_y = 19
    group(d, xs[3], mgmt_y, "5. 네트워크 관리와 진단", "26~28장", "Working Set, DM1, FMI", common)
    d.arrow(xs[3] + BW / 2, top - 0.3, xs[3] + BW / 2, mgmt_y + BH + 0.3)

    vt_y, tc_y = 27, 5
    group(d, xs[2], vt_y, "6. Virtual Terminal (VT)", "29~40장", "화면, 오브젝트 풀, 명령, AUX", feature)
    group(d, xs[2], tc_y, "7. Task Controller (TC)", "41~50장", "태스크, 프로세스 데이터, DDOP", feature)
    d.arrow(xs[3] - 0.3, mgmt_y + BH / 2 + 2, xs[2] + BW + 0.3, vt_y + BH / 2)
    d.arrow(xs[3] - 0.3, mgmt_y + BH / 2 - 2, xs[2] + BW + 0.3, tc_y + BH / 2)

    fs_y = 16
    group(d, xs[1], fs_y, "8. File Server와 SC", "51~54장", "공용 저장소, 조작 기록·재생", feature)
    d.arrow(xs[2] - 0.3, vt_y + BH / 2, xs[1] + BW + 0.3, fs_y + BH / 2 + 2)
    d.arrow(xs[2] - 0.3, tc_y + BH / 2, xs[1] + BW + 0.3, fs_y + BH / 2 - 2)

    group(d, xs[0], fs_y, "9. 종합 실습", "55~57장", "로그, ISOXML, 바이너리 파일", practice)
    d.arrow(xs[1] - 0.3, fs_y + BH / 2, xs[0] + BW + 0.3, fs_y + BH / 2)

    handles = [
        Patch(facecolor=base, edgecolor=P["edge"], label="바탕 통신(CAN, J1939)"),
        Patch(facecolor=common, edgecolor=P["edge"], label="ISOBUS 공통 규칙"),
        Patch(facecolor=feature, edgecolor=P["edge"], label="ISOBUS 기능"),
        Patch(facecolor=practice, edgecolor=P["edge"], label="실습"),
    ]
    d.legend(handles, loc="lower left", anchor=(0.01, 0.02), fontsize=9)


diagram("00-roadmap", draw, w=13, h=7.3, xmax=100, ymax=56)
