"""CH32 §4 오브젝트 풀 전송 순서 (light/dark PNG)."""
from _common import diagram

ECU_X, VT_X = 17, 83
HEAD_H = 6.5
FRAME_X0, FRAME_X1 = 3, 97

# (종류, ...) 위에서 아래로 그린다
ROWS = [
    ("msg", "VT", "VT Status (1초마다: 활성 마스크, busy 상태 등)"),
    ("msg", "ECU", "Working Set Maintenance (1초마다)"),
    ("msg", "ECU", "Get Memory (오브젝트 풀 크기 전달, VT 버전 확인)"),
    ("msg", "VT", "Get Memory Response (저장 가능 여부)"),
    ("frame", "A. 버전이 일치하는 풀이 VT에 이미 저장되어 있을 때"),
    ("msg", "ECU", "Load Version (저장된 버전 불러오기)"),
    ("msg", "VT", "Load Version Response (성공)"),
    ("end",),
    ("frame", "B. 새로 보내야 할 때"),
    ("msg", "ECU", "Object Pool Transfer (TP/ETP로 전송, 응답 없음)"),
    ("note", 50, 62, "1785바이트 초과 시 ETP 사용, ETP 최대 117,440,505바이트"),
    ("msg", "ECU", "End of Object Pool (전송 완료 알림)"),
    ("note", VT_X, 26, "파싱 중: parsing 비트 = 1"),
    ("msg", "VT", "End of Object Pool Response (파싱 결과)"),
    ("msg", "ECU", "Store Version (다음 Load Version을 위해 저장)"),
    ("end",),
    ("note", VT_X, 26, "풀 파싱, 화면 활성화"),
    ("note", VT_X, 26, "Active Data Mask 표시"),
]
STEP = {"msg": 4.6, "note": 4.4, "frame": 3.8, "end": 3.6}

BOTTOM = 3
CONTENT = sum(STEP[r[0]] for r in ROWS)
TOP = BOTTOM + CONTENT + 4 + HEAD_H
YMAX = TOP + 1


def draw(d):
    P = d.P
    for x, name, sub in ((ECU_X, "작업기 ECU", "VT 클라이언트"), (VT_X, "VT", "서버")):
        d.box(x - 11, TOP - HEAD_H, 22, HEAD_H, P["blue"])
        d.text(x, TOP - HEAD_H / 2 + 1.3, name, size=10.5, weight="bold")
        d.text(x, TOP - HEAD_H / 2 - 1.3, sub, size=8.5, color=P["dim"])
        d.ax.plot([x, x], [TOP - HEAD_H, BOTTOM], color=P["edge"], lw=1.2, zorder=1)

    y = TOP - HEAD_H - 3
    frame_top = None
    for row in ROWS:
        kind = row[0]
        if kind == "msg":
            y -= STEP[kind]
            src, label = row[1], row[2]
            from_vt = src == "VT"
            x1, x2 = (VT_X, ECU_X) if from_vt else (ECU_X, VT_X)
            d.arrow(x1, y, x2, y, color=P["orange"] if from_vt else P["accent"], lw=1.5,
                    ls="--" if from_vt else "-")
            d.text((ECU_X + VT_X) / 2, y + 1.5, label, size=9.5)
        elif kind == "note":
            y -= STEP[kind]
            _, cx, w, label = row
            d.box(cx - w / 2, y - 1.6, w, 3.2, P["chip"], lw=1.0)
            d.text(cx, y, label, size=8.8, color=P["dim"])
        elif kind == "frame":
            y -= 1.2
            frame_top = y
            d.ax.text(FRAME_X0 + 1, y - 1.9, row[1], fontsize=8.8, color=P["orange"],
                      ha="left", va="center", fontweight="bold", zorder=6,
                      bbox=dict(boxstyle="square,pad=0.25", facecolor=P["bg"],
                                edgecolor=P["edge"], linewidth=0.8))
            y -= STEP[kind] - 1.2
        elif kind == "end":
            y -= 2.4
            d.ax.plot([FRAME_X0, FRAME_X1, FRAME_X1, FRAME_X0, FRAME_X0],
                      [frame_top, frame_top, y, y, frame_top],
                      color=P["edge"], lw=1.0, ls="--", zorder=1)
            y -= STEP[kind] - 2.4


diagram("32-pool-transfer", draw, w=12, h=12 * YMAX / 100, xmax=100, ymax=YMAX)
