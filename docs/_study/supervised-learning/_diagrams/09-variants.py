"""CH9 나이브 베이즈 세 변형 — 특징 형태에 따라 우도 모델을 고른다 (light/dark PNG)."""
from _common import diagram


def draw(d):
    P = d.P

    cards = [
        ("Gaussian", P["blue"],
         "연속형 특징",
         "각 특징이 클래스별\n정규분포를 따른다고 가정\n\n예: 센서 측정값, 키·몸무게"),
        ("Multinomial", P["green"],
         "횟수 · 빈도",
         "단어 등장 횟수 같은\n카운트 데이터\n\n예: 텍스트 분류(BoW·TF)"),
        ("Bernoulli", P["brown"],
         "이진 (0/1)",
         "특징의 등장 여부만\n사용 (있다/없다)\n\n예: 단어 포함 여부"),
    ]
    w, gap = 30, 3
    x0 = 2
    for i, (title, fc, tag, body) in enumerate(cards):
        x = x0 + i * (w + gap)
        d.box(x, 3, w, 34, fc)
        d.text(x + w / 2, 32, title, size=12, weight="bold")
        d.text(x + w / 2, 26.5, tag, size=9.5, color=P["accent"], weight="bold")
        d.text(x + w / 2, 15, body, size=9, color=P["dim"])


diagram("09-variants", draw, w=12, h=4.6, xmax=100, ymax=40)
