---
title: "모델 평가 지표"
description: "회귀 지표(MSE/RMSE/MAE/R²)의 이상치 민감성 차이와 분류 지표(혼동 행렬→정밀도/재현율/F1)를 정리하고 정확도의 함정을 짚는다. 불균형 데이터에서 ROC-AUC와 PR-AUC가 어떻게 갈리는지, 다중 클래스 평균(macro/micro/weighted) 선택, 그리고 지표를 비즈니스 비용에서 역산하는 기준을 다룬다."
date: 2026-07-03
tags: [Machine Learning, Supervised Learning, Metrics, ROC-AUC, Precision-Recall]
prev: /study/supervised-learning/02-generalization-overfitting
next: /study/supervised-learning/04-cross-validation-tuning
---

# 모델 평가 지표

::: info 학습 목표
- 회귀 지표 MSE/RMSE/MAE/R²의 차이, 특히 이상치 민감성 차이를 이해한다.
- 혼동 행렬에서 정밀도·재현율·F1이 어떻게 유도되는지 안다.
- 정확도(accuracy)가 불균형 데이터에서 왜 함정인지 설명한다.
- ROC-AUC와 PR-AUC가 불균형에서 어떻게 갈리는지 구분한다.
- 다중 클래스 평균(macro/micro/weighted)을 상황에 맞게 고른다.
- 지표를 비즈니스 비용에서 역산해 선택하는 관점을 갖는다.
:::

## 1. 회귀 지표 — 이상치 민감성이 가른다

회귀 지표는 "예측이 정답에서 얼마나 벗어났는가"를 재는데, <strong>오차를 어떻게 벌하느냐</strong>에서 성격이 갈린다.

- <strong>MAE(평균 절대 오차)</strong> — 오차의 절댓값 평균. 원래 단위(원, 개)로 해석되고, 큰 오차든 작은 오차든 <strong>선형으로</strong> 벌해서 이상치에 둔감하다.
- <strong>MSE(평균 제곱 오차)</strong> — 오차를 제곱해 평균. 큰 오차를 <strong>제곱으로</strong> 크게 벌해서 이상치에 민감하다. 단위가 제곱이라 직접 해석은 어렵다.
- <strong>RMSE</strong> — MSE의 제곱근. 이상치 민감성은 MSE와 같고, 단위를 원래대로 되돌려 해석 가능하게 만든 것.
- <strong>R²(결정 계수)</strong> — "평균으로만 예측하는 것 대비 얼마나 나은가"를 0~1(음수도 가능)로 표준화한 상대 지표. 스케일이 다른 문제 간 비교에 편하다.

핵심 갈림길은 <strong>이상치를 어떻게 볼 것인가</strong>다. 배달 시간 예측에서 몇 건의 극단적 지연을 반드시 잡아야 한다면 그 큰 오차를 강하게 벌하는 RMSE가 맞고, 극단값이 측정 오류에 가까워 무시하고 싶다면 MAE가 낫다.

```python
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np

y_true = np.array([100, 102, 98, 500])     # 마지막이 이상치
y_pred = np.array([101, 100, 99, 120])

print(mean_absolute_error(y_true, y_pred))          # 96.0  — 선형 반영
print(np.sqrt(mean_squared_error(y_true, y_pred)))  # 190.0 — 이상치에 크게 반응
print(r2_score(y_true, y_pred))                     # 큰 오차 하나로 급락
```

같은 예측인데 RMSE가 MAE의 두 배다. 이 격차 자체가 "큰 오차 소수가 존재한다"는 신호이며, 두 지표를 <strong>함께</strong> 보면 오차 분포의 모양까지 읽을 수 있다.

## 2. 분류 지표 — 혼동 행렬에서 출발

분류 지표는 모두 <strong>혼동 행렬(confusion matrix)</strong>이라는 2×2 표에서 유도된다. 관심 클래스를 Positive로 두고 예측×실제의 네 칸을 센다.

![혼동 행렬에서 정밀도·재현율 유도 — 실제와 예측의 2x2 표에서 TP/FP/FN/TN을 세고, 정밀도는 예측 Positive 열 방향으로 TP/(TP+FP), 재현율은 실제 Positive 행 방향으로 TP/(TP+FN)로 계산한다](/images/study-supervised-learning/03-confusion-matrix-light.png)
![혼동 행렬에서 정밀도·재현율 유도 — 실제와 예측의 2x2 표에서 TP/FP/FN/TN을 세고, 정밀도는 예측 Positive 열 방향으로 TP/(TP+FP), 재현율은 실제 Positive 행 방향으로 TP/(TP+FN)로 계산한다](/images/study-supervised-learning/03-confusion-matrix-dark.png)

- <strong>정밀도(precision) = TP / (TP+FP)</strong> — 모델이 Positive라 외친 것 중 진짜 비율. "거짓 경보를 얼마나 안 내는가."
- <strong>재현율(recall) = TP / (TP+FN)</strong> — 실제 Positive 중 모델이 잡아낸 비율. "놓치지 않고 얼마나 잡는가."
- <strong>F1 = 정밀도와 재현율의 조화 평균</strong> — 둘의 균형을 하나로 요약. 한쪽이 심하게 낮으면 F1도 낮아진다.

정밀도와 재현율은 <strong>맞교환</strong> 관계다. 판정 임계값(threshold)을 낮춰 Positive를 남발하면 재현율은 오르지만 정밀도는 떨어지고, 반대로 높이면 정밀도는 오르지만 재현율이 떨어진다. 그래서 하나만 봐선 안 되고, 어느 쪽이 비즈니스에 중요한지가 임계값을 정한다.

## 3. 정확도의 함정

<strong>정확도(accuracy) = 전체 중 맞힌 비율</strong>은 직관적이지만 불균형 데이터에서 완전히 무너진다. 사기 거래가 0.1%인 데이터에서 "전부 정상"이라고만 답하는 모델은 정확도 99.9%지만, 사기를 한 건도 못 잡으니 쓸모가 없다.

```python
from sklearn.metrics import accuracy_score, precision_score, recall_score

y_true = [0]*999 + [1]      # 1000개 중 사기 1건
y_pred = [0]*1000           # 전부 정상이라 예측

print(accuracy_score(y_true, y_pred))    # 0.999  — 훌륭해 보이지만
print(recall_score(y_true, y_pred))      # 0.0    — 사기를 하나도 못 잡음
```

정확도가 높다는 말이 무의미해지는 지점이다. <strong>불균형 데이터에서는 정확도 대신 관심 클래스의 정밀도·재현율·F1을, 확률 순위 품질은 뒤에 나올 PR-AUC를 봐야 한다.</strong>

## 4. ROC-AUC vs PR-AUC

임계값 하나에 매이지 않고 <strong>모든 임계값에 걸친 순위 품질</strong>을 하나의 곡선·넓이로 요약하는 것이 ROC와 PR이다.

![ROC 곡선과 PR 곡선 — ROC는 FPR 대 TPR을 그리며 무작위 분류기가 대각선 기준선이고, PR은 Recall 대 Precision을 그리며 양성 비율이 수평 기준선이 되어 불균형이 심할수록 기준선이 낮아진다](/images/study-supervised-learning/03-roc-pr-light.png)
![ROC 곡선과 PR 곡선 — ROC는 FPR 대 TPR을 그리며 무작위 분류기가 대각선 기준선이고, PR은 Recall 대 Precision을 그리며 양성 비율이 수평 기준선이 되어 불균형이 심할수록 기준선이 낮아진다](/images/study-supervised-learning/03-roc-pr-dark.png)

- <strong>ROC 곡선</strong> — x축 FPR(거짓 양성률), y축 TPR(재현율). 넓이(AUC)가 1에 가까울수록 좋고 0.5는 무작위. <strong>참 음성(TN)</strong>을 계산에 포함한다.
- <strong>PR 곡선</strong> — x축 재현율, y축 정밀도. TN을 아예 쓰지 않아 <strong>Positive를 얼마나 잘 찾는가</strong>에만 집중한다.

둘이 갈리는 지점이 <strong>불균형</strong>이다. ROC-AUC는 FPR을 쓰는데, 음성이 압도적으로 많으면 거짓 양성이 꽤 늘어도 FPR은 분모(전체 음성)가 커서 별로 안 움직인다. 그래서 <strong>ROC-AUC는 극심한 불균형에서 성능을 낙관적으로 보여준다.</strong> 반면 PR-AUC의 정밀도는 분모가 예측 Positive라 거짓 양성 증가에 곧바로 반응해, 소수 Positive를 찾는 문제(사기·질병·이상 탐지)의 실제 난이도를 더 정직하게 드러낸다.

::: tip 어느 곡선을 볼까
음성·양성이 비교적 균형 잡혀 있으면 ROC-AUC가 직관적이고 안정적이다. <strong>Positive가 희소하고 그걸 찾는 게 목적이면 PR-AUC를 본다.</strong> PR 곡선의 기준선은 양성 비율이라, 불균형이 심할수록 기준선이 낮아져 "무작위 대비 얼마나 나은가"가 냉정하게 보인다.
:::

::: details 순위가 아니라 확률값 자체가 중요하다면
ROC-AUC·PR-AUC는 <strong>순위(어느 게 더 Positive 같은가)</strong>만 평가한다. 하지만 예측 확률을 그대로 의사결정에 쓴다면(기대 손실 계산, 가격 책정 등) 확률값이 실제 빈도와 맞는지가 중요하다. 이를 재는 지표가 로그 손실(`log_loss`)과 브라이어 점수(`brier_score_loss`)다. AUC는 높은데 확률이 0/1로 쏠려 캘리브레이션이 나쁠 수 있는데, 이 교정은 [17장](/study/supervised-learning/17-imbalanced-calibration)에서 다룬다.
:::

## 5. 다중 클래스 평균 — macro / micro / weighted

클래스가 셋 이상이면 클래스별 정밀도·재현율을 하나로 합쳐야 하는데, <strong>합치는 방식</strong>이 결과를 바꾼다.

- <strong>macro</strong> — 클래스별 지표를 <strong>단순 평균</strong>. 모든 클래스를 동등하게 취급해, 샘플 적은 소수 클래스도 큰 클래스와 같은 비중을 갖는다. 소수 클래스 성능이 중요하면 이걸 본다.
- <strong>micro</strong> — 전체 TP/FP/FN을 다 모아 <strong>한 번에</strong> 계산. 샘플 많은 클래스가 지배하며, 다중 클래스에서 micro 평균 F1은 정확도와 같아진다.
- <strong>weighted</strong> — 클래스별 지표를 <strong>샘플 수로 가중 평균</strong>. macro와 micro의 절충으로, 클래스 비중을 반영하되 클래스별 지표를 유지한다.

```python
from sklearn.metrics import f1_score, classification_report

print(f1_score(y_true, y_pred, average="macro"))     # 소수 클래스 동등 반영
print(f1_score(y_true, y_pred, average="weighted"))  # 샘플 수로 가중
print(classification_report(y_true, y_pred))         # 클래스별 + 세 평균 한눈에
```

불균형 다중 클래스에서 macro와 weighted가 크게 벌어진다면, 그 격차가 "소수 클래스에서 모델이 약하다"는 진단이다. `classification_report`로 클래스별 수치를 함께 보면 어느 클래스가 발목을 잡는지 바로 보인다.

## 6. 지표는 비즈니스 비용에서 역산한다

지표 선택의 최종 기준은 통계가 아니라 <strong>틀렸을 때의 비용</strong>이다. 거짓 양성(FP)과 거짓 음성(FN)의 대가가 비대칭이면, 그 비대칭이 지표와 임계값을 정해야 한다.

- <strong>암 검진</strong> — FN(놓친 환자)의 대가가 FP(추가 검사)보다 훨씬 크다 → <strong>재현율</strong> 우선.
- <strong>스팸 필터</strong> — FP(중요 메일을 스팸함으로)가 FN(스팸 몇 개 통과)보다 치명적 → <strong>정밀도</strong> 우선.
- <strong>사기 탐지</strong> — 양성이 희소하고 놓치면 큰 손실 → <strong>PR-AUC</strong>로 모델을 고르고, FP 심사 비용과 FN 손실을 저울질해 임계값을 정한다.

이 방향은 절대 뒤집지 않는다. <strong>먼저 "무엇을 틀리면 얼마를 잃는가"를 정하고, 거기서 지표를 역산한다.</strong> 지표를 먼저 고르고 비즈니스를 끼워 맞추면, 최적화가 끝난 모델이 정작 현장에서 엉뚱한 실수를 저지른다. F1을 기본값처럼 쓰는 습관도 이 점에서 위험하다 — 정밀도와 재현율에 같은 비중을 준다는 건 그 자체로 하나의 비즈니스 가정이기 때문이다. 임계값 조정과 확률 캘리브레이션으로 이 비용 비대칭을 다루는 실전은 [17장](/study/supervised-learning/17-imbalanced-calibration)에서 이어진다.

::: tip 핵심 정리
- 회귀 지표는 이상치 민감성이 가른다. MAE는 둔감·선형, MSE/RMSE는 제곱으로 큰 오차를 크게 벌한다. 두 지표를 함께 보면 오차 분포가 읽힌다.
- 정밀도·재현율·F1은 모두 혼동 행렬에서 유도되며, 정밀도와 재현율은 임계값을 사이에 둔 맞교환 관계다.
- 정확도는 불균형에서 무너진다. 다수 클래스만 찍어도 높게 나오므로 관심 클래스의 정밀도·재현율을 본다.
- ROC-AUC는 TN을 포함해 불균형에서 낙관적일 수 있고, PR-AUC는 소수 Positive를 찾는 문제의 난이도를 더 정직하게 드러낸다.
- 다중 클래스는 macro(소수 클래스 동등)·micro(다수 클래스 지배)·weighted(샘플 수 가중)로 평균 방식을 골라야 한다.
- 지표는 FP·FN의 비용 비대칭에서 역산한다. 무엇을 틀리면 얼마를 잃는지를 먼저 정하고 지표를 고른다.
:::

## 다음 챕터

지표를 정했어도 valid 한 조각으로 낸 점수는 우연에 흔들린다. [교차 검증과 하이퍼파라미터 튜닝](/study/supervised-learning/04-cross-validation-tuning)에서는 k-fold로 성능 추정을 안정화하고, 그룹·시계열 분할로 누출을 막으며, grid/random/bayesian search로 하이퍼파라미터를 leakage 없이 고르는 방법을 다룬다.
