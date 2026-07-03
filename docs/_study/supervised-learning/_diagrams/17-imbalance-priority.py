"""CH17 불균형 대응 우선순위 — 지표 재정의부터 리샘플링까지 단계 사다리 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    steps = [
        (P["blue"], "1. 지표부터 바꾼다",
         "정확도 폐기 → PR-AUC·F1·recall\n비용 기준으로 무엇이 중요한지 정의"),
        (P["green"], "2. threshold 조정",
         "기본 0.5는 규칙이 아니다\n비용 기반으로 최적 임계값 탐색"),
        (P["purple"], "3. class_weight",
         "손실에 소수 클래스 가중\n데이터 안 늘리고 모델만 조정"),
        (P["brown"], "4. 리샘플링 (최후)",
         "언더/오버·SMOTE\nCV fold 안에서만, train에만"),
    ]
    w, gap = 21.5, 3
    x0 = 3
    for i, (fc, head, body) in enumerate(steps):
        x = x0 + i * (w + gap)
        d.box(x, 6, w, 20, fc)
        d.text(x + w / 2, 21, head, size=10, weight="bold")
        d.text(x + w / 2, 13.5, body, size=8.4, color=P["dim"])
        if i:
            d.arrow(x - gap + 0.3, 16, x - 0.3, 16, color=P["accent"], lw=1.6)

    d.text(x0, 30, "간단·저위험 → 복잡·고위험 순으로 올라간다",
           size=9, color=P["dim"], ha="left", style="italic")


diagram("17-imbalance-priority", draw, w=13, h=3.6, ymax=33)
