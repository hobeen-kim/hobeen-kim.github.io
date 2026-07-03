---
title: "일반화와 과적합"
description: "암기와 일반화를 가르는 선을 짚고, train/valid/test 3분할이 왜 필요한지 설명한다. 학습 곡선으로 과적합·과소적합을 진단하고, 편향-분산 트레이드오프를 직관 중심으로 이해한 뒤 모델 복잡도를 제어하는 수단들을 개관한다."
date: 2026-07-03
tags: [Machine Learning, Supervised Learning, Overfitting, Bias-Variance, Generalization]
prev: /study/supervised-learning/01-what-is-supervised-learning
next: /study/supervised-learning/03-evaluation-metrics
---

# 일반화와 과적합

::: info 학습 목표
- 암기(memorization)와 일반화(generalization)가 무엇이 다른지 설명한다.
- train/valid/test 3분할이 왜 필요하며 각 조각이 어떤 역할을 하는지 이해한다.
- 학습 곡선으로 과적합과 과소적합을 진단할 수 있다.
- 편향-분산 트레이드오프를 수식 최소로, 직관 중심으로 파악한다.
- 모델 복잡도를 제어하는 대표 수단들을 개관한다.
:::

## 1. 암기 vs 일반화

[1장](/study/supervised-learning/01-what-is-supervised-learning)에서 지도 학습의 진짜 목표는 훈련 데이터가 아니라 <strong>본 적 없는 데이터에서의 손실 최소화</strong>라고 했다. 이 문장이 이 챕터 전체를 지배한다.

훈련 데이터를 완벽히 맞히는 모델은 만들기 쉽다. 극단적으로, 모든 훈련 샘플과 정답을 통째로 외운 뒤 "본 적 있는 입력이면 외운 답을, 처음 보는 입력이면 아무 답이나" 내는 모델은 훈련 정확도 100%다. 하지만 이건 <strong>암기</strong>일 뿐 새 데이터엔 무력하다.

우리가 원하는 것은 <strong>일반화</strong> — 훈련 데이터에서 배운 규칙이 처음 보는 데이터에도 통하는 것이다. 시험공부에 비유하면, 기출문제의 정답 번호를 외운 학생과 원리를 이해한 학생은 기출을 푸는 실력은 같아 보여도 새 문제 앞에서 갈린다. 머신러닝의 모든 기법은 결국 <strong>암기를 억제하고 일반화를 유도하는 장치</strong>다.

## 2. train / valid / test 3분할

일반화 성능을 재려면 <strong>학습에 쓰지 않은 데이터</strong>로 평가해야 한다. 그래서 데이터를 최소 세 조각으로 나눈다.

![train/valid/test 3분할 — 전체 데이터를 Train(모델이 fit, 여러 번 반복해서 봄), Valid(튜닝·모델 선택, 간접적으로 정보 누출), Test(최종 성능 1회 측정, 배포 전 마지막에만)로 나누고 학습→검증→테스트 한 방향으로 진행한다](/images/study-supervised-learning/02-train-valid-test-light.png)
![train/valid/test 3분할 — 전체 데이터를 Train(모델이 fit, 여러 번 반복해서 봄), Valid(튜닝·모델 선택, 간접적으로 정보 누출), Test(최종 성능 1회 측정, 배포 전 마지막에만)로 나누고 학습→검증→테스트 한 방향으로 진행한다](/images/study-supervised-learning/02-train-valid-test-dark.png)

- <strong>Train</strong> — 모델이 파라미터를 학습하는 데 쓴다. 모델은 이 데이터를 여러 번 본다.
- <strong>Valid(검증)</strong> — 하이퍼파라미터를 고르고 모델을 비교하는 데 쓴다. 모델 파라미터를 직접 학습하진 않지만, 우리가 이 점수를 보고 결정을 내리므로 <strong>간접적으로 정보가 새어 들어간다</strong>. 검증셋에 맞춰 튜닝을 반복하면 검증셋에도 과적합될 수 있다.
- <strong>Test</strong> — 배포 직전 딱 한 번, 최종 성능을 재는 데만 쓴다. 이 점수를 보고 다시 모델을 고치기 시작하면 test는 사실상 두 번째 valid가 되어 순수한 일반화 추정치의 자격을 잃는다.

test를 "마지막에 한 번만"으로 지키는 규율이 핵심이다. 데이터가 적어 고정 valid를 떼기 아까울 땐 train+valid를 교차 검증(cross-validation)으로 돌려 쓰는데, 이는 [4장](/study/supervised-learning/04-cross-validation-tuning)의 주제다. 어떤 방식이든 <strong>test는 건드리지 않는다</strong>는 원칙은 같다.

::: warning 데이터 누출(leakage)
분할보다 먼저 스케일링·인코딩·결측 대치를 전체 데이터에 적용하면 test의 정보가 train으로 새어 들어가 성능이 낙관적으로 부풀려진다. 전처리는 <strong>반드시 분할 이후 train에서만</strong> 학습해야 한다. sklearn `Pipeline`으로 이를 구조적으로 막는 방법은 [16장](/study/supervised-learning/16-feature-engineering-pipeline)에서 다룬다.
:::

## 3. 과적합·과소적합 진단 — 학습 곡선

<strong>과적합(overfitting)</strong>은 모델이 훈련 데이터의 신호뿐 아니라 노이즈까지 외운 상태다. 훈련 점수는 높은데 검증 점수가 확 낮다. <strong>과소적합(underfitting)</strong>은 모델이 너무 단순해 신호조차 못 잡은 상태다. 훈련 점수도 검증 점수도 둘 다 낮다.

둘을 구분하는 실전 도구가 <strong>train/valid 점수의 격차</strong>다.

| 상태 | 훈련 점수 | 검증 점수 | 격차 | 처방 |
|---|---|---|---|---|
| 과소적합 | 낮음 | 낮음 | 작음 | 복잡도↑, 특징 추가, 규제↓ |
| 적정 | 높음 | 높음 | 작음 | 유지 |
| 과적합 | 매우 높음 | 낮음 | 큼 | 복잡도↓, 데이터↑, 규제↑ |

sklearn `learning_curve`로 훈련 샘플 수에 따른 두 점수의 궤적을 그려 진단할 수 있다.

```python
import numpy as np
from sklearn.model_selection import learning_curve
from sklearn.tree import DecisionTreeClassifier

# max_depth를 키우면 과적합 쪽으로 기운다
sizes, train_scores, valid_scores = learning_curve(
    DecisionTreeClassifier(max_depth=None),   # 제한 없는 깊은 트리
    X, y, train_sizes=np.linspace(0.1, 1.0, 5), cv=5)

print("train:", train_scores.mean(axis=1))    # 거의 1.0에 붙어 있으면
print("valid:", valid_scores.mean(axis=1))    # valid와 벌어진 격차가 과적합의 증거
```

훈련 점수가 1.0 근처에 붙어 있는데 검증 점수가 한참 아래에서 멈춰 있고, 데이터를 더 넣어도 두 곡선이 좁혀지지 않으면 과적합이다. 반대로 두 곡선이 낮은 값에서 이미 붙어 있으면 과소적합 — 데이터를 더 넣는 것보다 모델을 키우는 게 답이다.

## 4. 편향-분산 트레이드오프

과적합과 과소적합의 뿌리를 한 단계 더 파고들면 <strong>편향-분산 분해</strong>가 나온다. 모델의 기대 예측 오차는 크게 세 조각으로 나뉜다.

- <strong>편향(bias)</strong> — 모델이 너무 단순해서 진짜 관계를 구조적으로 못 잡는 정도. 직선으로 곡선을 근사하려는 데서 오는 체계적 오차다. 과소적합의 원인.
- <strong>분산(variance)</strong> — 훈련 데이터가 조금만 바뀌어도 학습된 모델이 크게 흔들리는 정도. 노이즈에 과민 반응하는 데서 온다. 과적합의 원인.
- <strong>줄일 수 없는 오차(irreducible)</strong> — 데이터 자체의 노이즈. 어떤 모델로도 못 없앤다.

모델을 복잡하게 만들수록 편향은 줄지만 분산은 커진다. 반대로 단순하게 만들면 분산은 줄지만 편향이 커진다. <strong>둘을 동시에 0으로 만들 수 없다는 이 맞교환이 편향-분산 트레이드오프</strong>다.

![편향-분산 트레이드오프 — 모델 복잡도가 커질수록 편향²은 감소하고 분산은 증가하며, 둘의 합인 검증 오차는 U자를 그려 최적 복잡도에서 최소가 된다. 학습 오차는 복잡도와 함께 단조 감소한다](/images/study-supervised-learning/02-bias-variance-light.png)
![편향-분산 트레이드오프 — 모델 복잡도가 커질수록 편향²은 감소하고 분산은 증가하며, 둘의 합인 검증 오차는 U자를 그려 최적 복잡도에서 최소가 된다. 학습 오차는 복잡도와 함께 단조 감소한다](/images/study-supervised-learning/02-bias-variance-dark.png)

검증 오차(편향²+분산)는 복잡도에 대해 <strong>U자</strong>를 그린다. 왼쪽 끝은 과소적합(편향 지배), 오른쪽 끝은 과적합(분산 지배), 골짜기가 최적 복잡도다. 학습 오차는 복잡도와 함께 계속 떨어지기만 하므로, <strong>학습 오차만 보고 모델을 고르면 반드시 오른쪽 과적합 지대로 끌려간다.</strong> 그래서 검증셋이 필요하다.

이 트레이드오프는 앙상블에서 다시 만난다. 배깅·랜덤 포레스트는 분산을 낮추는 쪽, 부스팅은 편향을 낮추는 쪽으로 작동하는데, 그 메커니즘은 [11장 앙상블 기초](/study/supervised-learning/11-ensemble-basics)에서 이 프레임으로 재방문한다.

## 5. 모델 복잡도 제어 수단

과적합은 복잡도를 낮추거나 데이터를 늘려 다스린다. 대표 수단을 개관한다.

- <strong>규제(regularization)</strong> — 손실에 "파라미터가 크면 벌점"을 더해 모델이 과하게 복잡해지는 걸 억제한다. 선형 모델의 릿지/라쏘([6장](/study/supervised-learning/06-linear-regression))가 전형이다.
- <strong>구조적 제약</strong> — 트리의 최대 깊이(`max_depth`), 리프 최소 샘플 수처럼 모델이 가질 수 있는 복잡도 자체에 상한을 건다.
- <strong>조기 종료(early stopping)</strong> — 검증 점수가 나빠지기 시작하면 학습을 멈춘다. 부스팅에서 특히 강력하며 [15장](/study/supervised-learning/15-gbdt-tuning)에서 다룬다.
- <strong>데이터 늘리기</strong> — 데이터가 많을수록 노이즈를 외우기 어려워져 분산이 자연히 줄어든다. 가장 근본적인 처방이지만 가장 비싸다.
- <strong>앙상블</strong> — 여러 모델을 합쳐 분산 또는 편향을 낮춘다(11장 이후).

규제의 효과는 코드로 바로 확인된다. 트리의 `max_depth` 하나만 조여도 훈련·검증 격차가 줄어든다.

```python
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import cross_val_score

for depth in [None, 8, 4, 2]:              # None=제한 없음(과적합 위험)
    clf = DecisionTreeClassifier(max_depth=depth)
    train = clf.fit(X_train, y_train).score(X_train, y_train)
    valid = cross_val_score(clf, X_train, y_train, cv=5).mean()
    print(f"depth={depth}: train={train:.3f} valid={valid:.3f}")
# depth=None 은 train≈1.0 이지만 valid와 벌어지고,
# depth를 줄이면 격차가 좁아지다가 너무 줄이면 둘 다 떨어진다(과소적합).
```

`depth=None`에서 훈련 점수는 거의 1.0에 붙지만 검증 점수와 벌어진다. 깊이를 줄이면 격차가 좁혀지고, 지나치게 줄이면 이번엔 둘 다 낮아진다. 이 과정이 바로 U자 곡선 위를 오른쪽에서 왼쪽으로 걸어가는 것과 같다.

이 수단들은 모두 <strong>복잡도라는 하나의 손잡이를 어느 방향으로 돌리는가</strong>로 이해할 수 있다. 무엇을 쓰든 최종 판단은 검증 성능이 내린다.

::: tip 핵심 정리
- 목표는 훈련 데이터 암기가 아니라 새 데이터로의 일반화이며, 머신러닝 기법은 암기를 억제하는 장치다.
- train은 학습, valid는 튜닝·모델 선택, test는 배포 직전 1회 측정에만 쓴다. test를 반복해서 보면 일반화 추정치 자격을 잃는다.
- 훈련↔검증 점수의 격차로 진단한다. 격차가 크면 과적합, 둘 다 낮으면 과소적합이다.
- 복잡도를 키우면 편향↓·분산↑, 줄이면 편향↑·분산↓ — 검증 오차는 U자를 그리고 골짜기가 최적점이다.
- 학습 오차만 보고 고르면 과적합으로 끌려가므로 반드시 검증셋으로 판단한다.
- 복잡도 제어 수단(규제·구조 제약·조기 종료·데이터·앙상블)은 모두 복잡도 손잡이를 조절하는 방식이다.
:::

## 다음 챕터

일반화가 잘됐는지 판단하려면 "잘됐다"를 재는 자가 필요하다. [모델 평가 지표](/study/supervised-learning/03-evaluation-metrics)에서는 회귀와 분류 각각의 지표, 정확도의 함정, 불균형 데이터에서 갈리는 ROC-AUC와 PR-AUC, 그리고 "지표는 비즈니스 비용에서 역산한다"는 선택 기준을 다룬다.
