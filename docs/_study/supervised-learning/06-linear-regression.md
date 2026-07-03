---
title: "선형 회귀와 정규화"
description: "선형 가설과 OLS 닫힌해, 대규모에서 경사하강법(배치/미니배치/SGD)을 쓰는 이유, 다항 피처로의 비선형 확장, 과적합을 막는 릿지·라쏘·엘라스틱넷 정규화와 라쏘의 피처 선택 효과, 스케일링과 정규화의 관계, 다중공선성 아래 계수 해석의 함정까지 선형 회귀를 실전 관점에서 정리한다."
date: 2026-07-03
tags: [Machine Learning, Supervised Learning, Linear Regression, Ridge, Lasso, scikit-learn]
prev: /study/supervised-learning/05-knn
next: /study/supervised-learning/07-logistic-regression
---

# 선형 회귀와 정규화

::: info 학습 목표
- 선형 가설과 OLS(최소제곱)가 잔차 제곱합을 최소화한다는 것과, 닫힌해가 존재한다는 사실을 이해한다.
- 닫힌해가 있는데도 대규모 데이터에서는 왜 경사하강법(배치/미니배치/SGD)을 쓰는지 안다.
- 다항 피처로 선형 모델을 비선형으로 확장하는 방법과 그 대가(과적합)를 안다.
- 릿지(L2)·라쏘(L1)·엘라스틱넷 정규화의 차이와, 라쏘가 왜 피처 선택 효과를 갖는지 이해한다.
- 정규화 전에 스케일링이 필수인 이유를 안다.
- 다중공선성이 있을 때 계수 해석이 왜 위험한지 파악한다.
:::

## 1. 선형 가설과 OLS

선형 회귀는 입력 피처의 <strong>가중 합</strong>으로 연속값 출력을 예측한다. 피처가 여러 개면 예측은 `ŷ = w₁x₁ + w₂x₂ + … + wₙxₙ + b` 형태이고, 학습은 이 가중치 `w`와 절편 `b`를 데이터에 맞게 정하는 일이다. "무엇에 맞춘다"의 기준이 바로 <strong>OLS(Ordinary Least Squares, 최소제곱)</strong> — 각 데이터의 실제값과 예측값의 차이(잔차)를 제곱해 모두 더한 <strong>잔차 제곱합(RSS)</strong>을 최소화하는 직선을 고른다.

![OLS는 각 점에서 회귀 직선까지의 세로 거리(잔차)를 제곱해 합한 값을 최소화한다. 데이터 점들과 이를 관통하는 회귀 직선, 그리고 각 점에서 직선으로 내려긋는 잔차 세로선을 보여준다](/images/study-supervised-learning/06-ols-residuals-light.png)
![OLS는 각 점에서 회귀 직선까지의 세로 거리(잔차)를 제곱해 합한 값을 최소화한다. 데이터 점들과 이를 관통하는 회귀 직선, 그리고 각 점에서 직선으로 내려긋는 잔차 세로선을 보여준다](/images/study-supervised-learning/06-ols-residuals-dark.png)

왜 절댓값이 아니라 제곱인가. 제곱은 큰 오차에 더 큰 벌점을 줘 이상치에 민감하지만, 대신 <strong>미분 가능한 매끄러운 함수</strong>가 되어 최소점을 대수적으로 풀 수 있다. 그 결과가 선형 회귀의 가장 큰 특징인 <strong>닫힌해(closed-form solution)</strong>다 — 정규방정식 `w = (XᵀX)⁻¹Xᵀy`로 반복 없이 한 번에 최적 가중치가 나온다. 트리나 신경망처럼 반복 최적화가 필요한 모델과 달리, 선형 회귀는 이론적으로 정확한 해가 공식으로 존재한다.

```python
from sklearn.linear_model import LinearRegression

model = LinearRegression()
model.fit(X_train, y_train)          # 내부적으로 최소제곱해를 구함
print(model.coef_, model.intercept_) # 가중치 w, 절편 b
```

학습된 회귀 모델이 얼마나 맞는지는 잔차 기반 지표로 잰다 — 평균이 아니라 예측이 실제 변동을 얼마나 설명하는지 보는 <strong>R²(결정계수)</strong>, 오차 크기를 원 단위로 보는 <strong>RMSE·MAE</strong>가 대표적이다. RSS를 최소화한다는 목표가 곧 RMSE를 줄이는 것과 같은 방향임을 기억하면 된다. 회귀 지표의 선택 기준은 [3장 모델 평가 지표](/study/supervised-learning/03-evaluation-metrics)에서 다룬다.

## 2. 경사하강법 — 닫힌해가 있는데도 쓰는 이유

닫힌해가 있는데 왜 경사하강법을 이야기하나. `(XᵀX)⁻¹`은 피처 개수 `n`에 대해 대략 `O(n³)` 비용의 행렬 역연산을 요구한다. 피처가 수만 개거나 샘플이 수천만 개면 이 역행렬을 메모리에 올리는 것 자체가 불가능하다. 이때는 손실 함수의 <strong>기울기(gradient)</strong> 방향으로 가중치를 조금씩 움직여 최소점에 다가가는 <strong>경사하강법(gradient descent)</strong>이 현실적인 대안이다.

경사하강법은 한 번의 갱신에 얼마나 많은 데이터를 쓰느냐로 갈린다.

- <strong>배치 GD(Batch)</strong> — 매 갱신마다 <strong>전체 데이터</strong>로 기울기를 계산한다. 방향이 정확해 매끄럽게 수렴하지만, 한 스텝마다 전체를 훑어 대규모에서는 느리다.
- <strong>확률적 GD(SGD)</strong> — <strong>한 샘플</strong>씩 기울기를 계산해 바로 갱신한다. 방향이 출렁여 지그재그로 움직이지만 스텝이 압도적으로 싸고, 데이터가 스트리밍으로 들어와도 학습할 수 있다.
- <strong>미니배치 GD(Mini-batch)</strong> — 32·64·256개 같은 <strong>작은 묶음</strong>으로 계산한다. 둘의 절충안으로, 벡터 연산 효율과 안정성을 함께 얻어 실무 기본값이다.

![배치 GD와 SGD의 손실 등고선 위 수렴 경로 비교. 배치 GD는 전체 데이터로 정확한 방향을 계산해 매끄러운 곡선으로 최소점에 접근하고, SGD는 한 샘플씩 갱신해 지그재그로 출렁이며 최소점 근처로 수렴한다](/images/study-supervised-learning/06-gd-paths-light.png)
![배치 GD와 SGD의 손실 등고선 위 수렴 경로 비교. 배치 GD는 전체 데이터로 정확한 방향을 계산해 매끄러운 곡선으로 최소점에 접근하고, SGD는 한 샘플씩 갱신해 지그재그로 출렁이며 최소점 근처로 수렴한다](/images/study-supervised-learning/06-gd-paths-dark.png)

정리하면 데이터가 작으면 닫힌해(`LinearRegression`)가 간단하고 정확하지만, <strong>대규모·온라인 학습에서는 `SGDRegressor` 같은 경사하강 기반 구현</strong>이 사실상 필수다. 경사하강법은 스텝 크기(학습률)에 민감하므로 피처 스케일이 제각각이면 수렴이 크게 흔들린다 — [5장 스케일링](/study/supervised-learning/05-knn)이 여기서도 전제 조건이 된다.

```python
from sklearn.linear_model import SGDRegressor

# 대규모/온라인 학습: 스케일링이 특히 중요
model = SGDRegressor(loss="squared_error", penalty="l2", max_iter=1000)
model.fit(X_train_scaled, y_train)
```

## 3. 다항 피처로 비선형 확장

선형 회귀의 "선형"은 <strong>가중치에 대해 선형</strong>이라는 뜻이지, 피처와 출력의 관계가 직선이어야 한다는 뜻이 아니다. 원래 피처 `x`에 `x²`, `x³`, `x₁x₂` 같은 <strong>다항 피처</strong>를 추가로 만들어 넣으면, 모델은 여전히 가중치에 대해 선형이면서도 곡선·곡면을 학습할 수 있다. 즉 비선형 관계를 선형 모델의 틀 안에서 다룰 수 있다.

```python
from sklearn.preprocessing import PolynomialFeatures
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LinearRegression

# 2차 다항 피처 + 선형 회귀
model = make_pipeline(PolynomialFeatures(degree=2), LinearRegression())
model.fit(X_train, y_train)
```

대가는 명확하다. 차수를 올릴수록 피처 수가 폭발하고 모델이 훈련 데이터의 잡음까지 외워 <strong>과적합</strong>한다 — [2장](/study/supervised-learning/02-generalization-overfitting)에서 본 편향-분산 트레이드오프에서 분산이 급격히 커지는 전형적 상황이다. 그래서 다항 확장은 거의 항상 다음에 볼 <strong>정규화</strong>와 짝을 이룬다.

## 4. 과적합과 정규화 — 릿지·라쏘·엘라스틱넷

과적합한 선형 모델의 증상은 <strong>거대한 가중치</strong>다. 데이터의 작은 흔들림에 억지로 맞추느라 계수가 극단적으로 커진다. <strong>정규화(regularization)</strong>는 손실 함수에 "가중치가 크면 벌점"을 더해, 데이터 적합과 가중치 크기 억제를 동시에 추구하게 만든다. 벌점의 형태에 따라 세 가지로 나뉜다.

- <strong>릿지(Ridge, L2)</strong> — 가중치 제곱합 `Σwᵢ²`을 벌점으로 더한다. 계수를 전반적으로 0 쪽으로 <strong>줄이되 완전히 0으로는 잘 만들지 않는다</strong>. 다중공선성에 강하다.
- <strong>라쏘(Lasso, L1)</strong> — 가중치 절댓값 합 `Σ|wᵢ|`을 더한다. 일부 계수를 <strong>정확히 0으로</strong> 만들어, 정규화와 동시에 <strong>피처 선택</strong>이 일어난다.
- <strong>엘라스틱넷(Elastic Net)</strong> — L1과 L2를 섞는다. 피처 선택 효과를 유지하면서 상관 높은 피처 그룹을 함께 다루는 라쏘의 불안정성을 완화한다.

라쏘가 계수를 0으로 만드는 이유는 <strong>제약 영역의 모양</strong>에 있다. 정규화는 "RSS를 최소화하되 가중치를 일정 크기 안에 가두라"는 제약과 같은데, L2의 제약 영역은 매끄러운 <strong>원</strong>이고 L1은 축 위에 뾰족한 꼭짓점을 가진 <strong>마름모</strong>다. RSS 등고선이 제약 영역과 처음 닿는 지점이 해가 되는데, 마름모는 꼭짓점(=어떤 계수가 0인 축)에서 닿기 쉬워 계수가 0이 된다.

![릿지(L2)와 라쏘(L1)의 제약 영역 비교. 왼쪽 릿지는 원형 제약이라 RSS 등고선과 곡면에서 만나 계수가 0이 되지 않고, 오른쪽 라쏘는 마름모 제약이라 뾰족한 꼭짓점(한 계수가 0인 축) 위에서 만나 그 계수가 정확히 0이 된다](/images/study-supervised-learning/06-regularization-constraint-light.png)
![릿지(L2)와 라쏘(L1)의 제약 영역 비교. 왼쪽 릿지는 원형 제약이라 RSS 등고선과 곡면에서 만나 계수가 0이 되지 않고, 오른쪽 라쏘는 마름모 제약이라 뾰족한 꼭짓점(한 계수가 0인 축) 위에서 만나 그 계수가 정확히 0이 된다](/images/study-supervised-learning/06-regularization-constraint-dark.png)

벌점의 세기는 `alpha`로 조절한다. `alpha`가 0이면 일반 OLS, 커질수록 계수를 강하게 억제해 편향이 늘고 분산이 준다. 적절한 `alpha`는 [4장 교차 검증](/study/supervised-learning/04-cross-validation-tuning)으로 고른다.

셋 중 무엇을 쓸지는 피처에 대한 가정으로 갈린다. <strong>대부분의 피처가 조금씩 기여</strong>한다고 보면 릿지가 기본값으로 무난하고, <strong>상당수 피처가 쓸모없어 희소한 모델을 원하면</strong> 라쏘가 자동으로 걸러준다. <strong>피처가 서로 상관 높은 그룹을 이루면</strong> 라쏘는 그룹에서 하나만 임의로 남기고 나머지를 0으로 만드는 불안정성이 있어, 이럴 때 엘라스틱넷이 그룹을 함께 살리며 안정적으로 작동한다.

```python
from sklearn.linear_model import Ridge, Lasso, ElasticNet

Ridge(alpha=1.0).fit(X_train_scaled, y_train)                    # L2
Lasso(alpha=0.1).fit(X_train_scaled, y_train)                    # L1 (일부 계수 0)
ElasticNet(alpha=0.1, l1_ratio=0.5).fit(X_train_scaled, y_train) # L1+L2 혼합
```

## 5. 스케일링과 정규화의 관계

정규화는 <strong>스케일링을 반드시 전제</strong>한다. 벌점 `Σwᵢ²`은 계수의 크기를 보는데, 어떤 피처가 미터(0~2) 단위이고 다른 피처가 밀리미터(0~2000) 단위라면, 같은 실제 영향이라도 밀리미터 피처의 계수가 1000배 작아 벌점을 거의 안 받는다. 즉 <strong>단위가 큰 피처가 정규화를 회피</strong>해 벌점이 불공평하게 걸린다.

그래서 릿지·라쏘·엘라스틱넷 앞에는 [5장](/study/supervised-learning/05-knn)에서 본 표준화(`StandardScaler`)가 사실상 필수다. 순서 실수로 인한 leakage를 막으려면 [4장](/study/supervised-learning/04-cross-validation-tuning)처럼 `Pipeline`으로 묶어 fold 안에서 스케일러가 학습되게 한다.

```python
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge

# 스케일러를 파이프라인에 묶어 fold별로 안전하게 fit
model = make_pipeline(StandardScaler(), Ridge(alpha=1.0))
```

## 6. 계수 해석의 함정 — 다중공선성

선형 회귀의 매력은 "계수를 곧 피처의 영향력으로 읽을 수 있다"는 해석 가능성이다. 하지만 이 해석에는 큰 함정이 있다. 피처들끼리 강하게 상관돼 있으면(<strong>다중공선성, multicollinearity</strong>) 개별 계수가 <strong>불안정</strong>해진다. 예를 들어 "키(cm)"와 "키(inch)"처럼 사실상 같은 정보를 담은 두 피처가 있으면, 모델은 둘 사이에 영향력을 임의로 배분한다 — 한쪽 계수가 +10, 다른 쪽이 -8이 되기도 하고, 데이터가 조금만 바뀌어도 값이 크게 요동친다.

이 상태에서 "이 피처의 계수가 음수이니 출력을 낮춘다"고 단정하면 틀린 결론에 이르기 쉽다. 대응은 세 가지다 — 상관 높은 피처를 제거·통합하거나(VIF로 진단), <strong>릿지</strong>로 계수를 안정화하거나, 인과가 아닌 <strong>예측</strong>이 목적이라면 개별 계수 해석을 아예 포기하고 예측 성능만 본다. 계수 해석이 핵심이라면 [18장 모델 해석](/study/supervised-learning/18-model-interpretation)의 permutation importance·SHAP처럼 상관에 덜 취약한 도구를 병행하는 편이 안전하다.

::: tip 핵심 정리
- 선형 회귀는 잔차 제곱합(RSS)을 최소화하며, 정규방정식으로 <strong>닫힌해</strong>가 존재한다.
- 닫힌해는 역행렬 비용 때문에 대규모에선 비싸다 — 피처·샘플이 많거나 온라인 학습이면 배치/미니배치/SGD 경사하강법을 쓴다(미니배치가 실무 기본).
- 다항 피처를 추가하면 선형 모델로 비선형 관계를 학습할 수 있지만 과적합 위험이 커진다.
- 정규화는 큰 가중치에 벌점을 준다 — 릿지(L2)는 계수를 줄이고, 라쏘(L1)는 일부를 0으로 만들어 피처 선택을, 엘라스틱넷은 둘을 절충한다.
- 정규화는 스케일 민감하므로 표준화가 필수이며, `Pipeline`으로 묶어 leakage를 막는다.
- 다중공선성이 있으면 개별 계수 해석이 불안정해진다 — 릿지로 안정화하거나 예측 목적에 집중한다.
:::

## 다음 챕터

선형 회귀는 연속값을 예측한다. 그렇다면 "이 메일이 스팸인가"처럼 <strong>범주</strong>를 맞히는 분류는 어떻게 풀까. [로지스틱 회귀](/study/supervised-learning/07-logistic-regression)에서는 선형 출력을 시그모이드로 확률로 바꿔 분류를 푸는 아이디어와, 크로스엔트로피 손실·다중 클래스 전략을 다룬다.
