"""CH13 §1 VT 클라이언트 수명주기 — 연결부터 풀 업로드, 런타임까지."""
from _common import diagram


def draw(d):
    P = d.P

    # 1행: 연결 준비
    d.box(2, 30, 19, 9, P["gray"], ec=P["edge"])
    d.text(11.5, 34.5, "Disconnected\ninitialize(true)", size=9.5)

    d.box(25, 30, 22, 9, P["blue"])
    d.text(36, 34.5, "WaitForPartner\nVTStatusMessage", size=9.5)

    d.box(51, 30, 21, 9, P["blue"])
    d.text(61.5, 34.5, "SendWorkingSet\nMasterMessage", size=9.5)

    d.box(76, 30, 22, 9, P["blue"])
    d.text(87, 34.5, "ReadyFor\nObjectPool", size=9.5)

    d.arrow(21, 34.5, 25, 34.5)
    d.arrow(47, 34.5, 51, 34.5)
    d.arrow(72, 34.5, 76, 34.5)

    # 2행: VT 능력 조회
    d.box(24, 16, 74, 10, P["chip"], ec=P["edge"])
    d.text(61, 23.6, "VT 능력 조회 (Get* 요청·응답)", size=9.5, color=P["dim"])
    for i, label in enumerate(["GetMemory", "GetNumber\nSoftkeys",
                               "GetTextFont\nData", "GetHardware",
                               "GetVersions"]):
        x = 26.5 + i * 14
        d.box(x, 17.4, 12.5, 5.2, P["purple"])
        d.text(x + 6.25, 20, label, size=8.6)

    d.arrow(87, 30, 87, 26, rad=0.0)

    # 3행: 버전 분기
    d.box(58, 3, 18, 9, P["green"])
    d.text(67, 7.5, "LoadVersion\n(VT 캐시 재사용)", size=9)

    d.box(31, 3, 22, 9, P["brown"])
    d.text(42, 7.5, "UploadObjectPool\n→ EndOfObjectPool", size=9)

    d.box(2, 3, 22, 9, P["gray"], ec=P["accent"], lw=1.8)
    d.text(13, 7.5, "Connected\n(애플리케이션 계층)", size=9.5, weight="bold")

    d.arrow(50, 16, 45, 12, color=P["orange"])
    d.text(40, 14.2, "버전 없음", size=8.2, color=P["orange"])
    d.arrow(72, 16, 69, 12, color=P["violet"])
    d.text(63.5, 13.8, "해시 일치", size=8.2, color=P["violet"])

    d.arrow(31, 7.5, 24, 7.5)
    d.arrow(58, 5.2, 53, 5.2)

    d.box(80, 3, 18, 9, P["gray"], ec=P["edge"], lw=1.2)
    d.text(89, 7.5, "Failed", size=9.5, color=P["dim"])
    d.arrow(95, 16, 95, 12, color=P["edge"], ls="--", lw=1.2)
    d.text(84.5, 13.9, "타임아웃·오류", size=8.2, color=P["dim"])


diagram("13-vt-client-lifecycle", draw, w=13, h=5.6, ymax=42)
