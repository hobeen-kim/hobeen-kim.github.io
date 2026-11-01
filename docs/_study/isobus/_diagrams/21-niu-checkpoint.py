"""CH21 §1 NIU 네 유형을 검문소 비유로: 유형마다 하는 일이 누적되는 모습 (light/dark PNG)."""
from _common import diagram

JOBS = [
    ("전달", "forwarding"),
    ("거르기", "filtering"),
    ("주소 변환", "address translation"),
    ("재포장", "repackaging"),
]

ROWS = [
    ("Repeater", "모든 차를 그대로 통과", "gray", 1, "공유"),
    ("Bridge", "통행 목록을 보고 골라 통과", "blue", 2, "공유"),
    ("Router", "번호판을 바꿔 달고 통과", "green", 3, "분리"),
    ("Gateway", "짐을 풀어 새 상자로 꾸림", "brown", 4, "분리"),
]

JOB_X = [41, 55, 69, 83]


def draw(d):
    P = d.P
    top = 45.5

    d.text(14, top, "NIU 유형 (검문소 비유)", size=10, weight="bold", color=P["dim"])
    for x, (ko, en) in zip(JOB_X, JOBS):
        d.text(x, top + 0.8, ko, size=10, weight="bold", color=P["dim"])
        d.text(x, top - 1.6, en, size=8, color=P["dim"])
    d.text(95.5, top, "주소 공간", size=10, weight="bold", color=P["dim"])

    row_h = 9.6
    box_h = 7.2
    for i, (name, sub, color, n_jobs, space) in enumerate(ROWS):
        y = top - 5.5 - (i + 1) * row_h + (row_h - box_h)
        cy = y + box_h / 2

        d.box(2, y, 25, box_h, P[color])
        d.text(14.5, cy + 1.4, name, size=11, weight="bold")
        d.text(14.5, cy - 1.6, sub, size=8.6, color=P["dim"])

        for k, x in enumerate(JOB_X):
            done = k < n_jobs
            if done:
                d.box(x - 5.5, cy - 2.3, 11, 4.6, P[color], ec=P["accent"], lw=1.6)
                d.text(x, cy, "O", size=11, weight="bold", color=P["accent"])
            else:
                d.box(x - 5.5, cy - 2.3, 11, 4.6, P["chip"])
                d.text(x, cy, "X", size=10, color=P["dim"])

        space_color = P["accent"] if space == "공유" else P["orange"]
        d.text(95.5, cy, space, size=10.5, weight="bold", color=space_color)


diagram("21-niu-checkpoint", draw, w=12.5, h=5.8, xmax=100, ymax=48)
