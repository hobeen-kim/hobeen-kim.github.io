---
title: "불균형 데이터와 캘리브레이션"
description: "클래스 불균형에서 정확도가 무너지는 이유를 PR-AUC로 다시 짚고, class_weight·리샘플링(SMOTE)·threshold 조정으로 예측을 교정하며, 모델별 확률 왜곡을 reliability diagram으로 진단하고 Platt scaling·isotonic·CalibratedClassifierCV로 확률을 보정하는 실전 우선순위를 정리한다."
date: 2026-07-03
tags: [SupervisedLearning, ImbalancedData, Calibration, SMOTE, Threshold]
prev: /study/supervised-learning/16-feature-engineering-pipeline
next: /study/supervised-learning/18-model-interpretation
---

# 불균형 데이터와 캘리브레이션

::: info 학습 목표
- 클래스 불균형에서 정확도가 왜 무의미해지는지 이해하고, PR-AUC 같은 지표로 다시 본다.
- `class_weight`로 손실을 재조정하는 방식과 그 한계를 안다.
- 언더/오버샘플링과 SMOTE의 원리·주의점을 이해하고, 리샘플링을 CV fold 안에서만 적용해야 하는 이유를 안다.
- 기본 임계값 0.5가 규칙이 아니라는 점을 이해하고, 비용 기반으로 threshold를 최적화한다.
- 모델별 확률 왜곡 성향을 reliability diagram으로 진단하고, Platt scaling·isotonic으로 보정한다.
- `CalibratedClassifierCV`로 확률 보정을 파이프라인에 넣고, 불균형 대응의 우선순위를 세운다.
:::

## 1. 불균형에서 정확도는 붕괴한다

양성이 전체의 1%인 사기 탐지 데이터를 생각해보자. "무조건 음성"이라고 답하는 모델은 정확도 99%를 얻지만, 정작 잡아야 할 사기는 하나도 못 잡는다. [3장 평가 지표](/study/supervised-learning/03-evaluation-metrics)에서 다뤘듯, 불균형에서는 정확도가 다수 클래스에 지배당해 모델의 실제 유용성을 전혀 반영하지 못한다.

이때 봐야 할 것은 소수 클래스에 초점을 둔 지표다. <strong>Precision-Recall 곡선과 그 아래 면적인 PR-AUC</strong>가 대표적이다. ROC-AUC도 쓰이지만, 음성이 압도적으로 많으면 ROC 곡선은 낙관적으로 보이기 쉽다 — false positive rate의 분모(전체 음성)가 워낙 커서 상당한 오탐도 곡선을 크게 훼손하지 못하기 때문이다. 반면 PR 곡선은 precision을 통해 오탐의 대가를 직접 드러내므로, 희귀 양성을 찾는 문제에서 더 정직한 그림을 준다. 지표를 먼저 바로잡지 않으면 이후의 모든 튜닝이 잘못된 방향을 향한다.

## 2. class_weight — 손실을 다시 저울질한다

가장 손이 덜 가는 대응은 <strong>손실 함수에서 소수 클래스에 가중치를 주는</strong> 것이다. 데이터를 건드리지 않고, 소수 클래스를 틀렸을 때의 벌점만 키운다. 대부분의 sklearn 분류기가 `class_weight` 인자를 지원한다.

```python
from sklearn.linear_model import LogisticRegression

# 클래스 빈도의 역수로 자동 가중
clf = LogisticRegression(class_weight="balanced", max_iter=1000)
clf.fit(X_train, y_train)
```

`class_weight="balanced"`는 각 클래스 가중치를 빈도의 역수에 비례하게 설정해, 소수 클래스 한 건이 손실에 더 크게 기여하도록 만든다. 트리·랜덤 포레스트·SVM에도 동일한 인자가 있다. 데이터 크기를 바꾸지 않아 계산 비용이 늘지 않고 leakage 위험도 없어, 리샘플링보다 먼저 시도할 만한 안전한 선택이다.

## 3. 리샘플링과 SMOTE — CV fold 안에서만

데이터 자체의 균형을 바꾸는 방법도 있다.

- <strong>언더샘플링</strong>: 다수 클래스를 줄인다. 빠르지만 정보를 버린다.
- <strong>오버샘플링</strong>: 소수 클래스를 복제해 늘린다. 단순 복제는 같은 점을 반복 학습하게 해 과적합을 부른다.
- <strong>SMOTE</strong>(Synthetic Minority Over-sampling): 소수 클래스 샘플들 사이를 보간해 <strong>합성 샘플</strong>을 생성한다. 단순 복제보다 결정 경계를 부드럽게 만든다.

SMOTE는 강력하지만 주의점이 많다. 이웃 간 보간이므로 고차원·희소 데이터에서는 의미 없는 합성점을 만들 수 있고, 소수 클래스에 노이즈가 섞여 있으면 그 노이즈까지 증폭한다.

::: warning SMOTE·리샘플링은 반드시 fold 안에서만
리샘플링은 <strong>train fold에만</strong> 적용해야 한다. 전체 데이터를 먼저 SMOTE로 부풀린 뒤 교차 검증하면, 합성 샘플이 원본을 이웃으로 참조하므로 validation fold의 정보가 train으로 새어 들어간다 — 전형적인 leakage다. 검증 점수는 비현실적으로 높아지고 배포 성능은 그에 한참 못 미친다. 반드시 `imblearn`의 `Pipeline`을 써서 SMOTE를 파이프라인 단계로 넣고, CV가 fold마다 train 부분에만 리샘플링을 적용하게 해야 한다. 또한 validation·test는 절대 리샘플링하지 않는다 — 평가는 실제 분포에서 해야 하기 때문이다.
:::

```python
from imblearn.pipeline import Pipeline as ImbPipeline
from imblearn.over_sampling import SMOTE
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import cross_val_score

pipe = ImbPipeline([
    ("smote", SMOTE(random_state=0)),        # fold의 train 부분에만 적용됨
    ("clf", RandomForestClassifier(random_state=0)),
])

scores = cross_val_score(pipe, X_train, y_train, cv=5, scoring="average_precision")
```

`imblearn`의 `Pipeline`은 리샘플링 단계를 fit 때만 동작시키고 predict 때는 건너뛰므로, validation fold가 원본 분포 그대로 평가된다.

## 4. threshold 조정 — 0.5는 규칙이 아니다

분류기는 확률을 출력하고, 관례적으로 0.5를 기준으로 양/음을 나눈다. 하지만 <strong>0.5는 수학적 규칙이 아니라 임의의 기본값</strong>일 뿐이다. 불균형·비용 비대칭 문제에서 최적 임계값은 대개 0.5가 아니다.

핵심은 <strong>오류의 비용이 대칭이 아니라는</strong> 점이다. 사기를 놓치는 비용(false negative)이 정상 거래를 막는 비용(false positive)보다 훨씬 크다면, 임계값을 낮춰 recall을 올리는 게 총비용을 줄인다. threshold는 모델을 다시 학습하지 않고 예측만 바꾸므로, 비용 구조가 정해지면 검증셋에서 곧바로 최적점을 찾을 수 있다.

```python
import numpy as np
from sklearn.metrics import precision_recall_curve

proba = clf.predict_proba(X_valid)[:, 1]
prec, rec, thr = precision_recall_curve(y_valid, proba)

# 비용 기반: FN 비용 10, FP 비용 1 이라고 가정
cost = 10 * (1 - rec[:-1]) + 1 * (1 - prec[:-1])
best_t = thr[np.argmin(cost)]
preds = (proba >= best_t).astype(int)
```

임계값은 반드시 validation에서 정하고 test에서는 그대로 적용만 한다 — test로 임계값을 고르면 그 자체가 test에 대한 튜닝이 되어 성능을 부풀린다.

## 5. probability calibration — 확률을 신뢰할 수 있게

threshold 조정이든 기대비용 계산이든, 모델이 내놓는 확률이 실제 빈도와 맞아야 의미가 있다. "확률 0.8로 예측한 케이스들 중 실제로 약 80%가 양성"일 때 그 확률은 <strong>보정(calibrated)되었다</strong>고 한다. 그런데 많은 모델의 확률 출력은 이 성질을 만족하지 않는다.

이를 진단하는 도구가 <strong>reliability diagram</strong>이다. 예측 확률을 구간으로 나눠, 각 구간의 평균 예측 확률(x축)과 실제 양성 비율(y축)을 찍는다. 완벽히 보정된 모델은 대각선 위에 놓인다.

![신뢰도 곡선 개념도 — x축 예측 확률과 y축 실제 양성 비율 평면에서 완벽 보정은 대각선 점선으로, 대각선 아래로 처지는 곡선은 예측 확률이 실제보다 높은 과신(SVM·부스팅 경향), 대각선 위로 뜨는 곡선은 예측 확률이 실제보다 낮은 과소신(NaiveBayes 경향)을 나타낸다](/images/study-supervised-learning/17-reliability-diagram-light.png)
![신뢰도 곡선 개념도 — x축 예측 확률과 y축 실제 양성 비율 평면에서 완벽 보정은 대각선 점선으로, 대각선 아래로 처지는 곡선은 예측 확률이 실제보다 높은 과신(SVM·부스팅 경향), 대각선 위로 뜨는 곡선은 예측 확률이 실제보다 낮은 과소신(NaiveBayes 경향)을 나타낸다](/images/study-supervised-learning/17-reliability-diagram-dark.png)

모델마다 왜곡 성향이 다르다. 마진 최대화로 학습하는 <strong>SVM</strong>과 exponential loss를 밀어붙이는 <strong>부스팅</strong>은 확률을 극단(0·1)으로 밀어 <strong>과신</strong>하는 경향이 있어 곡선이 대각선 아래로 처진다. 조건부 독립을 강하게 가정하는 <strong>나이브 베이즈</strong>는 반대로 확률을 극단으로 몰지만 방향이 얽혀 곡선이 S자로 뒤틀린다. 로지스틱 회귀는 확률 최적화가 학습 목표라 비교적 잘 보정된 편이다.

보정 방법은 두 가지가 대표적이다.

- <strong>Platt scaling(sigmoid)</strong>: 모델 출력에 시그모이드를 한 겹 학습해 확률로 매핑한다. 파라미터가 두 개뿐이라 데이터가 적어도 안정적이지만, 왜곡이 시그모이드 형태일 때만 잘 맞는다.
- <strong>isotonic regression</strong>: 단조 증가 계단 함수를 자유롭게 학습한다. 표현력이 크지만 그만큼 데이터가 충분해야 하고, 적으면 과적합한다.

sklearn의 `CalibratedClassifierCV`가 두 방법을 감싼다. 내부적으로 교차 검증으로 보정 함수를 학습해, base 모델의 학습 데이터와 보정 데이터가 겹치지 않게 한다.

```python
from sklearn.calibration import CalibratedClassifierCV
from sklearn.svm import SVC

base = SVC(probability=False)   # SVM은 확률 왜곡이 크다
calibrated = CalibratedClassifierCV(base, method="sigmoid", cv=5)
calibrated.fit(X_train, y_train)

proba = calibrated.predict_proba(X_test)[:, 1]   # 보정된 확률
```

데이터가 넉넉하면 `method="isotonic"`이 더 정확한 보정을 주기도 한다. 보정은 순위(AUC)를 거의 바꾸지 않지만, 임계값·기대비용 계산의 신뢰성을 크게 높인다.

## 6. 불균형 대응 우선순위

지금까지의 기법을 한꺼번에 던지면 서로 간섭하고 leakage 위험만 키운다. <strong>간단하고 위험이 낮은 것부터</strong> 단계적으로 올라가는 것이 실전 권장 순서다.

![불균형 대응 우선순위 사다리 — 1단계 지표부터 바꾼다(정확도 폐기, PR-AUC·F1·recall, 비용 기준 정의), 2단계 threshold 조정(기본 0.5는 규칙이 아님, 비용 기반 최적 임계값 탐색), 3단계 class_weight(손실에 소수 클래스 가중, 데이터 안 늘리고 모델만 조정), 4단계 리샘플링(언더/오버·SMOTE, CV fold 안에서만·train에만)이 간단·저위험에서 복잡·고위험 순으로 배치된다](/images/study-supervised-learning/17-imbalance-priority-light.png)
![불균형 대응 우선순위 사다리 — 1단계 지표부터 바꾼다(정확도 폐기, PR-AUC·F1·recall, 비용 기준 정의), 2단계 threshold 조정(기본 0.5는 규칙이 아님, 비용 기반 최적 임계값 탐색), 3단계 class_weight(손실에 소수 클래스 가중, 데이터 안 늘리고 모델만 조정), 4단계 리샘플링(언더/오버·SMOTE, CV fold 안에서만·train에만)이 간단·저위험에서 복잡·고위험 순으로 배치된다](/images/study-supervised-learning/17-imbalance-priority-dark.png)

먼저 지표를 정확도에서 PR-AUC·recall 등으로 바꾸고 비용 구조를 정의한다. 그다음 threshold를 비용 기반으로 조정한다 — 모델을 다시 학습하지 않고도 큰 개선을 얻는 경우가 많다. 여전히 부족하면 `class_weight`로 손실을 조정하고, 그래도 안 되면 마지막에 SMOTE 같은 리샘플링을 fold 안에서 신중히 적용한다. 확률 자체가 의사결정에 쓰인다면 마지막에 calibration을 얹는다. 순서가 뒤집혀 리샘플링부터 손대면, 성능은 애매하게 오르면서 leakage와 확률 왜곡이라는 새 문제를 떠안게 된다.

::: tip 핵심 정리
- 불균형에서 정확도는 다수 클래스에 지배되므로 폐기하고, PR-AUC·recall 등 소수 클래스 지표로 본다.
- `class_weight="balanced"`는 데이터를 안 건드리고 손실만 재조정하는 저위험 1차 대응이다.
- SMOTE·리샘플링은 반드시 `imblearn` 파이프라인으로 CV fold의 train 부분에만 적용하고, validation·test는 원본 분포로 평가한다.
- 임계값 0.5는 임의의 기본값이다. 비용 비대칭을 반영해 validation에서 최적 threshold를 찾는다.
- SVM·부스팅은 과신, 나이브 베이즈는 왜곡이 커 reliability diagram으로 진단하고 Platt scaling·isotonic으로 보정한다.
- 대응은 지표 → threshold → class_weight → 리샘플링 → calibration의 저위험·고위험 순서로 올라간다.
:::

## 다음 챕터

지표를 바로잡고 확률까지 보정했다면, 이제 남은 질문은 "이 모델은 무엇을 근거로 그렇게 예측하는가"다. [모델 해석](/study/supervised-learning/18-model-interpretation)에서는 피처 중요도의 함정, permutation importance, 그리고 SHAP로 개별 예측을 분해해 블랙박스 모델의 판단 근거를 읽어내는 방법을 다룬다.
