---
title: "그래디언트 부스팅 원리"
description: "AdaBoost의 가중치 재조정에서 GBM의 잔차 학습으로 넘어가는 흐름을 짚고, 이전 모델이 틀린 만큼을 다음 트리가 배운다는 직관과 이를 손실의 음의 그래디언트를 회귀 트리로 근사하는 함수 공간 경사하강으로 일반화한다. 학습률(shrinkage)과 트리 수의 트레이드오프, 임의 미분가능 손실로의 확장, 서브샘플링(stochastic GB), 그리고 배깅과 달리 트리를 늘리면 과적합할 수 있다는 부스팅의 특성을 정리한다."
date: 2026-07-03
tags: [Machine Learning, Supervised Learning, Gradient Boosting, GBM, Boosting, AdaBoost]
prev: /study/supervised-learning/12-random-forest
next: /study/supervised-learning/14-xgboost-lightgbm-catboost
---

# 그래디언트 부스팅 원리

::: info 학습 목표
- AdaBoost의 샘플 가중치 재조정에서 GBM의 잔차 학습으로 넘어가는 흐름을 이해한다.
- "이전 모델이 틀린 만큼을 다음 트리가 배운다"는 잔차 학습의 직관을 설명한다.
- 잔차 학습을 손실의 음의 그래디언트를 회귀 트리로 근사하는 <strong>함수 공간 경사하강</strong>으로 일반화해 이해한다.
- 학습률(shrinkage)과 트리 수의 트레이드오프를 안다.
- 임의의 미분가능 손실로 회귀·분류·랭킹까지 일반화되는 구조를 파악한다.
- 서브샘플링(stochastic gradient boosting)의 효과와, 배깅과 달리 트리를 늘리면 과적합할 수 있다는 부스팅의 특성을 이해한다.
:::

## 1. AdaBoost에서 GBM으로 — 가중치에서 잔차로

부스팅의 첫 성공작은 AdaBoost(Adaptive Boosting)다. 발상은 단순하다. 약한 학습기(보통 얕은 트리)를 순차적으로 학습하되, <strong>이전 학습기가 틀린 샘플의 가중치를 키워</strong> 다음 학습기가 그 어려운 샘플에 더 집중하게 한다. 맞힌 샘플은 가중치를 줄이고 틀린 샘플은 키우는 식으로 데이터의 관심을 옮겨 가며, 각 학습기의 발언권(정확도)에 비례한 가중치로 최종 예측을 합친다.

AdaBoost는 "틀린 샘플에 집중한다"는 부스팅의 정신을 <strong>샘플 가중치 재조정</strong>으로 구현한 셈이다. 그런데 이 방식은 손실 함수가 지수 손실(exponential loss)로 고정되어 있어, 다른 문제(회귀, 다른 손실)로 확장하기가 번거롭다.

그래디언트 부스팅(GBM, Gradient Boosting Machine)은 같은 "틀린 부분에 집중한다"는 목표를 <strong>가중치 대신 잔차(residual)</strong>로 달성한다. 샘플에 가중치를 매기는 대신, 이전 모델이 얼마나 <strong>틀렸는지 그 오차 자체를 새로운 목표값으로 삼아</strong> 다음 트리를 학습시킨다. 이 관점의 전환 — 가중치 → 잔차 — 이 GBM을 훨씬 유연하게 만든다. 2절과 3절에서 그 이유를 본다.

두 방식의 대비를 한 줄로 정리하면 이렇다.

- <strong>AdaBoost</strong> — "어려운 샘플의 <strong>가중치</strong>를 키운다". 손실이 지수 손실로 고정되어 확장이 제한적이다.
- <strong>GBM</strong> — "남은 <strong>잔차</strong>를 다음 트리의 목표값으로 삼는다". 손실만 미분가능하면 어떤 문제로든 확장된다(5절).

## 2. 잔차 학습의 직관

그래디언트 부스팅의 핵심 아이디어는 한 문장으로 요약된다. <strong>"이전 모델이 틀린 만큼(잔차)을 다음 트리가 배운다."</strong>

![잔차 학습의 흐름 — 초기 예측 F0(평균)에서 잔차 r1=y-F0을 구하고 트리 h1이 r1을 근사하며, 다시 잔차 r2=y-F1을 구해 트리 h2가 r2를 근사하는 식으로, 각 트리는 학습률 만큼만 더해져 F0+η·h1+η·h2+… 로 틀린 만큼만 계속 메워 나간다](/images/study-supervised-learning/13-residual-learning-light.png)
![잔차 학습의 흐름 — 초기 예측 F0(평균)에서 잔차 r1=y-F0을 구하고 트리 h1이 r1을 근사하며, 다시 잔차 r2=y-F1을 구해 트리 h2가 r2를 근사하는 식으로, 각 트리는 학습률 만큼만 더해져 F0+η·h1+η·h2+… 로 틀린 만큼만 계속 메워 나간다](/images/study-supervised-learning/13-residual-learning-dark.png)

회귀 문제로 흐름을 따라가 보자.

1. <strong>초기 예측 $F_0$</strong> — 아주 단순하게 시작한다. 예컨대 모든 샘플에 대해 타깃의 평균을 예측값으로 둔다.
2. <strong>잔차 계산</strong> — 실제값에서 현재 예측을 뺀다: $r_1 = y - F_0$. 이 잔차는 "지금 모델이 각 샘플에서 얼마나, 어느 방향으로 틀렸는가"다.
3. <strong>잔차를 학습</strong> — 새 회귀 트리 $h_1$을 학습하는데, 목표값을 원래 $y$가 아니라 <strong>잔차 $r_1$</strong>으로 둔다. 즉 이 트리는 "앞 모델이 틀린 오차의 패턴"을 배운다.
4. <strong>예측 갱신</strong> — 새 트리를 더한다: $F_1 = F_0 + \eta\, h_1$. 여기서 $\eta$는 학습률로, 트리의 기여를 조금씩만 반영한다(4절).
5. <strong>반복</strong> — 다시 잔차 $r_2 = y - F_1$을 구하고, 트리 $h_2$로 학습하고, 또 더한다. 이를 정해진 트리 수만큼 반복한다.

매 단계 모델은 <strong>아직 남은 오차</strong>에만 집중하므로, 트리를 더할수록 예측이 실제값에 점점 다가간다. AdaBoost가 "어려운 샘플의 가중치"로 관심을 옮겼다면, GBM은 "남은 잔차"라는 새 목표값으로 관심을 옮긴다. 여기서 개별 트리는 [11장 3절](/study/supervised-learning/11-ensemble-basics)의 원칙대로 <strong>얕게(약하게)</strong> 둔다. 편향은 순차 보정이 잡아 주기 때문이다.

초기 예측 $F_0$은 손실을 최소로 만드는 가장 단순한 상수로 둔다 — 회귀(제곱 오차)에서는 타깃의 평균, 분류(로그 손실)에서는 기저 비율의 로그 오즈(log-odds)다. 여기서부터 트리들이 잔차를 한 겹씩 메워 나가는 것이 부스팅의 전체 그림이다.

## 3. 함수 공간 경사하강이라는 관점

잔차 학습은 사실 더 깊은 원리의 특수한 경우다. 그래디언트 부스팅이라는 이름의 "그래디언트"가 여기서 나온다.

일반적인 경사하강법은 파라미터 공간에서 손실을 줄이는 방향(음의 그래디언트)으로 파라미터를 조금씩 움직인다. 그래디언트 부스팅은 이 아이디어를 <strong>함수 공간(function space)</strong>으로 옮긴다. 우리가 갱신하는 대상은 파라미터 벡터가 아니라 <strong>예측 함수 $F$ 자체</strong>다. 매 단계 손실을 가장 빨리 줄이는 방향으로 함수를 조금 움직이고 싶은데, 그 방향이 바로 <strong>손실의 음의 그래디언트</strong>다.

즉 각 샘플에서 계산한 "손실을 현재 예측으로 미분한 음의 값"이 우리가 이번에 근사하고 싶은 목표다. 이걸 pseudo-residual(유사 잔차)이라 부른다. 그리고 이 목표 방향을 데이터 위에서 표현하는 도구로 <strong>회귀 트리</strong>를 쓴다. 트리 하나가 각 샘플의 음의 그래디언트 값을 근사하고, 그 트리를 학습률만큼 더해 함수를 한 걸음 옮긴다.

여기서 2절의 잔차가 특수 경우로 떨어진다. 손실을 제곱 오차 $\frac{1}{2}(y - F)^2$로 두면, 이를 $F$로 미분한 음의 그래디언트는 정확히 $y - F$, 곧 <strong>잔차</strong>다. 그래서 "잔차를 학습한다"는 직관은 "제곱 오차 손실에서 음의 그래디언트를 근사한다"의 다른 말일 뿐이다.

이 관점이 두 가지를 설명해 준다. 첫째, <strong>회귀 트리가 왜 분류에서도 기본 학습기인가</strong>다. 분류라 해도 우리가 매 단계 트리로 근사하는 것은 클래스 라벨이 아니라 <strong>손실의 음의 그래디언트라는 연속값</strong>이다. 연속값을 근사하는 일은 회귀이므로, 분류 문제의 부스팅에서도 각 단계의 약한 학습기는 [10장](/study/supervised-learning/10-decision-tree)의 <strong>회귀 트리</strong>다. 둘째, 손실만 미분가능하면 어떤 문제든 같은 틀로 다룰 수 있다는 점인데, 이는 5절에서 이어진다.

## 4. 학습률과 트리 수의 트레이드오프

4단계에서 새 트리를 더할 때 곱하는 <strong>학습률 $\eta$(shrinkage)</strong>는 그래디언트 부스팅에서 가장 중요한 손잡이 중 하나다. 각 트리의 기여를 $\eta$배로 줄여 조금씩만 반영한다.

왜 굳이 트리 기여를 깎을까. 각 트리를 온전히(예: $\eta=1$) 반영하면 몇 그루 만에 훈련 데이터의 잔차를 지나치게 빠르게 메워 잡음까지 학습하기 쉽다. $\eta$를 작게(예: 0.1, 0.05) 두면 한 걸음 한 걸음이 신중해져, 더 많은 트리를 쌓으며 <strong>천천히 그러나 더 낮은 오차까지</strong> 내려갈 수 있다. 정규화 효과다.

![학습률과 트리 수의 트레이드오프 — 큰 학습률 곡선은 검증 오차가 빠르게 내려가다 일찍 최저점을 찍고 다시 상승해 과적합에 접어드는 반면, 작은 학습률 곡선은 더 천천히 내려가 더 낮은 바닥까지 도달하며, 큰 학습률의 최저점에는 early stopping 지점이 표시되어 있다](/images/study-supervised-learning/13-lr-trees-tradeoff-light.png)
![학습률과 트리 수의 트레이드오프 — 큰 학습률 곡선은 검증 오차가 빠르게 내려가다 일찍 최저점을 찍고 다시 상승해 과적합에 접어드는 반면, 작은 학습률 곡선은 더 천천히 내려가 더 낮은 바닥까지 도달하며, 큰 학습률의 최저점에는 early stopping 지점이 표시되어 있다](/images/study-supervised-learning/13-lr-trees-tradeoff-dark.png)

여기서 학습률($\eta$, `learning_rate`)과 트리 수($M$, `n_estimators`)는 <strong>서로 맞물린다</strong>. $\eta$를 절반으로 줄이면 같은 성능에 도달하기 위해 대략 두 배의 트리가 필요하다. 그래서 실전 감각은 이렇다 — <strong>학습률은 충분히 작게 고정하고, 트리 수는 검증 성능이 더 나아지지 않을 때까지 늘린다.</strong> 작은 학습률 + 많은 트리 조합이 대체로 큰 학습률 + 적은 트리보다 일반화가 좋지만, 그만큼 학습 시간은 길어진다.

트리 수를 얼마로 둘지는 검증셋으로 정한다. 검증 오차가 내려가다 다시 오르기 시작하는 지점에서 멈추는 것이 <strong>early stopping</strong>이며, 부스팅 튜닝의 표준 기법이다([15장](/study/supervised-learning/15-gbdt-tuning)에서 심화).

## 5. 임의 미분가능 손실로 일반화

3절의 함수 공간 관점이 주는 최대 선물은 <strong>일반성</strong>이다. 알고리즘이 손실 함수에 대해 요구하는 것은 오직 하나 — <strong>미분가능할 것</strong>뿐이다. 손실을 예측으로 미분해 음의 그래디언트만 계산할 수 있으면, 그 값을 회귀 트리로 근사하는 나머지 절차는 문제 종류와 무관하게 똑같다.

그래서 손실만 바꿔 끼우면 하나의 틀로 다양한 문제를 푼다.

- <strong>회귀</strong> — 제곱 오차 손실이면 음의 그래디언트가 잔차, 절대 오차나 Huber 손실이면 이상치에 강건한 변형이 된다.
- <strong>분류</strong> — 로그 손실(logistic loss)을 쓰면 음의 그래디언트가 "실제 확률과 예측 확률의 차"에 해당하는 값이 되어, 로짓 공간에서 부스팅한다. 여기서도 각 트리는 회귀 트리다(3절).
- <strong>랭킹</strong> — 순위를 다루는 손실(예: LambdaMART 계열)을 쓰면 검색 결과 정렬 같은 문제도 같은 틀로 학습한다.

이 "손실만 갈아 끼우면 된다"는 성질이 그래디언트 부스팅을 표 형태 데이터의 만능 도구로 만든 결정적 이유다. [14장](/study/supervised-learning/14-xgboost-lightgbm-catboost)의 XGBoost·LightGBM·CatBoost도 모두 이 틀 위에서 손실·근사·구현을 정교화한 것이다.

한 가지 덧붙이면, 지금까지 설명한 표준 GBM은 손실의 <strong>1차 그래디언트</strong>만 쓴다. [14장](/study/supervised-learning/14-xgboost-lightgbm-catboost)에서 볼 XGBoost는 여기에 <strong>2차 미분(헤시안)</strong>까지 동원해 각 단계의 근사를 더 정확하게 만든다. 원리의 뼈대는 같되, 함수 공간에서 한 걸음의 방향과 크기를 더 정밀하게 잡는 개선이라고 보면 된다.

## 6. 서브샘플링과 부스팅의 과적합 특성

<strong>서브샘플링(stochastic gradient boosting)</strong>은 각 트리를 학습할 때 전체 데이터가 아니라 <strong>매번 무작위로 뽑은 일부 샘플</strong>(예: 80%)만 쓰는 기법이다(`subsample<1.0`). 트리마다 보는 데이터가 조금씩 달라져 트리 간 상관이 낮아지고, 이는 [12장](/study/supervised-learning/12-random-forest)의 무작위성처럼 약간의 정규화와 분산 감소 효과를 준다. 학습 속도도 빨라진다. 피처 서브샘플링(`colsample`)도 비슷한 취지로 함께 쓰인다.

한 가지 오해를 짚어 둔다. 서브샘플링은 부트스트랩(복원 추출로 원본 크기만큼)이 아니라 <strong>복원 없이 일부만</strong> 뽑는다는 점, 그리고 무작위성을 주더라도 트리는 여전히 <strong>순차적으로 앞의 잔차를 보정하며</strong> 쌓인다는 점에서 랜덤 포레스트의 병렬 배깅과 근본적으로 다르다. 부스팅은 이 순차 의존성 때문에 트리 학습을 서로 독립적으로 병렬화하기 어렵다.

마지막으로 [11장](/study/supervised-learning/11-ensemble-basics)에서 예고한 부스팅의 핵심 특성을 못박아 둔다. <strong>부스팅은 배깅과 달리 트리를 늘리면 과적합할 수 있다.</strong>

[12장 3절](/study/supervised-learning/12-random-forest)에서 랜덤 포레스트는 트리를 아무리 늘려도 과적합하지 않는다고 했다. 배깅은 독립적인 예측을 평균해 분산만 줄이므로, 트리를 더해도 훈련 데이터에 더 들러붙지 않기 때문이다. 부스팅은 정반대다. 매 트리가 <strong>남은 잔차를 계속 메우도록 순차적으로 쌓이므로</strong>, 트리를 많이 넣으면 신호를 다 학습한 뒤에는 훈련 데이터의 잡음까지 학습해 검증 오차가 다시 오른다(4절 그림의 큰 학습률 곡선). 그래서 부스팅에서 트리 수는 랜덤 포레스트처럼 "많을수록 안전한 값"이 아니라 <strong>과적합을 좌우하는 규제 손잡이</strong>이며, 학습률·서브샘플링·early stopping과 함께 신중히 조절해야 한다.

간단한 sklearn 예제로 전체 그림을 확인한다.

```python
from sklearn.datasets import make_regression
from sklearn.model_selection import train_test_split
from sklearn.ensemble import GradientBoostingRegressor

X, y = make_regression(n_samples=2000, n_features=20, noise=15, random_state=0)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.3, random_state=0)

gb = GradientBoostingRegressor(
    n_estimators=500,     # 트리 수 — 부스팅에선 과적합 손잡이
    learning_rate=0.05,   # 학습률 — 작게 두고 트리로 보완
    max_depth=3,          # 얕은 약한 학습기
    subsample=0.8,        # 서브샘플링(stochastic GB)
    random_state=0,
)
gb.fit(Xtr, ytr)
print("train R2:", round(gb.score(Xtr, ytr), 3))
print("test  R2:", round(gb.score(Xte, yte), 3))
```

`n_estimators`를 과하게 키우거나 `learning_rate`를 함께 크게 두면 train 점수는 계속 오르는데 test 점수는 정체하거나 떨어지는 과적합을 관찰할 수 있다. 이 손잡이들의 상호작용과 실전 튜닝 순서는 [15장](/study/supervised-learning/15-gbdt-tuning)에서 다룬다.

참고로 sklearn에는 위 `GradientBoostingRegressor` 외에 히스토그램 기반으로 훨씬 빠른 `HistGradientBoostingRegressor`/`Classifier`도 있다. 원리는 같지만 연속 피처를 구간(bin)으로 나눠 분할 후보를 줄이는 최적화가 들어가 있어, 데이터가 크면 이쪽이 실용적이다. 이 히스토그램 기법과 그 밖의 현대적 개선은 [14장](/study/supervised-learning/14-xgboost-lightgbm-catboost)에서 본격적으로 다룬다.

::: tip 핵심 정리
- AdaBoost가 틀린 샘플의 <strong>가중치</strong>로 관심을 옮긴다면, GBM은 이전 모델의 <strong>잔차</strong>를 새 목표값으로 삼아 다음 트리를 학습한다.
- 잔차 학습의 직관은 "이전 모델이 틀린 만큼을 다음 트리가 배운다"이며, 개별 트리는 얕게(약하게) 둔다.
- 이는 손실의 <strong>음의 그래디언트를 회귀 트리로 근사</strong>하는 함수 공간 경사하강의 특수 경우다. 제곱 오차의 음의 그래디언트가 곧 잔차이며, 그래서 분류에서도 학습기는 회귀 트리다.
- 학습률은 작게 고정하고 트리 수를 늘리는 조합이 일반화에 유리하며, early stopping으로 트리 수를 정한다.
- 손실만 미분가능하면 회귀·분류·랭킹을 같은 틀로 푼다.
- 서브샘플링은 약한 정규화와 분산 감소를 주고, 부스팅은 배깅과 달리 트리를 늘리면 과적합할 수 있어 트리 수가 규제 손잡이가 된다.
:::

## 다음 챕터

그래디언트 부스팅의 원리를 실전에서 극한까지 끌어올린 것이 현대 GBDT 라이브러리다. [XGBoost·LightGBM·CatBoost](/study/supervised-learning/14-xgboost-lightgbm-catboost)에서는 2차 근사, 히스토그램 기반 분할, GOSS/EFB, ordered boosting 같은 각 라이브러리의 핵심 아이디어와 차이를 비교한다.
