"""CH15 §11 VT 클라이언트(Working Set) 초기화 상태 머신 (light/dark PNG)."""
from _common import diagram

BW, BH = 17, 7.5

STATES = {
    "claim": (9.5, 48, "AUX 할당 지움·\n주소 클레임", "chip"),
    "wait": (35, 48, "VT Status 대기", "blue"),
    "ident": (60.5, 48, "WS 식별\n(WS Master 메시지)", "blue"),
    "maint": (86, 48, "Maintenance 시작\n(첫 메시지만 Initiating)", "blue"),
    "query": (90, 30, "기술 데이터·\n저장 버전 조회", "blue"),
    "load": (90, 13, "Load Version\n(parsing 비트 관찰)", "purple"),
    "upload": (58, 30, "전체 업로드\n(Get Memory→Transfer→EOP)", "brown"),
    "store": (58, 13, "Store Version\n(선택)", "brown"),
    "done": (30, 13, "연결 완료\n(운용)", "green"),
    "safe": (9.5, 30, "안전 상태", "gray"),
}


def pt(name, side, dx=0.0, dy=0.0):
    x, y = STATES[name][0], STATES[name][1]
    base = {
        "l": (x - BW / 2, y),
        "r": (x + BW / 2, y),
        "t": (x, y + BH / 2),
        "b": (x, y - BH / 2),
    }[side]
    return base[0] + dx, base[1] + dy


def draw(d):
    P = d.P
    for name, (x, y, label, color) in STATES.items():
        ec = P["accent"] if name in ("done", "safe") else None
        d.box(x - BW / 2, y - BH / 2, BW, BH, P[color], ec=ec)
        d.text(x, y, label, size=9)

    def link(p1, p2, label="", at=None, color=None, ls="-", rad=0.0):
        d.arrow(p1[0], p1[1], p2[0], p2[1], color=color or P["accent"], ls=ls, rad=rad)
        if label:
            lx, ly = at if at else ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2 + 1.4)
            d.text(lx, ly, label, size=8, color=P["dim"])

    warn = P["orange"]
    link(pt("claim", "r"), pt("wait", "l"), "주소 확보")
    link(pt("wait", "r"), pt("ident", "l"), "VT Status 수신")
    link(pt("ident", "r"), pt("maint", "l"))
    link(pt("maint", "b"), pt("query", "t"))
    link(pt("query", "b"), pt("load", "t"), "맞는 라벨 있음", at=(96.2, 21.5))
    link(pt("query", "l"), pt("upload", "r"), "라벨 없음·조회 생략")
    link(pt("load", "l", dy=2.0), pt("upload", "b", dx=6.0), "오류·무응답",
         at=(73.5, 16.0), color=warn, ls="--")
    link(pt("load", "b"), pt("done", "b"), "Error Codes=0", at=(60, 6.0), rad=-0.16)
    link(pt("upload", "b", dx=-3.0), pt("store", "t", dx=-3.0), "EOP 오류 없음", at=(49.8, 21.5))
    link(pt("store", "l"), pt("done", "r"), "응답 수신")
    link(pt("upload", "l"), pt("safe", "r"), "EOP 오류", color=warn, ls="--")
    link(pt("done", "t", dx=-4.0), pt("safe", "b", dx=4.0), "VT Status\n3초 끊김",
         at=(24.8, 22.6), color=warn, ls="--")
    link(pt("safe", "t"), pt("claim", "b"), "재연결 설계면\n초기화 재시작",
         at=(16.2, 39.0), color=P["violet"], ls="--")


diagram("15-client-init-state", draw, w=14, h=8.2, xmax=101, ymax=55)
