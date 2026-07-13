"""CH11 메모리 지표 — VSS/RSS/PSS/USS 포함 관계 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    # 중첩 박스로 포함 관계 표현 (바깥이 넓은 개념)
    d.box(4, 4, 62, 40, P["gray"])
    d.text(35, 41, "VSS — 가상 주소 공간 전체 (매핑됐지만 미할당 포함)",
           size=9.5, weight="bold", color=P["dim"])

    d.box(9, 8, 52, 30, P["brown"])
    d.text(35, 35, "RSS — 물리 메모리에 올라온 페이지 전체 (공유 라이브러리 통째 계산)",
           size=9, weight="bold")

    d.box(14, 12, 42, 20, P["blue"])
    d.text(35, 29, "PSS — 공유 페이지를 공유 프로세스 수로 나눠 배분",
           size=9, weight="bold")

    d.box(20, 16, 30, 12, P["green"])
    d.text(35, 24, "USS", size=11, weight="bold")
    d.text(35, 20, "이 프로세스만의\n독점(사유) 페이지", size=8.8, color=P["dim"])

    # 오른쪽 도구 힌트
    tips = [
        "procrank — PSS/USS 순위",
        "showmap <pid> — 매핑별 분해",
        "dumpsys meminfo — 항목별 PSS",
        "/proc/<pid>/smaps — 원천 데이터",
    ]
    for i, t in enumerate(tips):
        y = 34 - i * 8
        d.box(70, y, 26, 6, P["chip"])
        d.text(83, y + 3, t, size=8.5, color=P["dim"])


diagram("11-memory-metrics", draw, w=12, h=6, ymax=48)
