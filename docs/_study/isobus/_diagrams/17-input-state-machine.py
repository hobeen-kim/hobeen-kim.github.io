"""CH17 §9 운전자 입력 상태 기계: Navigating / Data input 천이 (ISO 11783-6 4.6.17 Table 5) (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 상태 노드
    d.box(6, 22, 26, 12, P["blue"], ec=P["accent"], lw=2.0)
    d.text(19, 28, "Navigating", size=13, weight="bold")
    d.box(68, 22, 26, 12, P["green"], ec=P["accent"], lw=2.0)
    d.text(81, 28, "Data input", size=13, weight="bold")

    # Navigating -> Data input
    d.arrow(32, 31, 68, 31, color=P["accent"], lw=2.0)
    d.text(50, 35.0, "운전자가 입력용으로 열기", size=9, color=P["accent"])
    d.text(50, 32.9, "Select Input Object (Byte 4 = 00)", size=9, color=P["accent"])

    # Data input -> Navigating
    d.arrow(68, 25, 32, 25, color=P["orange"], lw=2.0)
    d.text(50, 23.1, "ENTER: VT Change Numeric/String Value", size=8.8, color=P["orange"])
    d.text(50, 21.2, "ESC: VT ESC message 또는 ESC response", size=8.8, color=P["orange"])
    d.text(50, 19.3, "Change Active Mask, Select Active WS (VT ESC 먼저)", size=8.8, color=P["orange"])
    d.text(50, 17.4, "부모 Container 숨김, Pool 갱신, Pointer 변경 (VT ESC)", size=8.8, color=P["orange"])

    # Navigating 자기 천이
    d.arrow(13, 34, 25, 34, color=P["violet"], rad=-1.1, lw=1.6)
    d.box(2, 41.5, 36, 13, P["chip"], ec=P["edge"], lw=1.0)
    d.text(20, 51.6, "그대로 Navigating", size=9, weight="bold", color=P["violet"])
    d.text(20, 48.9, "포커스 이동 -> VT Select Input Object", size=8.5)
    d.text(20, 46.8, "Select Input Object (FF) -> 응답", size=8.5)
    d.text(20, 44.7, "Button 활성화 -> Button Activation", size=8.5)
    d.text(20, 42.6, "ESC command -> 오류 응답 (열린 입력 없음)", size=8.5)

    # Data input 자기 천이
    d.arrow(75, 34, 87, 34, color=P["violet"], rad=-1.1, lw=1.6)
    d.box(61, 41.5, 37, 13, P["chip"], ec=P["edge"], lw=1.0)
    d.text(79.5, 51.6, "그대로 Data input", size=9, weight="bold", color=P["violet"])
    d.text(79.5, 48.9, "포커스 대상 값·속성·목록 변경 -> 응답", size=8.5)
    d.text(79.5, 46.8, "포커스 대상 Disable -> 오류 (입력 중)", size=8.5)
    d.text(79.5, 44.7, "다른 오브젝트 Select -> 오류 (입력 중)", size=8.5)

    # 진입(리셋)
    d.arrow(19, 9.5, 19, 22, color=P["dim"], lw=1.6)
    d.text(19, 7.6, "새 active Data Mask 선택", size=8.8, color=P["dim"])
    d.text(19, 5.6, "-> Navigating으로 리셋", size=8.8, color=P["dim"])


diagram("17-input-state-machine", draw, w=14, h=7.6, xmax=100, ymax=56)
