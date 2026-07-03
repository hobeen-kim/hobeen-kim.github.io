---
title: "앙상블 기초"
description: "왜 약한 모델 여럿이 강한 하나를 이기는가를 오류의 독립성에서 출발해 설명하고, 배깅과 부스팅을 편향-분산 관점으로 재방문한다. 배깅=분산 감소, 부스팅=편향 감소라는 축으로 두 계열을 나누고, 스태킹·보팅 개요와 다양성(diversity)이 앙상블의 핵심이라는 원리, 그리고 불안정한 트리가 앙상블의 기본 학습기로 애용되는 이유를 정리한다."
date: 2026-07-03
tags: [Machine Learning, Supervised Learning, Ensemble, Bagging, Boosting, Stacking]
prev: /study/supervised-learning/10-decision-tree
next: /study/supervised-learning/12-random-forest
---

# 앙상블 기초

::: info 학습 목표
- 약한 모델 여럿을 모으면 강한 하나를 이기는 이유를 오류의 독립성으로 설명할 수 있다.
- 배깅과 부스팅을 [02장의 편향-분산 트레이드오프](/study/supervised-learning/02-generalization-overfitting) 관점에서 재방문해, 배깅은 분산을, 부스팅은 편향을 줄인다는 축으로 구분한다.
- 배깅(부트스트랩+집계)과 부스팅(순차적 오류 보정)의 작동 구조 차이를 안다.
- 스태킹과 보팅의 개요를 파악하고 언제 쓰는지 감을 잡는다.
- 앙상블의 성패를 가르는 것이 정확도가 아니라 다양성(diversity)이라는 원리를 이해한다.
- 불안정한 결정 트리가 오히려 앙상블의 기본 학습기로 애용되는 이유를 안다.
:::

## 1. 왜 약한 모델 여럿이 강한 하나를 이기는가

앙상블(ensemble)은 여러 모델의 예측을 결합해 하나의 예측을 만드는 방법이다. 직관적으로는 이상하다. 각자 그저 그런 모델을 여럿 모은다고 어떻게 더 좋아진단 말인가. 답은 <strong>오류의 독립성</strong>에 있다.

동전 던지기에 비유하면 쉽다. 정답을 51% 확률로 맞히는 모델 하나는 거의 찍기 수준이다. 그런데 이런 모델을 <strong>서로 다른 실수를 하는</strong> 여러 개 모아 다수결로 결정하면, 개별 모델이 동시에 틀릴 확률은 급격히 낮아진다. 51%짜리 분류기가 서로 독립적으로 틀린다면, 이를 여럿 모아 투표할 때 전체 정확도는 51%보다 훨씬 높은 곳으로 수렴한다. 큰 수의 법칙이 오류를 상쇄해 주기 때문이다.

핵심 조건은 두 가지다. 개별 모델이 <strong>무작위 찍기보다는 나아야</strong> 하고(약하더라도 신호는 담고 있어야 하고), 서로의 실수가 <strong>겹치지 않아야</strong> 한다. 모두가 똑같은 곳에서 틀리면 아무리 많이 모아도 그 실수는 그대로 남는다. 그래서 앙상블 설계의 본질은 "정확한 모델을 만드는 것"이 아니라 "서로 다르게 틀리는 모델을 만드는 것"이다. 이 점은 6절에서 다시 강조한다.

같은 논리를 [02장](/study/supervised-learning/02-generalization-overfitting)의 언어로 바꾸면, 서로 독립적인 예측을 여럿 평균 낼 때 그 <strong>평균의 분산이 줄어드는</strong> 통계적 사실이다. 예측값 하나하나는 참값 주위에서 출렁이지만, 독립적인 출렁임을 평균하면 서로 상쇄되어 흔들림이 잦아든다. 다만 이 상쇄는 예측들이 서로 상관되어 있으면 그만큼 약해진다 — 그래서 다양성이 곧 앙상블의 연료다.

## 2. 두 갈래 — 배깅과 부스팅

앙상블을 만드는 방식은 크게 두 갈래로 나뉜다. 여러 모델을 <strong>서로 독립적으로 병렬 학습</strong>시켜 평균 내는 배깅(bagging), 그리고 <strong>순차적으로 앞 모델의 오류를 보정</strong>하며 쌓는 부스팅(boosting)이다.

![배깅과 부스팅의 구조 비교 — 왼쪽 배깅은 서로 다른 부트스트랩 표본으로 트리들을 병렬·독립 학습해 평균/투표로 집계하고, 오른쪽 부스팅은 트리를 순차로 이어 붙이며 앞 트리의 오류를 다음 트리가 보정한 뒤 가중 합한다](/images/study-supervised-learning/11-bagging-vs-boosting-light.png)
![배깅과 부스팅의 구조 비교 — 왼쪽 배깅은 서로 다른 부트스트랩 표본으로 트리들을 병렬·독립 학습해 평균/투표로 집계하고, 오른쪽 부스팅은 트리를 순차로 이어 붙이며 앞 트리의 오류를 다음 트리가 보정한 뒤 가중 합한다](/images/study-supervised-learning/11-bagging-vs-boosting-dark.png)

<strong>배깅</strong>은 원본 데이터에서 복원 추출로 여러 부트스트랩(bootstrap) 표본을 만들고, 각 표본으로 모델을 하나씩 독립적으로 학습한 뒤, 예측을 평균(회귀)하거나 다수결(분류)로 집계한다. 모델들끼리 서로를 전혀 모른 채 학습되므로 순서가 없고 병렬화가 자연스럽다. 랜덤 포레스트가 대표 주자다([12장](/study/supervised-learning/12-random-forest)).

<strong>부스팅</strong>은 정반대다. 모델을 하나씩 순차적으로 학습하되, 각 단계에서 <strong>지금까지 틀린 부분에 집중</strong>하도록 다음 모델을 만든다. 앞 모델이 놓친 오차를 뒤 모델이 메우는 식으로 약한 학습기를 이어 붙여 강한 예측기를 조립한다. AdaBoost와 그래디언트 부스팅이 대표 주자다([13장](/study/supervised-learning/13-gradient-boosting)).

## 3. 편향-분산 관점으로 재방문

[02장](/study/supervised-learning/02-generalization-overfitting)에서 일반화 오차를 <strong>편향(bias)</strong>과 <strong>분산(variance)</strong>으로 분해했다. 편향은 모델이 너무 단순해 진짜 패턴을 놓치는 정도(과소적합 쪽), 분산은 데이터가 조금만 바뀌어도 예측이 출렁이는 정도(과적합 쪽)다. 배깅과 부스팅은 바로 이 두 축을 각각 공략한다.

![편향-분산 평면 위의 배깅과 부스팅 — 가로축 편향·세로축 분산 평면에서 단일 깊은 트리는 저편향·고분산(좌상단)이라 배깅이 분산을 아래로 내려 랜덤 포레스트가 되고, 얕은 그루터기는 고편향·저분산(우하단)이라 부스팅이 편향을 왼쪽으로 내려 GBDT가 된다](/images/study-supervised-learning/11-bias-variance-view-light.png)
![편향-분산 평면 위의 배깅과 부스팅 — 가로축 편향·세로축 분산 평면에서 단일 깊은 트리는 저편향·고분산(좌상단)이라 배깅이 분산을 아래로 내려 랜덤 포레스트가 되고, 얕은 그루터기는 고편향·저분산(우하단)이라 부스팅이 편향을 왼쪽으로 내려 GBDT가 된다](/images/study-supervised-learning/11-bias-variance-view-dark.png)

<strong>배깅은 분산을 줄인다.</strong> 깊게 자란 결정 트리 하나는 편향은 낮지만 분산이 크다 — 훈련 데이터를 조금만 바꿔도 트리 구조가 확 달라진다. 서로 다른 부트스트랩 표본으로 학습한 여러 트리의 예측을 평균 내면, 각 트리의 출렁임이 서로 상쇄되어 분산이 낮아진다. 독립적인 예측값을 $N$개 평균 내면 그 평균의 분산이 대략 $1/N$로 줄어드는 통계의 기본 성질이 그대로 작동하는 것이다. 편향은 거의 그대로 유지되므로, 배깅은 <strong>저편향·고분산 모델(깊은 트리)을 저편향·저분산으로</strong> 옮긴다.

<strong>부스팅은 편향을 줄인다.</strong> 얕은 트리(때로는 깊이 1의 그루터기, stump) 하나는 표현력이 약해 편향이 크다. 부스팅은 이렇게 편향 높은 약한 학습기를 순차적으로 쌓으면서 매 단계 남은 오차를 조금씩 메워, 전체 모델의 편향을 점점 낮춘다. 결과적으로 <strong>고편향·저분산 모델(얕은 트리)을 저편향으로</strong> 끌어내린다.

그래서 같은 결정 트리를 쓰더라도 배깅과 부스팅은 정반대 방향으로 튜닝한다. 배깅에서는 개별 트리를 <strong>깊고 강하게</strong>(분산은 앙상블이 잡아 준다) 두고, 부스팅에서는 개별 트리를 <strong>얕고 약하게</strong>(편향은 순차 보정이 잡아 준다) 둔다. 이 대비는 [12장](/study/supervised-learning/12-random-forest)과 [13장](/study/supervised-learning/13-gradient-boosting)에서 하이퍼파라미터로 구체화된다.

한 가지 중요한 부작용도 여기서 갈린다. 배깅은 트리를 더 쌓아도 과적합이 심해지지 않는다(분산만 더 줄어들 뿐 수익이 체감할 뿐이다). 반면 부스팅은 트리를 계속 쌓으면 편향을 넘어 훈련 데이터의 잡음까지 학습해 <strong>과적합할 수 있다</strong>. 이 차이는 [13장](/study/supervised-learning/13-gradient-boosting)에서 학습률·트리 수 트레이드오프로 다시 다룬다.

## 4. 배깅 맛보기

sklearn의 `BaggingClassifier`로 배깅의 분산 감소 효과를 바로 확인할 수 있다. 깊은 트리 하나와, 그 트리 여러 개를 배깅한 앙상블을 비교한다.

```python
from sklearn.datasets import make_moons
from sklearn.model_selection import cross_val_score
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import BaggingClassifier

X, y = make_moons(n_samples=500, noise=0.3, random_state=0)

# 깊은 트리 하나 — 저편향·고분산
tree = DecisionTreeClassifier(random_state=0)

# 같은 트리를 200개 배깅 — 분산을 깎는다
bag = BaggingClassifier(
    estimator=DecisionTreeClassifier(random_state=0),
    n_estimators=200, random_state=0, n_jobs=-1,
)

print("단일 트리 :", cross_val_score(tree, X, y, cv=5).mean().round(3))
print("배깅      :", cross_val_score(bag, X, y, cv=5).mean().round(3))
```

개별 트리의 정확도는 그대로여도 배깅 쪽 교차 검증 점수가 더 높고 안정적이다. 편향은 두지 않고 분산만 깎았기 때문이다.

## 5. 부스팅·스태킹·보팅 개요

부스팅의 구조는 [13장](/study/supervised-learning/13-gradient-boosting)에서 잔차 학습으로 깊이 파고들므로 여기서는 갈래만 정리한다. 나머지 두 결합 방식도 개요만 짚는다.

<strong>보팅(voting)</strong>은 가장 단순한 앙상블이다. 서로 <strong>종류가 다른</strong> 모델들(예: 로지스틱 회귀, kNN, 트리)을 각각 학습한 뒤, 다수결(hard voting)이나 예측 확률 평균(soft voting)으로 합친다. 부트스트랩도 순차 보정도 없이 그냥 이질적인 모델을 묶는 방식이라, 서로 다른 관점의 모델을 손쉽게 섞어 볼 때 좋다.

```python
from sklearn.ensemble import VotingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier

vote = VotingClassifier(
    estimators=[
        ("lr", LogisticRegression(max_iter=1000)),
        ("knn", KNeighborsClassifier()),
        ("tree", DecisionTreeClassifier(max_depth=4, random_state=0)),
    ],
    voting="soft",  # 확률 평균
)
```

<strong>스태킹(stacking)</strong>은 한 걸음 더 나아간다. 여러 기반 모델(base learner)의 예측을 <strong>새로운 피처</strong>로 삼아, 그 위에 최종 모델(meta learner)을 하나 더 얹어 "어떤 모델의 예측을 얼마나 믿을지"를 학습시킨다. 보팅이 고정된 규칙(다수결·평균)으로 합친다면, 스태킹은 합치는 방법 자체를 데이터로 배운다. 다만 메타 모델이 leakage 없이 학습되도록, 기반 모델의 예측을 교차 검증 방식으로 만들어 넣는 것이 중요하다([04장](/study/supervised-learning/04-cross-validation-tuning) 참고). sklearn의 `StackingClassifier`는 이 절차를 내부에서 처리한다.

네 방식을 한눈에 정리하면 이렇다.

- <strong>배깅</strong> — 같은 약한 학습기를 부트스트랩 표본으로 병렬 학습 후 집계. 분산을 줄인다.
- <strong>부스팅</strong> — 같은 약한 학습기를 순차로 쌓으며 오류를 보정. 편향을 줄인다.
- <strong>보팅</strong> — 이질적 모델을 고정 규칙(다수결·평균)으로 결합.
- <strong>스태킹</strong> — 이질적 모델의 예측을 피처 삼아 메타 모델이 결합 방법을 학습.

정리하면, 보팅과 스태킹은 <strong>이질적 모델을 결합</strong>하는 데 초점이 있고, 배깅과 부스팅은 <strong>같은 종류의 약한 학습기를 대량으로</strong> 다루는 데 초점이 있다. 실무에서 표 형태 데이터의 주력은 후자, 특히 부스팅 계열(GBDT)이다.

## 6. 다양성이 핵심이다

앙상블의 성패를 가르는 단 하나를 꼽으라면 정확도가 아니라 <strong>다양성(diversity)</strong>이다. 1절의 논리 그대로, 개별 모델이 아무리 정확해도 모두 똑같이 틀리면 앙상블은 그 실수를 조금도 지우지 못한다. 반대로 개별 모델이 약해도 서로 다른 곳에서 틀리면, 결합할 때 오류가 상쇄되어 전체는 강해진다.

그래서 앙상블 기법들은 저마다 <strong>다양성을 일부러 주입</strong>한다. 배깅은 서로 다른 부트스트랩 표본으로, 랜덤 포레스트는 거기에 더해 피처 무작위 선택으로([12장](/study/supervised-learning/12-random-forest)), 부스팅은 매 단계 서로 다른 오차에 집중하게 함으로써 모델들을 서로 다르게 만든다. "각 모델을 최대한 정확하게"가 아니라 "각 모델을 최대한 다르게(그러면서도 찍기보다는 낫게)"가 앙상블의 설계 철학이다.

## 7. 왜 하필 트리인가 — 불안정성이 장점

앙상블의 기본 학습기로는 거의 항상 결정 트리가 쓰인다. 이유는 트리의 약점이 앙상블에서는 오히려 강점이 되기 때문이다.

[10장](/study/supervised-learning/10-decision-tree)에서 봤듯 결정 트리는 <strong>불안정한(unstable)</strong> 모델이다. 훈련 데이터가 조금만 바뀌어도 분할 지점이 달라져 전혀 다른 트리가 나온다. 단일 모델로 쓸 때는 이 높은 분산이 단점이지만, 배깅 관점에서는 정확히 원하는 성질이다. 서로 조금씩 다른 데이터에 노출된 트리들이 <strong>서로 다르게 반응</strong>하니, 곧 다양성이 저절로 확보된다. 선형 회귀처럼 안정적인 모델은 데이터를 조금 바꿔도 거의 같은 결과를 내므로 배깅해도 다양성이 생기지 않아 이득이 적다.

트리는 그 밖에도 앙상블 학습기로서 이점이 많다. 스케일링·정규화가 필요 없고, 수치형과 범주형을 함께 다루며, 피처 간 상호작용을 자동으로 잡고, 얕게 자르면 빠르게 학습되는 약한 학습기가 되고 깊게 두면 강한 학습기가 되어 배깅·부스팅 어느 쪽에도 맞춰 쓸 수 있다. 이 조합 덕분에 트리는 랜덤 포레스트부터 XGBoost까지 거의 모든 실전 앙상블의 표준 부품이 되었다.

::: tip 핵심 정리
- 앙상블이 강한 이유는 개별 모델이 서로 <strong>독립적으로 틀리면</strong> 결합 시 오류가 상쇄되기 때문이다.
- 배깅은 부트스트랩 표본으로 병렬·독립 학습 후 집계하고, 부스팅은 순차적으로 앞 모델의 오류를 보정하며 쌓는다.
- 편향-분산 관점에서 <strong>배깅=분산 감소</strong>(깊은 트리를 평균), <strong>부스팅=편향 감소</strong>(얕은 트리를 순차 보정)로 나뉜다.
- 그래서 배깅은 개별 트리를 깊고 강하게, 부스팅은 얕고 약하게 둔다. 배깅은 트리를 늘려도 과적합하지 않지만 부스팅은 과적합할 수 있다.
- 보팅·스태킹은 이질적 모델을 규칙 또는 학습으로 결합하고, 배깅·부스팅은 같은 약한 학습기를 대량으로 다룬다.
- 앙상블의 핵심은 정확도가 아니라 다양성이며, 불안정한 트리는 다양성을 잘 만들어 내 앙상블의 표준 학습기가 된다.
:::

## 다음 챕터

배깅의 대표 주자를 먼저 파고든다. [랜덤 포레스트](/study/supervised-learning/12-random-forest)에서는 배깅에 피처 무작위성을 더한 이중 무작위화, 공짜 검증셋인 OOB 평가, 그리고 feature importance의 함정까지 다룬다.
