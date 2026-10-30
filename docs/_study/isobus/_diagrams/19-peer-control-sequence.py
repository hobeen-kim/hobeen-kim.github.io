"""CH19 §16 Peer control assignment 절차 — 할당, 응답, 직접 setpoint 전송, 해제 (light/dark PNG)."""
from _common import diagram

X = {"user": 13, "src": 47, "tc": 87}
NAMES = {"user": "setpoint value user\n(rate controller)",
         "src": "setpoint value source\n(센서 CF)",
         "tc": "TC"}
TOP = 42.6
STEP = 4.3

# (종류, 시작, 끝, 라벨) — note는 (종류, 위치, None, 라벨)
ROWS = [
    ("note", "tc", None, "태스크 active"),
    ("msg", "tc", "src", "9 / mode 3  Assign Transmitter\nDETx·DDI, 목적지 DETy, user NAME"),
    ("msg", "tc", "user", "9 / mode 0  Assign Receiver\nDETy·DDI, source NAME"),
    ("ack", "src", "tc", "9 / mode 5  Transmitter Ack (250 ms 안)"),
    ("ack", "user", "tc", "9 / mode 2  Receiver Ack (250 ms 안)"),
    ("data", "src", "user", "3  Value command  DETy·DDI\n1 Hz 주기 + on change"),
    ("note", "user", None, "3 s 미수신 -> TC 통신 상실처럼 처리"),
    ("note", "tc", None, "태스크 inactive"),
    ("note2", ("src", "user"), None, ("송신 중지·할당 취소", "setpoint 거부·할당 취소")),
]


def row_y(i):
    return TOP - 5.2 - i * STEP


def label_x(a, b):
    xa, xb = X[a], X[b]
    lo, hi = min(xa, xb), max(xa, xb)
    if "src" not in (a, b):
        return (X["src"] + X["tc"]) / 2
    return (lo + hi) / 2


def note_rows(key):
    ys = []
    for i, (kind, a, _, _) in enumerate(ROWS):
        if (kind == "note" and a == key) or (kind == "note2" and key in a):
            ys.append(row_y(i))
    return ys


def draw(d):
    P = d.P
    bottom = row_y(len(ROWS) - 1) - 1.8
    for key, x in X.items():
        d.box(x - 10, TOP - 3.4, 20, 4.4, P["blue"])
        d.text(x, TOP - 1.2, NAMES[key], size=8.8, weight="bold")
        start = TOP - 3.5
        for g in note_rows(key) + [None]:
            end = bottom if g is None else g + 1.2
            if start - end > 0.5:
                d.arrow(x, start, x, end, color=P["edge"], lw=1.0, style="-", ls="--")
            if g is not None:
                start = g - 1.2

    for i, (kind, a, b, label) in enumerate(ROWS):
        y = row_y(i)
        if kind in ("msg", "ack", "data"):
            color = {"msg": P["accent"], "ack": P["orange"], "data": P["violet"]}[kind]
            ls = "--" if kind == "ack" else "-"
            d.arrow(X[a], y, X[b], y, color=color, ls=ls)
            lines = label.count("\n") + 1
            d.text(label_x(a, b), y + 0.75 + 0.7 * lines, label, size=7.8)
        elif kind == "note":
            d.box(X[a] - 11.5, y - 1.1, 23, 2.2, P["green"])
            d.text(X[a], y, label, size=7.8)
        else:
            for who, text in zip(a, label):
                d.box(X[who] - 11.5, y - 1.1, 23, 2.2, P["brown"])
                d.text(X[who], y, text, size=7.8)


diagram("19-peer-control-sequence", draw, w=12, h=5.5, xmax=100, ymax=43.6)
