"""51장 3절 FS 접근 흐름(옛 21장 mermaid sequenceDiagram을 옮김) (light/dark PNG)."""
from _common import diagram

C, FS = 20, 80

# (y, from, to, label, response?)
ROWS = [
    (53.0, C, FS, "Get File Server Properties Request", False),
    (47.5, FS, C, "Properties Response (버전, 최대 동시 열기 파일 수, 다중 볼륨 지원 여부)", True),
    (38.5, C, FS, "Client Connection Maintenance", False),
    (31.0, C, FS, "Open File Request (TAN, Flags, 경로)", False),
    (25.5, FS, C, "Open File Response (TAN, 에러 코드, Handle, 속성)", True),
    (17.0, C, FS, "Read/Write File Request (TAN, Handle, 바이트 수)", False),
    (11.5, FS, C, "Read/Write File Response (TAN, 에러 코드, 데이터 또는 실제 처리 수)", True),
    (5.5, C, FS, "Close File Request (TAN, Handle)", False),
    (1.0, FS, C, "Close File Response (TAN, 에러 코드)", True),
]

LOOPS = [
    (34.8, 43.6, "반복: 연결 유지 (2 s 주기)"),
    (8.6, 22.0, "반복: 데이터 전송"),
]


def draw(d):
    P = d.P
    for x, name in ((C, "Client (TC)"), (FS, "File Server")):
        d.box(x - 11, 64, 22, 6, P["blue"] if x == FS else P["chip"])
        d.text(x, 67, name, size=10, weight="bold")
        d.arrow(x, 63.8, x, -1.5, color=P["edge"], lw=1.0, style="-", ls="--")

    d.box(8, 57.2, 84, 4.6, P["brown"])
    d.text(50, 59.5, "FS는 File Server Status를 주기 방송 (평시 2 s, busy 시 200 ms)", size=9)

    for y0, y1, label in LOOPS:
        d.box(6, y0, 88, y1 - y0, P["gray"], ec=P["violet"], lw=1.1, alpha=0.6)
        d.text(7.5, y1 - 1.6, label, size=8.6, color=P["violet"], ha="left")

    for y, a, b, label, resp in ROWS:
        d.arrow(a, y, b, y, lw=1.4, ls="--" if resp else "-")
        d.text((a + b) / 2, y + 1.6, label, size=8.6)


diagram("51-fs-access-sequence", draw, w=12, h=7.6, xmax=100, ymax=71)
