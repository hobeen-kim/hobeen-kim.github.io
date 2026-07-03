---
title: "나이브 베이즈"
description: "나이브 베이즈를 베이즈 정리 기반 분류, 조건부 독립 가정(순진한 이유와 그럼에도 작동하는 이유), Gaussian/Multinomial/Bernoulli 변형과 텍스트 분류에서의 강점, 라플라스 스무딩으로 정리하고, 확률값 자체는 신뢰하기 어렵다는 점과 초고속 베이스라인으로서의 가치를 짚는다."
date: 2026-07-03
tags: [Machine Learning, Supervised Learning, Naive Bayes, scikit-learn]
prev: /study/supervised-learning/08-svm
next: /study/supervised-learning/10-decision-tree
---

# 나이브 베이즈

::: info 학습 목표
- 베이즈 정리로 분류 문제를 어떻게 푸는지 이해한다.
- 조건부 독립 가정이 왜 순진한지, 그런데도 왜 잘 작동하는지 안다.
- Gaussian/Multinomial/Bernoulli 세 변형을 특징 형태에 맞게 고를 수 있다.
- 텍스트 분류(스팸 필터)에서의 강점과 라플라스 스무딩의 역할을 익힌다.
- 나이브 베이즈의 확률값을 그대로 믿으면 안 되는 이유와, 초고속 베이스라인으로서의 가치를 파악한다.
:::

## 1. 베이즈 정리로 분류하기

나이브 베이즈는 "이 입력이 주어졌을 때 어느 클래스일 확률이 가장 큰가"를 <strong>베이즈 정리</strong>로 계산한다. 클래스 `c`와 특징 `x`에 대해 사후확률은 다음에 비례한다.

$$P(c \mid x) \propto P(c)\,P(x \mid c)$$

`P(c)`는 <strong>사전확률</strong>(그 클래스가 나타나는 기본 비율), `P(x|c)`는 <strong>우도</strong>(그 클래스에서 이 입력이 나올 가능성)다. 모든 클래스에 대해 이 값을 구한 뒤 가장 큰 클래스를 예측으로 고른다. 분모(증거 `P(x)`)는 모든 클래스에 공통이라 비교에는 필요 없어 생략한다.

![나이브 베이즈 분류 흐름 — 입력 특징 x에 대해 사전확률 P(c)와 조건부 독립 가정으로 곱한 우도 ∏P(xi|c)를 결합해 사후확률 P(c|x)를 구하고, argmax로 가장 큰 클래스를 예측한다](/images/study-supervised-learning/09-bayes-flow-light.png)
![나이브 베이즈 분류 흐름 — 입력 특징 x에 대해 사전확률 P(c)와 조건부 독립 가정으로 곱한 우도 ∏P(xi|c)를 결합해 사후확률 P(c|x)를 구하고, argmax로 가장 큰 클래스를 예측한다](/images/study-supervised-learning/09-bayes-flow-dark.png)

## 2. 조건부 독립 가정 — 순진하지만 작동한다

문제는 우도 `P(x|c)`, 즉 여러 특징이 동시에 나타날 확률을 그대로 추정하기 어렵다는 것이다. 나이브 베이즈는 여기서 과감한 지름길을 쓴다 — <strong>클래스가 주어지면 모든 특징이 서로 독립</strong>이라고 가정하고, 우도를 각 특징 확률의 곱으로 쪼갠다.

$$P(x \mid c) = \prod_i P(x_i \mid c)$$

이 가정이 "순진한(naive)" 이유는 현실에서 특징들이 대개 서로 연관되기 때문이다. 문서에서 "머신"과 "러닝"은 같이 등장하기 쉬운데 독립으로 취급해버린다. 그런데도 잘 작동하는 이유는, 분류의 목적이 정확한 확률을 구하는 게 아니라 <strong>어느 클래스의 점수가 가장 큰지 순위를 맞히는 것</strong>이기 때문이다. 특징이 중복돼 확률 크기가 왜곡돼도 클래스 간 <strong>대소 관계</strong>는 자주 보존되어, 확률값은 틀려도 예측은 맞는 경우가 많다.

## 3. 세 가지 변형

특징이 어떤 형태냐에 따라 우도 `P(xi|c)`를 다른 분포로 모델링한다. sklearn은 세 변형을 제공한다.

![나이브 베이즈 세 변형 — 연속형 특징에는 정규분포를 가정하는 Gaussian, 단어 등장 횟수 같은 카운트 데이터에는 Multinomial(텍스트 BoW·TF), 특징의 등장 여부(0/1)만 쓰는 Bernoulli를 특징 형태에 맞춰 선택한다](/images/study-supervised-learning/09-variants-light.png)
![나이브 베이즈 세 변형 — 연속형 특징에는 정규분포를 가정하는 Gaussian, 단어 등장 횟수 같은 카운트 데이터에는 Multinomial(텍스트 BoW·TF), 특징의 등장 여부(0/1)만 쓰는 Bernoulli를 특징 형태에 맞춰 선택한다](/images/study-supervised-learning/09-variants-dark.png)

- <strong>GaussianNB</strong> — 연속형 특징. 각 특징이 클래스별로 정규분포를 따른다고 가정한다. 센서 측정값처럼 실수 특징에 쓴다.
- <strong>MultinomialNB</strong> — 횟수·빈도 데이터. 단어 등장 횟수(BoW, TF) 같은 카운트에 맞고, 텍스트 분류의 기본 선택이다.
- <strong>BernoulliNB</strong> — 이진(0/1) 특징. 단어가 등장했는지 여부만 쓰는, 짧은 텍스트에 잘 맞는다.

## 4. 텍스트 분류와 라플라스 스무딩

나이브 베이즈가 가장 빛나는 곳은 <strong>텍스트 분류, 특히 스팸 필터</strong>다. 단어 수만큼 차원이 크고 대부분 0인 고차원 희소 데이터에서, 특징을 독립으로 곱하는 구조가 오히려 빠르고 안정적으로 작동한다. 학습·예측이 지극히 빨라 대량 메일 필터링 같은 곳에 잘 맞는다.

한 가지 함정이 있다. 학습 데이터의 어떤 클래스에서 한 번도 안 나온 단어가 있으면 그 우도가 0이 되고, 곱셈이므로 <strong>전체 확률이 0으로 붕괴</strong>한다. 이를 막는 것이 <strong>라플라스 스무딩(Laplace smoothing)</strong>이다 — 모든 카운트에 작은 값(보통 1)을 더해 0을 없앤다. sklearn에서는 `alpha` 파라미터로 조절하며 기본값이 1.0이다.

```python
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline

# 텍스트 → 카운트 벡터 → MultinomialNB (alpha=1.0 이 라플라스 스무딩)
clf = make_pipeline(
    CountVectorizer(),
    MultinomialNB(alpha=1.0),
)
clf.fit(texts_train, y_train)      # texts_train: 문자열 리스트
print(clf.predict(["free money click now"]))
```

## 5. 확률은 못 믿는다 — 그래도 베이스라인으로 강하다

나이브 베이즈의 <strong>예측(어느 클래스인가)</strong>은 자주 쓸 만하지만, <strong>확률값 자체(0.99 같은 수)</strong>는 신뢰하기 어렵다. 조건부 독립 위반으로 중복 특징의 증거가 과다 계산되어, 확률이 0이나 1 쪽으로 과도하게 쏠리는 경향이 있다. 확률을 임계값 조정이나 리스크 계산에 써야 한다면 별도 보정이 필요하다 — 이 캘리브레이션은 [17장](/study/supervised-learning/17-imbalanced-calibration)에서 다룬다.

정리하면 나이브 베이즈의 가치는 정밀함이 아니라 <strong>속도와 단순함</strong>에 있다. 몇 줄로 붙는 데다 학습이 순식간이라, 새 분류 문제에서 "이보다 잘하는가"를 재는 <strong>초고속 베이스라인</strong>으로 먼저 돌려보기에 이상적이다.

::: tip 핵심 정리
- 나이브 베이즈는 베이즈 정리로 사후확률 P(c|x) ∝ P(c)·P(x|c)를 계산해 가장 큰 클래스를 고른다.
- 조건부 독립 가정은 우도를 각 특징 확률의 곱으로 쪼개며, 순진하지만 클래스 간 순위는 자주 보존되어 예측은 잘 맞는다.
- 특징 형태에 따라 GaussianNB(연속형)·MultinomialNB(카운트)·BernoulliNB(이진)를 고른다.
- 텍스트 분류·스팸 필터에서 강하며, 확률 0 붕괴를 막는 라플라스 스무딩(alpha)이 필수다.
- 확률값 자체는 과신·과소로 치우쳐 신뢰하기 어렵지만(캘리브레이션은 17장), 초고속 베이스라인으로서의 가치가 크다.
:::

## 다음 챕터

지금까지의 모델이 거리·확률·마진으로 분류했다면, [결정 트리](/study/supervised-learning/10-decision-tree)는 규칙을 순서대로 물어 나눈다. 불순도 기반 분할, 회귀 트리, 가지치기를 다루며, 이어질 앙상블(랜덤 포레스트·부스팅)의 토대를 놓는다.
