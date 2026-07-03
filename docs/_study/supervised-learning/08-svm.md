---
title: "SVM"
description: "서포트 벡터 머신(SVM)을 마진 최대화 직관, soft margin과 C, 커널 트릭의 아이디어로 정리하고, 스케일링 필수·확률 출력이 기본이 아니라는 실무 주의점과 GBDT·로지스틱 회귀 대비 현재 포지션까지 짚는다."
date: 2026-07-03
tags: [Machine Learning, Supervised Learning, SVM, scikit-learn]
prev: /study/supervised-learning/07-logistic-regression
next: /study/supervised-learning/09-naive-bayes
---

# SVM

::: info 학습 목표
- SVM이 마진을 최대화하는 결정 경계를 찾는다는 직관과, 서포트 벡터만이 그 경계를 정한다는 사실을 이해한다.
- soft margin과 규제 파라미터 C가 무엇을 조절하는지 안다.
- 커널 트릭이 고차원 매핑을 내적으로 대체하는 아이디어라는 점을 파악한다.
- SVM에 스케일링이 필수이고, 확률 출력이 기본이 아니라는 실무 주의점을 익힌다.
- 현재 SVM의 실무 포지션과, 그럼에도 알아야 하는 이유를 정리한다.
:::

## 1. 마진 최대화 — 서포트 벡터가 경계를 정한다

두 클래스를 나누는 직선(고차원에서는 초평면)은 무수히 많다. <strong>SVM(Support Vector Machine)</strong>은 그중 <strong>마진(margin)</strong>, 즉 결정 경계와 가장 가까운 데이터 사이의 간격을 가장 크게 만드는 경계를 고른다. 경계에서 멀찍이 떨어진 여유가 큰 분류기일수록 새 데이터에도 잘 일반화된다는 것이 핵심 직관이다.

여기서 결정적인 점은 이 경계를 정하는 데 <strong>경계에 가장 가까운 소수의 점만</strong> 관여한다는 것이다. 이 점들을 <strong>서포트 벡터(support vector)</strong>라 부른다. 마진 안쪽 경계 위에 놓인 이 점들이 초평면의 위치와 방향을 결정하고, 나머지 멀리 있는 점들은 아무리 많아도 경계에 영향을 주지 않는다. 그래서 SVM은 데이터 개수보다 경계 근처의 구조에 민감한 모델이다.

![SVM 마진 최대화 — 두 클래스 사이에서 마진(점선 경계 사이 간격)을 최대로 하는 결정 경계(실선)를 찾으며, 마진 위에 놓인 소수의 서포트 벡터만이 경계를 결정한다](/images/study-supervised-learning/08-margin-light.png)
![SVM 마진 최대화 — 두 클래스 사이에서 마진(점선 경계 사이 간격)을 최대로 하는 결정 경계(실선)를 찾으며, 마진 위에 놓인 소수의 서포트 벡터만이 경계를 결정한다](/images/study-supervised-learning/08-margin-dark.png)

## 2. Soft margin과 C

현실 데이터는 두 클래스가 깔끔하게 나뉘지 않고 섞여 있는 경우가 많다. 완벽하게 나누는 경계를 고집하면 노이즈 하나에 경계가 크게 휘어져 과적합된다. 그래서 SVM은 일부 오분류나 마진 침범을 허용하는 <strong>soft margin</strong>을 쓴다.

이 허용 정도를 조절하는 것이 규제 파라미터 <strong>C</strong>다. C가 크면 오분류에 큰 벌점을 매겨 훈련 데이터를 최대한 맞히려 하고(마진이 좁아지고 과적합 위험이 커진다), C가 작으면 마진을 넓게 두는 대신 오분류를 더 관대하게 허용한다(과소적합 쪽으로 간다). C는 결국 [편향-분산 트레이드오프](/study/supervised-learning/02-generalization-overfitting)를 조절하는 손잡이이므로 교차 검증으로 정한다.

## 3. 커널 트릭 — 고차원 매핑을 내적으로 대체

직선으로 나눌 수 없는 데이터도 더 높은 차원으로 올리면 초평면으로 나뉘는 경우가 있다. 예를 들어 1차원에서 안쪽·바깥쪽으로 섞인 데이터는 `x`를 `(x, x²)`로 매핑하면 2차원에서 직선 하나로 갈라진다.

문제는 고차원으로 실제로 매핑하면 계산 비용이 폭발한다는 것이다. <strong>커널 트릭(kernel trick)</strong>은 이 고차원 매핑을 명시적으로 계산하지 않고, 두 점의 <strong>내적</strong>만 커널 함수로 대체해 같은 효과를 낸다. 대표적으로 <strong>RBF 커널(가우시안 커널)</strong>은 두 점의 거리가 가까울수록 큰 값을 주어, 사실상 무한 차원 공간에서의 분리를 흉내 낸다. 선형으로 안 되면 `kernel="rbf"`가 기본 출발점이다.

![커널 트릭 — 원 공간(1D)에서 직선 하나로 못 나누는 데이터를 φ(x)=(x, x²)로 특징 공간(2D)에 매핑하면 초평면(직선)으로 선형 분리되며, 실제 매핑 대신 내적만 커널로 대체한다](/images/study-supervised-learning/08-kernel-trick-light.png)
![커널 트릭 — 원 공간(1D)에서 직선 하나로 못 나누는 데이터를 φ(x)=(x, x²)로 특징 공간(2D)에 매핑하면 초평면(직선)으로 선형 분리되며, 실제 매핑 대신 내적만 커널로 대체한다](/images/study-supervised-learning/08-kernel-trick-dark.png)

RBF 커널은 C와 함께 `gamma`라는 파라미터를 갖는다. `gamma`는 하나의 점이 미치는 영향 범위를 정한다 — 크면 각 점의 영향이 좁아져 경계가 구불구불해지고(과적합), 작으면 경계가 매끄러워진다. C와 `gamma`는 함께 튜닝한다.

## 4. 실무 주의점

<strong>스케일링은 필수다.</strong> SVM은 거리와 내적에 기반하므로 특징의 스케일이 다르면 값이 큰 특징이 경계를 지배한다. 반드시 [표준화](/study/supervised-learning/05-knn) 같은 스케일링을 먼저 적용한다.

<strong>확률 출력이 기본이 아니다.</strong> SVM은 본래 확률이 아니라 경계까지의 부호 있는 거리를 낸다. `predict_proba`를 쓰려면 `probability=True`로 별도 보정(Platt scaling)을 거쳐야 하고, 이 값도 그대로 신뢰하긴 어렵다. 다중 클래스는 기본적으로 [one-vs-one 등의 전략](/study/supervised-learning/07-logistic-regression)으로 확장된다.

```python
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

# 스케일링 → SVM 을 파이프라인으로 묶어 leakage 를 막는다
clf = make_pipeline(
    StandardScaler(),
    SVC(kernel="rbf", C=1.0, gamma="scale"),  # 비선형이면 rbf 가 출발점
)
clf.fit(X_train, y_train)
print(clf.score(X_test, y_test))
```

대규모 데이터에서는 커널 SVM의 학습 비용이 샘플 수의 제곱 이상으로 커져 느리다. 선형 SVM이면 `LinearSVC`가 훨씬 빠르고, 데이터가 아주 크면 SVM 자체가 부적합할 수 있다.

## 5. 실무 포지션 — 그래도 알아야 하는 이유

SVM은 한때 중소규모 데이터, 특히 고차원 희소 데이터(텍스트 분류 등)에서 최강의 분류기였다. 지금은 표 형태 데이터에서 [GBDT](/study/supervised-learning/13-gradient-boosting)에, 확률과 해석·확장성이 필요한 문제에서 [로지스틱 회귀](/study/supervised-learning/07-logistic-regression)에 밀리는 경우가 많다. 대규모·확률 요구·튜닝 편의 어느 쪽에서도 우위를 잃었기 때문이다.

그럼에도 알아야 하는 이유는, 마진 최대화·서포트 벡터·커널 트릭이라는 개념이 머신러닝 전반의 기초 어휘이고, 샘플이 적고 차원이 높은 특정 상황에서는 여전히 강력한 베이스라인이기 때문이다.

::: tip 핵심 정리
- SVM은 마진(경계와 가장 가까운 점 사이 간격)을 최대화하는 초평면을 찾고, 그 경계는 소수의 서포트 벡터만으로 결정된다.
- soft margin은 오분류·마진 침범을 허용하며, 규제 파라미터 C가 그 허용 정도(편향-분산)를 조절한다.
- 커널 트릭은 고차원 매핑을 내적으로 대체하는 아이디어이고, 비선형 문제의 출발점은 RBF 커널(C·gamma 튜닝)이다.
- 스케일링은 필수이며, 확률 출력은 기본이 아니라 별도 보정이 필요하고 그마저 신뢰도가 낮다.
- 현재는 GBDT·로지스틱 회귀에 밀리는 경우가 많지만, 소규모·고차원 상황의 베이스라인이자 핵심 개념으로 알아둘 가치가 있다.
:::

## 다음 챕터

SVM이 기하학적 마진으로 분류했다면, [나이브 베이즈](/study/supervised-learning/09-naive-bayes)는 확률로 분류한다. 베이즈 정리와 조건부 독립 가정으로 만든 초고속 베이스라인이 어떻게, 그리고 왜 텍스트 분류에서 여전히 강한지 살펴본다.
