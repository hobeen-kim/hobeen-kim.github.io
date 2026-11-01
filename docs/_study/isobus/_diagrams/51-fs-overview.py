"""51장 1절 File Server 큰 그림: 클라이언트, 두 PGN, FS 안의 볼륨 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    d.box(2, 4, 28, 40, P["gray"])
    d.text(16, 40.5, "클라이언트", size=11, weight="bold")
    for i, (name, sub) in enumerate((("TC", "Task Controller"), ("VT", "Virtual Terminal"),
                                     ("작업기 ECU", "USB 단자 없음"))):
        y = 29 - i * 11
        d.box(5, y, 22, 8, P["chip"])
        d.text(16, y + 5.2, name, size=10.5, weight="bold")
        d.text(16, y + 2.4, sub, size=8.5, color=P["dim"])

    d.box(68, 4, 30, 40, P["blue"])
    d.text(83, 40.5, "File Server (FS)", size=11, weight="bold")
    d.text(83, 36.5, "볼륨 목록 \\\\", size=9, color=P["dim"])
    for i, (name, sub) in enumerate((("FLASH", "내부 저장소"), ("VOL_B", "이동식 매체 (USB 메모리 등)"))):
        y = 24 - i * 13
        d.box(71, y, 24, 9, P["chip"])
        d.text(83, y + 5.8, name, size=10.5, weight="bold")
        d.text(83, y + 2.7, sub, size=8.5, color=P["dim"])

    d.arrow(31, 32, 67, 32, lw=2.0)
    d.text(49, 35, "요청: PGN 0xAA00 (43520)", size=9.5, weight="bold", color=P["accent"])
    d.text(49, 29.6, "Open, Read, Write, Close ...", size=8.5, color=P["dim"])

    d.arrow(67, 21, 31, 21, lw=2.0, ls="--")
    d.text(49, 24, "응답: PGN 0xAB00 (43776)", size=9.5, weight="bold", color=P["accent"])
    d.text(49, 18.6, "결과 코드, Handle, 파일 데이터", size=8.5, color=P["dim"])

    d.arrow(67, 10, 31, 10, lw=1.4, ls=":", color=P["orange"])
    d.text(49, 13, "File Server Status (전역 방송)", size=9, color=P["orange"])
    d.text(49, 7.6, "평소 2 s, 바쁠 때 200 ms", size=8.5, color=P["dim"])


diagram("51-fs-overview", draw, w=12, h=5.4, xmax=100, ymax=46)
