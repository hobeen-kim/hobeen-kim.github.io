---
title: "로지스틱 회귀"
description: "선형 출력을 시그모이드로 확률로 바꿔 분류를 푸는 로지스틱 회귀의 아이디어, 크로스엔트로피(로그 손실)의 의미, 선형 결정 경계와 C 파라미터 정규화, 소프트맥스·OvR·OvO 다중 클래스 전략, 확률 출력의 실무 가치와 강력한 베이스라인으로서의 위치를 정리한다."
date: 2026-07-03
tags: [Machine Learning, Supervised Learning, Logistic Regression, Softmax, scikit-learn]
prev: /study/supervised-learning/06-linear-regression
next: /study/supervised-learning/08-svm
---

# 로지스틱 회귀

::: info 학습 목표
- 선형 출력을 시그모이드에 통과시켜 확률로 바꾸는 로지스틱 회귀의 핵심 아이디어를 이해한다.
- 로그 손실(크로스엔트로피)이 무엇을 최소화하는지, 왜 제곱 오차 대신 이걸 쓰는지 안다.
- 로지스틱 회귀의 결정 경계가 왜 선형인지 이해한다.
- 정규화 파라미터 `C`가 릿지의 `alpha`와 어떤 관계인지 안다.
- 소프트맥스(다항)·OvR·OvO 다중 클래스 전략을 구분하고, 이 전략들이 SVM·트리 등 다른 모델에도 쓰이는 일반 기법임을 안다.
- 확률 출력의 실무 가치와, 강력한 베이스라인으로서 로지스틱 회귀의 위치를 파악한다.
:::

## 1. 회귀로 분류를 푸는 아이디어

이름은 "회귀"지만 로지스틱 회귀는 <strong>분류</strong> 모델이다. 아이디어는 [6장 선형 회귀](/study/supervised-learning/06-linear-regression)를 그대로 빌린다 — 먼저 피처의 가중 합으로 <strong>선형 출력</strong> `z = w·x + b`를 만든다. 문제는 이 `z`가 `-∞ ~ +∞` 범위라 "스팸일 확률"처럼 0~1 사이 값으로는 바로 못 쓴다는 것이다.

선형 회귀 출력을 그대로 쓰면 안 되나. 예측이 0.5를 넘으면 양성으로 잘라도 되긴 하지만, 출력이 -3이나 +5처럼 확률 범위를 벗어나 "확률"로 해석할 수 없고, 극단값 하나에 직선이 통째로 끌려가 경계가 밀리는 문제가 있다. 확률로 쓰려면 출력을 0~1로 가두는 장치가 필요하다.

그 장치가 <strong>시그모이드(sigmoid)</strong> 함수 `σ(z) = 1 / (1 + e⁻ᶻ)`다. 시그모이드는 어떤 실수든 0~1 사이로 눌러 담는 S자 곡선이라, 선형 출력을 그대로 <strong>확률</strong>로 해석할 수 있게 만든다. 즉 로지스틱 회귀는 "선형 출력 → 시그모이드 → 확률"의 3단 파이프라인이다.

![로지스틱 회귀의 파이프라인. 입력 특징 x가 선형 결합 z=w·x+b로 묶여 -무한대에서 +무한대 값이 되고, 시그모이드 σ를 통과해 0~1 확률 p가 되며, 임계값 판정(p≥0.5면 1, 아니면 0)으로 클래스가 정해진다](/images/study-supervised-learning/07-linear-to-prob-light.png)
![로지스틱 회귀의 파이프라인. 입력 특징 x가 선형 결합 z=w·x+b로 묶여 -무한대에서 +무한대 값이 되고, 시그모이드 σ를 통과해 0~1 확률 p가 되며, 임계값 판정(p≥0.5면 1, 아니면 0)으로 클래스가 정해진다](/images/study-supervised-learning/07-linear-to-prob-dark.png)

시그모이드 곡선을 보면 `z=0`에서 확률이 정확히 0.5이고, `z`가 커질수록 1에, 작아질수록 0에 가까워진다. 기본 임계값 0.5로 자르면 `z ≥ 0`인 영역이 양성 클래스가 된다.

![시그모이드 곡선. 가로축은 선형 출력 z, 세로축은 확률 p로, z=0에서 p=0.5인 결정 경계를 지나 z가 커지면 p가 1로, 작아지면 0으로 수렴하는 S자 곡선을 보여준다](/images/study-supervised-learning/07-sigmoid-light.png)
![시그모이드 곡선. 가로축은 선형 출력 z, 세로축은 확률 p로, z=0에서 p=0.5인 결정 경계를 지나 z가 커지면 p가 1로, 작아지면 0으로 수렴하는 S자 곡선을 보여준다](/images/study-supervised-learning/07-sigmoid-dark.png)

## 2. 로그 손실(크로스엔트로피)

가중치를 어떻게 학습할까. 선형 회귀처럼 (확률 − 정답)의 제곱 오차를 쓰면 될 것 같지만, 시그모이드를 끼우면 이 손실은 <strong>울퉁불퉁(non-convex)</strong>해져 경사하강법이 지역 최소에 빠지기 쉽다. 그래서 로지스틱 회귀는 <strong>로그 손실(log loss) = 크로스엔트로피(cross-entropy)</strong>를 쓴다.

로그 손실의 직관은 간단하다 — <strong>정답 클래스에 예측 확률을 얼마나 높게 줬는지</strong>를 본다. 정답이 양성(1)인데 모델이 0.9를 줬으면 벌점이 작고, 0.1을 줬으면 벌점이 크다. 특히 <strong>확신에 찬 오답</strong>(정답 1인데 0.01을 준 경우)에는 `-log(0.01)`처럼 벌점이 급격히 커진다. 이 손실은 볼록(convex)해서 경사하강법으로 전역 최소를 안정적으로 찾을 수 있고, 확률을 잘 맞히도록 모델을 밀어붙인다.

이 "확신에 찬 오답에 큰 벌점"이라는 성질은 학습에는 좋지만, 라벨이 잘못 붙은 데이터가 있으면 그 소수 샘플이 손실을 지배해 모델을 왜곡할 수 있다는 뜻이기도 하다. 라벨 노이즈가 의심되면 손실 곡선과 오분류 샘플을 함께 들여다보는 편이 좋다.

## 3. 결정 경계는 선형

로지스틱 회귀가 분류하는 경계를 보면 <strong>직선(고차원에선 초평면)</strong>이다. 확률이 0.5가 되는 지점이 경계인데, `σ(z) = 0.5`는 곧 `z = 0`, 즉 `w·x + b = 0`이라는 <strong>선형 방정식</strong>이기 때문이다. 시그모이드라는 비선형 함수를 끼웠어도 경계 자체는 선형으로 남는다.

따라서 로지스틱 회귀는 클래스가 직선/평면으로 대충 나뉠 때 잘 맞고, 복잡하게 얽힌 경계가 필요하면 한계가 있다. 이때는 [6장](/study/supervised-learning/06-linear-regression)의 다항 피처를 넣어 경계를 휘게 하거나, [8장 SVM](/study/supervised-learning/08-svm)의 커널·트리 계열로 넘어간다.

선형 출력 `z`는 사실 <strong>로그-오즈(log-odds)</strong> — 양성 확률과 음성 확률의 비율에 로그를 취한 값이다. 덕분에 계수 `wᵢ`는 "피처가 1 늘 때 로그-오즈가 얼마나 변하는가"로 읽히고, `e^wᵢ`(오즈비)로 바꾸면 "그 피처가 1 늘면 양성 오즈가 몇 배가 되는가"라는 실무적 해석이 가능하다. 선형 회귀의 계수 해석 가능성이 분류에서도 이어지는 셈이며, 다만 [6장](/study/supervised-learning/06-linear-regression)에서 본 다중공선성의 함정은 여기서도 그대로 적용된다.

```python
from sklearn.linear_model import LogisticRegression

model = LogisticRegression()
model.fit(X_train_scaled, y_train)
model.predict(X_test_scaled)         # 클래스 (0/1)
model.predict_proba(X_test_scaled)   # 확률 [P(0), P(1)]
```

## 4. 정규화 — C 파라미터

로지스틱 회귀도 [6장](/study/supervised-learning/06-linear-regression)처럼 과적합을 막기 위해 정규화하며, sklearn의 `LogisticRegression`은 <strong>기본으로 L2 정규화가 켜져 있다</strong>. 다만 강도를 조절하는 파라미터가 릿지의 `alpha`가 아니라 <strong>`C`</strong>이고, 둘은 <strong>역수 관계</strong>다.

- `C`가 <strong>작으면</strong> 정규화가 <strong>강하다</strong> — 계수를 강하게 억제, 단순한 경계, 편향↑ 분산↓.
- `C`가 <strong>크면</strong> 정규화가 <strong>약하다</strong> — 데이터에 더 맞춤, 복잡한 경계, 과적합 위험↑.

`penalty="l1"`을 주면 라쏘처럼 일부 계수를 0으로 만들어 피처 선택도 된다. `C` 역시 [4장 교차 검증](/study/supervised-learning/04-cross-validation-tuning)으로 고르고, 정규화가 걸리는 이상 [스케일링](/study/supervised-learning/05-knn)이 전제다.

```python
# C가 작을수록 정규화 강함 (alpha와 역수 관계)
LogisticRegression(C=0.1, penalty="l2").fit(X_train_scaled, y_train)
LogisticRegression(C=1.0, penalty="l1", solver="liblinear").fit(X_train_scaled, y_train)
```

## 5. 다중 클래스 전략

지금까지는 양성/음성 2개 클래스였다. 3개 이상은 어떻게 다룰까. 전략은 세 가지이며, 이는 로지스틱 회귀만의 이야기가 아니라 <strong>본질적으로 이진 분류기인 모델(SVM 등)을 다중 클래스로 확장하는 일반 기법</strong>이기도 하다.

- <strong>소프트맥스(다항 로지스틱, multinomial)</strong> — 시그모이드를 여러 클래스로 일반화한 <strong>소프트맥스</strong>로 <strong>단일 모델</strong>이 모든 클래스의 확률을 한 번에 내놓는다. 출력들의 합은 항상 1인 확률 분포다. 로지스틱 회귀의 자연스러운 확장이라 sklearn 기본값이다.
- <strong>OvR(One-vs-Rest, 일대다)</strong> — "클래스 A vs 나머지 전부"처럼 클래스 수 `K`만큼 <strong>이진 분류기</strong>를 만들고, 각 분류기 점수가 가장 높은 클래스를 택한다. 분류기가 `K`개라 단순하고 널리 쓰인다.
- <strong>OvO(One-vs-One, 일대일)</strong> — 모든 클래스 <strong>쌍</strong>마다 이진 분류기를 만들어(`K(K-1)/2`개) 다수결로 정한다. 분류기 수는 많지만 각 분류기가 두 클래스만 보므로, SVM처럼 큰 데이터에 민감한 모델에서 유리할 때가 있다.

![세 가지 다중 클래스 전략(3클래스 A/B/C 예시). 소프트맥스는 단일 모델이 P(A)·P(B)·P(C)를 합 1인 확률 분포로 한 번에 내놓고, OvR은 'A vs 나머지'·'B vs 나머지'·'C vs 나머지' 분류기 K개로 최고 점수를 택하며, OvO는 'A vs B'·'A vs C'·'B vs C' 쌍별 분류기의 다수결로 정한다](/images/study-supervised-learning/07-multiclass-light.png)
![세 가지 다중 클래스 전략(3클래스 A/B/C 예시). 소프트맥스는 단일 모델이 P(A)·P(B)·P(C)를 합 1인 확률 분포로 한 번에 내놓고, OvR은 'A vs 나머지'·'B vs 나머지'·'C vs 나머지' 분류기 K개로 최고 점수를 택하며, OvO는 'A vs B'·'A vs C'·'B vs C' 쌍별 분류기의 다수결로 정한다](/images/study-supervised-learning/07-multiclass-dark.png)

```python
# sklearn은 다중 클래스를 자동 처리(기본 multinomial=소프트맥스)
LogisticRegression().fit(X_train_scaled, y_train_multi)

# 전략을 명시적으로 감싸고 싶을 때
from sklearn.multiclass import OneVsRestClassifier, OneVsOneClassifier
OneVsRestClassifier(LogisticRegression()).fit(X_train_scaled, y_train_multi)
```

로지스틱 회귀 자체는 소프트맥스가 자연스럽고 잘 보정된 확률을 주므로 기본값을 그대로 쓰면 된다. OvR·OvO 래퍼가 진가를 발휘하는 쪽은 오히려 확률 분포를 직접 내놓지 않는 SVM 같은 모델을 다중 클래스로 확장할 때다 — 전략과 모델을 분리해 조합할 수 있다는 점이 이 래퍼들의 핵심이다.

## 6. 확률 출력과 베이스라인으로서의 가치

로지스틱 회귀의 큰 실무 가치는 <strong>잘 보정된 확률</strong>을 준다는 점이다. 단순히 "양성/음성"이 아니라 "양성일 확률 0.82"를 내놓으므로, 상황에 맞춰 <strong>임계값</strong>을 0.5가 아닌 다른 값으로 조정할 수 있다. 사기 탐지처럼 놓치면 치명적인 문제는 임계값을 낮춰 재현율을 올리고, 반대로 오탐 비용이 크면 임계값을 높인다.

```python
import numpy as np

proba = model.predict_proba(X_test_scaled)[:, 1]  # 양성 확률
pred_default = (proba >= 0.5)                      # 기본 임계값
pred_recall  = (proba >= 0.3)                      # 임계값 낮춰 재현율↑ (놓침 최소화)
```

이 threshold 조정과 확률 보정은 [17장 불균형 데이터와 캘리브레이션](/study/supervised-learning/17-imbalanced-calibration)에서 본격적으로 다룬다. 확률 품질과 분류 성능을 함께 보려면 [3장](/study/supervised-learning/03-evaluation-metrics)의 ROC/PR 곡선과 log loss를 쓴다.

마지막으로 로지스틱 회귀는 어떤 분류 문제든 <strong>가장 먼저 세우는 베이스라인</strong>으로서 가치가 크다. 빠르게 학습되고, 계수로 대략적 해석이 되며, 확률까지 준다. 복잡한 GBDT를 붙이기 전에 로지스틱 회귀 점수를 먼저 재두면, 이후 모델이 정말 값어치를 하는지 판단하는 기준선이 생긴다 — [19장 모델 선택 가이드](/study/supervised-learning/19-model-selection-guide)의 출발점도 여기다.

::: tip 핵심 정리
- 로지스틱 회귀는 선형 출력 `z`를 시그모이드에 통과시켜 0~1 확률로 바꾸는 <strong>분류</strong> 모델이다.
- 손실은 로그 손실(크로스엔트로피)로, 정답 클래스에 높은 확률을 주도록 학습하며 확신에 찬 오답에 큰 벌점을 준다.
- 확률 0.5가 되는 지점이 경계라 <strong>결정 경계는 선형</strong>이다 — 복잡한 경계는 다항 피처·커널·트리로 넘어간다.
- 정규화 강도는 `C`로 조절하며 `alpha`와 <strong>역수 관계</strong>다(작을수록 강한 정규화). 기본은 L2.
- 다중 클래스는 소프트맥스(단일 다항)·OvR·OvO로 풀며, OvR/OvO는 SVM 등 다른 이진 분류기에도 쓰이는 일반 전략이다.
- 잘 보정된 확률을 주어 임계값 조정이 가능하고, 빠르고 해석 가능한 <strong>베이스라인</strong>으로서 가치가 크다.
:::

## 다음 챕터

로지스틱 회귀의 결정 경계는 선형이다. [SVM](/study/supervised-learning/08-svm)에서는 경계를 "여백(마진)이 가장 넓게" 긋는다는 다른 관점과, 커널 트릭으로 비선형 경계를 다루는 방법을 살펴본다.
