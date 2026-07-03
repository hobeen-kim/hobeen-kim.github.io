"""CH17 쓰기 경로 시퀀스 — distributor → ingester → 스토리지 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    actors = [
        (12, "클라이언트", "Alloy / Promtail", P["blue"]),
        (38, "Distributor", "stateless", P["gray"]),
        (64, "Ingester", "stateful · WAL", P["green"]),
        (89, "오브젝트\n스토리지", "S3 / GCS", P["brown"]),
    ]
    for x, name, sub, fc in actors:
        d.box(x - 9, 47, 18, 6, fc, ec=P["accent"], lw=1.4)
        d.text(x, 50.6, name, size=10, weight="bold")
        d.text(x, 48.4, sub, size=7.5, color=P["dim"])
        d.ax.plot([x, x], [5, 47], color=P["edge"], lw=1.1, ls="--", zorder=1)

    def hmsg(x1, x2, y, label, color):
        d.arrow(x1, y, x2, y, color=color)
        d.text((x1 + x2) / 2, y + 1.4, label, size=8, color=color)

    def selfmsg(x, y, label):
        d.box(x + 1.5, y - 1.6, 21, 3.2, P["chip"], ec=P["orange"], lw=1.1)
        d.text(x + 12, y, label, size=8)

    hmsg(12, 38, 43, "POST /push (로그 배치)", P["dim"])
    selfmsg(38, 39, "검증 + rate limit")
    selfmsg(38, 34.5, "라벨 해싱 → ingester 결정")
    hmsg(38, 64, 30, "스트림 라우팅 (복제)", P["orange"])
    selfmsg(64, 26, "WAL 기록")
    selfmsg(64, 21.5, "메모리 청크 append")

    d.box(50, 13, 28, 5, P["chip"], ec=P["orange"], lw=1.2)
    d.text(64, 15.5, "청크 가득 참 / 유휴 초과 시", size=8, color=P["orange"])

    hmsg(64, 89, 8, "압축 청크 + 인덱스 flush", P["accent"])


diagram("17-write-path", draw, w=13, h=6.4, ymax=55)
