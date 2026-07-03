---
title: "지도 학습이란"
description: "지도 학습을 입력 X·정답 y·손실 함수로 형식화하고, 회귀와 분류의 차이, 지도·비지도·강화 학습의 경계를 정리한다. 이탈·수요 예측·이상 탐지 같은 실무 문제가 언제 지도 학습이 되는지 판별하고, scikit-learn의 fit/predict 계약을 첫 코드로 확인한다."
date: 2026-07-03
tags: [Machine Learning, Supervised Learning, scikit-learn, Regression, Classification]
prev: /study/supervised-learning/
next: /study/supervised-learning/02-generalization-overfitting
---

# 지도 학습이란

::: info 학습 목표
- 지도 학습을 입력 X, 정답 y, 손실 함수로 형식화할 수 있다.
- 회귀와 분류가 무엇이 같고 무엇이 다른지 출력 공간의 관점에서 구분한다.
- 지도·비지도·강화 학습이 "무엇을 받아 무엇을 최적화하는가"로 갈린다는 것을 이해한다.
- 이탈 예측·수요 예측·이상 탐지 같은 실무 문제가 언제 지도 학습으로 성립하는지 판별한다.
- scikit-learn의 `fit`/`predict` 계약을 첫 코드로 확인한다.
:::

## 1. 지도 학습의 형식화 — X, y, 손실

지도 학습은 한 문장으로 요약된다. <strong>입력과 정답 쌍의 모음에서 입력을 정답으로 옮기는 함수를 찾는 것</strong>이다. 여기서 세 가지 기호만 잡으면 나머지는 모두 이 위에 쌓인다.

- <strong>입력 X</strong> — 특징(feature)들의 행렬이다. 행 하나가 샘플 하나(고객 한 명, 거래 하나)이고, 열 하나가 특징 하나(나이, 결제 금액)다. 보통 `(n_samples, n_features)` 모양의 2차원 배열로 표현한다.
- <strong>정답 y</strong> — 각 샘플에 붙은 목표값(target/label)이다. 샘플 수만큼의 1차원 벡터이며, 이 정답이 존재한다는 점이 지도 학습을 "지도(supervised)"로 만든다.
- <strong>손실 함수 L</strong> — 모델의 예측 `f(x)`가 정답 `y`에서 얼마나 벗어났는지를 숫자 하나로 재는 자다. 학습이란 결국 훈련 데이터 전체에서 이 손실의 평균을 가장 작게 만드는 함수 `f`를 고르는 최적화 문제다.

즉 목표는 임의의 `f`가 아니라, 손실을 최소화하는 `f`다. 회귀에서는 대개 제곱 오차 `(y − f(x))²`, 분류에서는 로그 손실(크로스 엔트로피)을 쓰는데, 어떤 손실을 고르느냐가 "무엇을 잘한다고 볼 것인가"를 정의한다. 손실 선택은 [3장 평가 지표](/study/supervised-learning/03-evaluation-metrics)에서 비즈니스 비용과 연결해 다시 다룬다.

여기서 핵심 함정이 하나 있다. 우리가 진짜 원하는 것은 <strong>훈련 데이터에서의 손실 최소화가 아니라, 본 적 없는 데이터에서의 손실 최소화</strong>다. 훈련 데이터만 완벽히 맞추는 함수는 얼마든지 만들 수 있지만 그건 암기일 뿐이다. 이 간극이 [2장 일반화와 과적합](/study/supervised-learning/02-generalization-overfitting)의 주제다.

## 2. 회귀 vs 분류 — 출력 공간이 가른다

지도 학습 문제는 <strong>정답 y가 어떤 공간에 사는가</strong>로 두 갈래가 된다.

- <strong>회귀(regression)</strong> — y가 연속적인 실수다. 집값(원), 내일 기온(℃), 다음 달 주문량(개)처럼 "얼마나"를 맞힌다. 예측이 정답에 가까울수록 좋고, 크게 빗나갈수록 나쁘다는 <strong>거리</strong> 개념이 자연스럽다.
- <strong>분류(classification)</strong> — y가 유한한 범주다. 스팸/정상, 이탈/유지, 개/고양이/새처럼 "무엇인지"를 맞힌다. 범주 사이엔 거리가 없어서(스팸이 정상보다 "2만큼 크다"는 말은 무의미) 맞았다/틀렸다로 세는 게 기본이다.

둘의 경계는 생각보다 미묘하다. 별점(1~5)은 숫자지만 순서만 있는 서열형이라 순수 회귀로도 순수 분류로도 딱 떨어지지 않고, 확률을 예측하는 분류기는 사실상 [0, 1] 구간의 회귀를 푸는 것과 닮았다. 그래서 <strong>같은 비즈니스 질문도 y를 어떻게 정의하느냐에 따라 회귀가 되기도 분류가 되기도 한다.</strong> "이 고객이 이번 달에 얼마를 쓸까"는 회귀지만, "이 고객이 이번 달에 결제할까"는 분류다.

## 3. 지도 · 비지도 · 강화 학습

머신러닝의 세 패러다임은 "무엇을 입력으로 받고, 무엇을 최적화하는가"로 갈린다.

![지도·비지도·강화 학습 비교 — 지도 학습은 입력 X와 정답 y를 받아 오차를 최소화하고, 비지도 학습은 정답 없는 X만으로 구조를 발견하며, 강화 학습은 상태와 보상 신호를 받아 누적 보상을 최대화한다](/images/study-supervised-learning/01-learning-paradigms-light.png)
![지도·비지도·강화 학습 비교 — 지도 학습은 입력 X와 정답 y를 받아 오차를 최소화하고, 비지도 학습은 정답 없는 X만으로 구조를 발견하며, 강화 학습은 상태와 보상 신호를 받아 누적 보상을 최대화한다](/images/study-supervised-learning/01-learning-paradigms-dark.png)

- <strong>지도 학습</strong> — 정답 y가 붙은 데이터로 입력→출력 함수를 배운다. 정답이 명확한 만큼 성능도 "얼마나 정답에 가까운가"로 깔끔하게 잰다. 이 스터디의 전 범위다.
- <strong>비지도 학습(unsupervised)</strong> — 정답 없이 입력 X만 주고 데이터의 숨은 구조를 찾게 한다. 비슷한 것끼리 묶는 군집화(clustering), 차원을 줄이는 차원 축소(PCA 등)가 대표적이다. "정답"이 없으니 잘했는지 판단하는 기준도 지도 학습만큼 명확하지 않다.
- <strong>강화 학습(reinforcement)</strong> — 환경과 상호작용하며 상태를 관찰하고 행동한 뒤 보상을 받는다. 목표는 즉각적 정답이 아니라 <strong>장기 누적 보상의 최대화</strong>다. 로봇 제어, 게임 AI, 순차적 의사결정에 쓰인다.

실무 표(tabular) 데이터 예측의 절대다수는 지도 학습으로 풀린다. 비지도 학습은 라벨이 없을 때의 탐색·전처리 수단으로, 강화 학습은 순차적 행동이 본질인 문제에서 주로 등장한다.

## 4. 실무 문제를 지도 학습으로 프레이밍하기

현실의 요구사항은 "지도 학습 문제"라는 딱지를 달고 오지 않는다. 이걸 X, y, 손실로 번역하는 것이 데이터 과학의 첫 관문이다. 판별의 열쇠는 <strong>학습에 쓸 정답(y)을 실제로 확보할 수 있는가</strong>다.

- <strong>이탈 예측(churn)</strong> — 과거 고객들의 "그 뒤 실제로 이탈했는지"를 라벨로 붙일 수 있으면 이탈=1/유지=0의 이진 분류다. 라벨은 과거 로그에서 사후적으로 만들어진다.
- <strong>수요 예측(demand)</strong> — 과거 판매량이라는 연속값 정답이 있으니 회귀다. 다만 시간 순서가 핵심이라 분할·검증 방식이 일반 회귀와 다르다([4장](/study/supervised-learning/04-cross-validation-tuning)에서 시계열 분할로 다룬다).
- <strong>이상 탐지(anomaly)</strong> — 여기가 경계다. "사기/정상" 라벨을 충분히 확보했다면 (대개 극심한 불균형의) 지도 분류로 풀 수 있다. 하지만 이상 사례가 극히 드물거나 라벨 자체가 없다면, 정상 데이터의 분포만 학습해 벗어난 것을 찾는 <strong>비지도 이상 탐지</strong>로 기운다. 같은 "이상 탐지"라도 라벨 유무가 패러다임을 가른다.

::: tip 지도 학습 문제인지 판별하는 질문
"과거 데이터의 각 샘플에 대해, 내가 예측하려는 정답을 지금 붙일 수 있는가?" — Yes면 지도 학습으로 시작하라. No거나 정답이 극히 희소하면 비지도 쪽을 검토한다.
:::

## 5. 첫 코드 — fit / predict 계약

scikit-learn의 모든 지도 학습 모델은 <strong>동일한 계약</strong>을 따른다. `fit(X, y)`로 학습하고 `predict(X_new)`로 예측한다. 모델을 바꿔도 이 인터페이스는 그대로라, kNN을 GBDT로 교체하는 것이 사실상 클래스 이름 한 줄 교체가 된다.

![fit/predict 계약 — 학습 데이터의 X와 y로 fit해 모델 f의 파라미터를 학습하고, 학습된 f를 고정한 채 정답 없는 새 입력 X_new에 predict를 적용해 예측값을 얻는다](/images/study-supervised-learning/01-fit-predict-light.png)
![fit/predict 계약 — 학습 데이터의 X와 y로 fit해 모델 f의 파라미터를 학습하고, 학습된 f를 고정한 채 정답 없는 새 입력 X_new에 predict를 적용해 예측값을 얻는다](/images/study-supervised-learning/01-fit-predict-dark.png)

분류 예제로 계약을 확인한다. 붓꽃 데이터로 품종을 맞히는 분류기다.

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score

X, y = load_iris(return_X_y=True)          # X: (150, 4) 특징, y: (150,) 품종 0/1/2

# 학습용과 평가용을 나눈다 — 본 적 없는 데이터로 재야 하므로 (2장 참고)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y)

model = KNeighborsClassifier(n_neighbors=5)
model.fit(X_train, y_train)                # 학습: X_train → y_train 규칙을 배운다
pred = model.predict(X_test)               # 예측: 정답 없는 X_test에 적용

print(accuracy_score(y_test, pred))        # 예: 0.97
```

핵심은 <strong>`fit`에는 정답 y가 들어가지만 `predict`에는 X만 들어간다</strong>는 점이다. 이 비대칭이 지도 학습의 본질을 그대로 보여준다 — 학습할 때만 정답을 보고, 예측할 때는 정답 없이 입력만으로 답을 내야 한다.

회귀도 인터페이스는 똑같고 모델 클래스와 지표만 바뀐다.

```python
from sklearn.datasets import fetch_california_housing
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

X, y = fetch_california_housing(return_X_y=True)   # y: 집값(연속값)
X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)

reg = LinearRegression().fit(X_train, y_train)
pred = reg.predict(X_test)
print(mean_absolute_error(y_test, pred))           # 평균 절대 오차(원 단위 해석 가능)
```

`KNeighborsClassifier`가 `LinearRegression`으로, `accuracy_score`가 `mean_absolute_error`로 바뀌었을 뿐 `fit`/`predict`의 흐름은 동일하다. 이 일관성 덕분에 앞으로 배울 수많은 모델을 같은 골격 위에서 갈아 끼우며 비교할 수 있다.

한 가지 더 알아둘 것은, 분류기는 `predict`로 클래스를 바로 내놓기 전에 대개 <strong>클래스별 확률 `predict_proba`</strong>를 계산하고 임계값 0.5로 잘라 최종 클래스를 정한다는 점이다.

```python
proba = model.predict_proba(X_test)        # 각 클래스에 대한 확률, 합은 1
print(proba[0])                            # 예: [0.02 0.95 0.03] → 클래스 1로 예측
```

이 확률을 어디서 자르느냐(임계값)가 정밀도와 재현율을 맞바꾸는 손잡이이며, 임계값에 무관한 순위 품질을 재는 ROC/PR 곡선의 출발점이기도 하다 — 모두 [3장 평가 지표](/study/supervised-learning/03-evaluation-metrics)에서 이어진다.

::: tip 핵심 정리
- 지도 학습은 입력 X와 정답 y의 쌍에서 손실을 최소화하는 함수 f를 찾는 문제다.
- 진짜 목표는 훈련 손실이 아니라 본 적 없는 데이터에서의 손실이며, 이 간극이 과적합 문제로 이어진다.
- 정답 y가 연속값이면 회귀, 유한한 범주면 분류다. 같은 질문도 y 정의에 따라 갈린다.
- 지도·비지도·강화 학습은 "무엇을 받아 무엇을 최적화하는가"로 구분되고, 실무 tabular 예측은 대부분 지도 학습이다.
- 실무 문제가 지도 학습인지는 "각 샘플에 정답을 붙일 수 있는가"로 판별한다. 이상 탐지는 라벨 유무에 따라 지도/비지도로 갈린다.
- scikit-learn은 `fit(X, y)`/`predict(X)` 계약을 모든 모델에 공유해, 모델 교체가 클래스 한 줄 교체가 된다.
:::

## 다음 챕터

`fit`이 훈련 데이터를 잘 맞히는 것과, 그 모델이 새 데이터에서도 잘 맞히는 것은 전혀 다른 문제다. [일반화와 과적합](/study/supervised-learning/02-generalization-overfitting)에서는 암기와 일반화를 가르는 선이 어디인지, train/valid/test 3분할이 왜 필요한지, 그리고 모든 모델 선택의 밑바탕에 깔린 편향-분산 트레이드오프를 다룬다.
