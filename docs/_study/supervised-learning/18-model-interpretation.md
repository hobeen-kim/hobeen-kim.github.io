---
title: "모델 해석"
description: "왜 모델을 해석해야 하는지(디버깅·신뢰·규제)를 짚고, 랜덤 포레스트의 impurity 기반 importance가 가진 고카디널리티 편향과 train 기준 함정을 재방문한 뒤, permutation importance·SHAP·PDP·ICE로 전역/국소 해석을 정리하고 'importance는 인과가 아니다'라는 경고로 마무리한다."
date: 2026-07-03
tags: [Machine Learning, Supervised Learning, Interpretability, SHAP, Feature Importance]
prev: /study/supervised-learning/17-imbalanced-calibration
next: /study/supervised-learning/19-model-selection-guide
---

# 모델 해석

::: info 학습 목표
- 모델을 해석해야 하는 실무적 이유(디버깅·신뢰·규제 대응)를 구분해서 설명할 수 있다.
- [랜덤 포레스트](/study/supervised-learning/12-random-forest)의 impurity 기반 importance가 가진 고카디널리티 편향과 train 기준 함정을 다시 짚는다.
- permutation importance를 검증셋 기준으로 계산하는 이유와 상관 피처에서 생기는 착시를 이해한다.
- 협력 게임 이론의 직관으로 SHAP이 개별 예측을 피처 기여로 분해하는 원리를 파악한다.
- TreeSHAP이 GBDT에서 빠른 이유와 summary·dependence·waterfall plot을 읽는 법을 익힌다.
- PDP·ICE로 피처와 예측의 관계를 보고, 전역/국소 해석을 구분하며, "importance는 인과가 아니다"를 새긴다.
:::

## 1. 왜 모델을 해석하는가

성능 좋은 모델을 만들었다고 일이 끝나는 경우는 드물다. 예측이 왜 그렇게 나왔는지 설명하지 못하면, 모델은 실무에서 세 가지 벽에 부딪힌다.

- <strong>디버깅</strong> — 검증 성능은 높은데 배포하면 무너지는 모델은 대개 엉뚱한 신호에 의존한다. 의료 영상 모델이 병변이 아니라 촬영 장비의 워터마크를 학습하거나, 이탈 예측 모델이 "해지 신청 페이지 방문" 같은 <strong>타깃 누수(leakage)</strong> 피처에 붙는 일은 흔하다. 무엇이 예측을 끌고 가는지 봐야 이런 결함을 잡는다.
- <strong>신뢰</strong> — 대출 심사·채용·추천처럼 사람에게 영향을 주는 결정에서는, 담당자와 사용자가 근거를 납득해야 모델을 실제로 쓴다. "점수 0.7"만으로는 아무도 움직이지 않는다.
- <strong>규제</strong> — GDPR의 설명 요구권, 금융권의 모델 리스크 관리 지침처럼 개별 결정의 근거를 제시하도록 요구하는 규제가 늘고 있다. 해석은 선택이 아니라 의무가 되기도 한다.

해석 기법은 크게 <strong>전역(global)</strong> — 모델이 전체적으로 어떤 피처에 의존하는가 — 와 <strong>국소(local)</strong> — 이 한 건의 예측은 왜 이렇게 나왔는가 — 로 나뉜다. 이 구분을 계속 염두에 두면 도구 선택이 쉬워진다.

## 2. impurity 기반 importance의 함정 (12장 재방문)

가장 손쉬운 중요도는 트리 모델이 공짜로 주는 <strong>impurity 기반 importance</strong>(scikit-learn의 `feature_importances_`)다. 각 피처가 분할에서 줄인 불순도(지니·엔트로피·분산)를 학습 과정 내내 합산한 값이다. [12장 랜덤 포레스트](/study/supervised-learning/12-random-forest)에서 이미 경고했듯, 이 값은 두 가지 구조적 편향을 갖는다.

- <strong>고카디널리티 편향</strong> — 값의 종류가 많은 피처(고유 ID, 타임스탬프, 고카디널리티 범주)일수록 분할 후보가 많아, 순수하게 우연으로도 불순도를 더 줄일 기회가 많다. 그래서 예측력이 없는 무작위 ID 컬럼이 상위 중요도로 올라오는 착시가 생긴다. 수치형이 범주형보다, 범주 수가 많은 피처가 적은 피처보다 부풀려진다.
- <strong>train 기준</strong> — impurity 감소는 <strong>학습 데이터</strong>에서 측정된다. 모델이 train에 과적합하며 노이즈를 외운 부분까지 중요도로 계상되므로, 일반화에 기여하지 않는 피처가 높게 나올 수 있다.

```python
# 아무 예측력 없는 무작위 ID 컬럼을 넣어 본다
import numpy as np
X_train["random_id"] = np.arange(len(X_train))   # 고유값 = 행 수
model.fit(X_train, y_train)

imp = model.feature_importances_                  # train 기준·고카디널리티 편향
# random_id가 상위권에 올라오는 착시가 흔히 관찰된다
```

그래서 impurity importance는 "이 모델이 학습 중 무엇을 많이 쪼갰나"는 알려줘도, "이 피처가 진짜 예측에 유용한가"는 신뢰성 있게 답하지 못한다. 방향만 보는 빠른 스케치로는 쓰되, 결론의 근거로 삼지 않는다. 대안이 다음 절의 permutation importance와 SHAP이다.

## 3. permutation importance

<strong>permutation importance</strong>는 발상이 단순하다. 학습을 마친 모델을 고정한 채, <strong>한 피처의 값만 무작위로 섞어(permute)</strong> 그 피처와 타깃의 관계를 끊은 뒤, 성능이 얼마나 떨어지는지 잰다. 많이 떨어지면 모델이 그 피처에 크게 의존했다는 뜻이다. 모델 종류를 가리지 않고(model-agnostic), 실제 예측 성능 저하로 중요도를 정의한다는 점이 impurity 방식과 다르다.

두 가지 원칙이 중요하다.

- <strong>검증셋(혹은 홀드아웃)에서 계산한다</strong> — train에서 재면 impurity와 같은 과적합 함정에 다시 빠진다. 일반화 성능에 대한 기여를 보려면 모델이 학습에 쓰지 않은 데이터에서 섞어야 한다.
- <strong>상관 피처를 주의한다</strong> — 두 피처가 강하게 상관되면, 하나를 섞어도 모델은 나머지 하나에서 같은 정보를 얻어 성능이 거의 안 떨어진다. 결과적으로 둘 다 "안 중요한" 것처럼 나오는 착시가 생긴다. 상관 그룹을 묶어 함께 섞거나, 사전에 상관 구조를 확인하고 해석해야 한다.

```python
from sklearn.inspection import permutation_importance

# model은 이미 학습됨. 반드시 검증셋(X_val, y_val)에서 계산
r = permutation_importance(
    model, X_val, y_val,
    n_repeats=10, scoring="roc_auc", random_state=0)

for i in r.importances_mean.argsort()[::-1]:
    print(f"{X_val.columns[i]:20s} "
          f"{r.importances_mean[i]:.4f} ± {r.importances_std[i]:.4f}")
```

`n_repeats`로 여러 번 섞어 평균과 표준편차를 함께 보면, 편차가 큰(불안정한) 중요도를 걸러낼 수 있다.

## 4. SHAP — 협력 게임에서 예측 분해까지

permutation importance는 "피처가 전체적으로 얼마나 중요한가"라는 <strong>전역</strong> 질문에 답한다. 하지만 "이 고객의 대출이 왜 거절됐나"라는 <strong>국소</strong> 질문에는 개별 예측을 피처별로 쪼개야 한다. 여기에 원리적 답을 주는 것이 <strong>SHAP(SHapley Additive exPlanations)</strong>다.

직관은 <strong>협력 게임 이론</strong>에서 온다. 여러 명이 협력해 얻은 성과(예측값)를 각자의 기여도로 공정하게 나눈다고 하자. 어떤 사람의 기여는 "그가 팀에 합류할 때 성과가 얼마나 늘었는가"를 <strong>가능한 모든 합류 순서에 대해 평균</strong>낸 값으로 정하면 공정하다 — 이것이 <strong>Shapley 값</strong>이다. SHAP은 피처를 이 "참가자"로 보고, <strong>기준값(base value, 전체 평균 예측 E[f(x)])</strong>에서 시작해 각 피처가 예측을 얼마나 밀어올리거나 끌어내렸는지를 Shapley 값으로 계산한다. 그래서 모든 피처 기여의 합이 정확히 "예측값 − 기준값"과 같다는 <strong>가산성(additivity)</strong>이 보장된다.

![SHAP 기여 분해 — 기준값 E[f(x)]=0.30에서 시작해 '소득 상위'(+0.15)·'연체 이력 없음'(+0.10)이 밀어올리고 '재직기간 짧음'(-0.08)이 끌어내린 뒤 '부채비율 낮음'(+0.13)이 더해져 최종 예측 f(x)=0.60에 도달하는 세로 waterfall](/images/study-supervised-learning/18-shap-attribution-light.png)
![SHAP 기여 분해 — 기준값 E[f(x)]=0.30에서 시작해 '소득 상위'(+0.15)·'연체 이력 없음'(+0.10)이 밀어올리고 '재직기간 짧음'(-0.08)이 끌어내린 뒤 '부채비율 낮음'(+0.13)이 더해져 최종 예측 f(x)=0.60에 도달하는 세로 waterfall](/images/study-supervised-learning/18-shap-attribution-dark.png)

문제는 계산량이다. 모든 피처 조합을 따지는 정의를 그대로 쓰면 피처 수에 지수적으로 폭발한다. 그래서 트리 모델 전용으로 이를 다항 시간에 정확히 푸는 <strong>TreeSHAP</strong>이 나왔다. 트리는 각 피처가 어떤 경로에서 어떤 분기에 쓰였는지 구조가 명시적이라, 조합별 기여를 트리를 따라 한 번에 집계할 수 있다. 그래서 XGBoost·LightGBM·CatBoost 같은 GBDT에서 SHAP을 실용적인 속도로 돌릴 수 있고, 이것이 GBDT + SHAP이 tabular 해석의 사실상 표준이 된 이유다.

```python
import shap

explainer = shap.TreeExplainer(model)     # GBDT/RF에 최적화
shap_values = explainer.shap_values(X_val)

shap.summary_plot(shap_values, X_val)     # 전역: 피처별 기여 분포
```

트리 모델이 아니면 어떻게 하나. SHAP은 임의 모델에 쓰는 <strong>KernelSHAP</strong>도 제공한다. 예측 함수만 있으면 되지만, 배경 데이터로 여러 번 예측하며 Shapley 값을 근사하므로 TreeSHAP보다 훨씬 느리고 근사 오차가 있다. 신경망에는 DeepSHAP 같은 전용 변형이 따로 있다. 즉 "정확하고 빠른 SHAP"은 트리 구조 덕에 가능한 것이고, 이 점이 tabular에서 GBDT를 고르는 또 하나의 실무적 이유가 된다.

## 5. SHAP plot 읽는 법

같은 SHAP 값을 세 가지 관점으로 본다.

- <strong>summary plot</strong> — 전역 뷰. 세로축은 중요도 순으로 정렬된 피처, 가로축은 SHAP 값(예측을 밀어올림/끌어내림), 점 하나가 샘플 하나다. 점 색은 그 피처의 값(빨강=큼, 파랑=작음)을 나타내므로, "피처 값이 클수록 예측을 올린다/내린다"는 방향까지 한눈에 읽힌다. permutation importance가 크기만 준다면, summary plot은 크기 + 방향 + 분포를 함께 준다.
- <strong>dependence plot</strong> — 한 피처의 값(가로축)에 따라 그 피처의 SHAP 값(세로축)이 어떻게 변하는지 그린다. 관계가 선형인지, 임계점이 있는지, 어디서 꺾이는지가 보인다. 색으로 상호작용하는 다른 피처를 겹쳐 보면 교호작용도 드러난다.
- <strong>waterfall plot</strong> — 국소 뷰. 한 샘플에 대해 기준값에서 출발해 피처 기여를 하나씩 쌓아 최종 예측에 도달하는 과정을 보여준다(위 다이어그램이 이 형태다). "이 건은 왜 이렇게 예측됐나"를 담당자에게 설명할 때 가장 직관적이다.

## 6. PDP와 ICE

<strong>PDP(Partial Dependence Plot, 부분 의존도)</strong>는 관심 피처를 여러 값으로 바꿔가며 <strong>나머지 피처는 데이터 분포대로 둔 채</strong> 예측을 평균낸다. 그러면 "그 피처가 커질 때 예측이 평균적으로 어떻게 변하나"라는 전역 관계 곡선이 나온다. 다만 평균이라, 하위 그룹마다 방향이 반대인 <strong>교호작용</strong>이 있으면 서로 상쇄돼 밋밋한 곡선으로 뭉개진다.

<strong>ICE(Individual Conditional Expectation)</strong>는 이 평균을 풀어, <strong>샘플 하나하나의 곡선</strong>을 그린다. 곡선들이 나란하면 효과가 균일한 것이고, 서로 엇갈리면 교호작용이 있다는 신호다. PDP는 ICE 곡선들의 평균이므로, 둘을 겹쳐 그리면 전역 경향과 개별 편차를 동시에 볼 수 있다.

```python
from sklearn.inspection import PartialDependenceDisplay

PartialDependenceDisplay.from_estimator(
    model, X_val, features=["부채비율"],
    kind="both")   # PDP(평균) + ICE(개별) 동시 표시
```

PDP·ICE도 permutation처럼 강한 상관 피처에서는 현실에 없는 조합(예: 나이 20세 + 근속 40년)까지 모델에 물어보게 되어 곡선이 왜곡될 수 있다는 점을 기억한다.

## 7. 전역 vs 국소, 그리고 인과가 아니라는 경고

지금까지의 도구를 전역/국소 축에 놓으면 지도가 그려진다. permutation importance·PDP·SHAP summary는 모델 전체의 경향을 보는 <strong>전역</strong> 도구, SHAP waterfall·ICE는 개별 예측을 뜯어보는 <strong>국소</strong> 도구다. SHAP은 같은 값을 전역(summary)과 국소(waterfall)로 모두 볼 수 있어 두 세계를 잇는다. impurity importance는 편향 때문에 이 지도에서 경고 딱지를 달고 있다.

![해석 지도 — 학습된 모델 f(x)를 가운데 두고 왼쪽 전역 해석(permutation importance·PDP·SHAP summary, 그리고 편향 주의 딱지가 붙은 impurity importance)과 오른쪽 국소 해석(SHAP waterfall/force·ICE·LIME)으로 나뉘며 SHAP이 두 세계를 잇는 구조](/images/study-supervised-learning/18-interpretation-map-light.png)
![해석 지도 — 학습된 모델 f(x)를 가운데 두고 왼쪽 전역 해석(permutation importance·PDP·SHAP summary, 그리고 편향 주의 딱지가 붙은 impurity importance)과 오른쪽 국소 해석(SHAP waterfall/force·ICE·LIME)으로 나뉘며 SHAP이 두 세계를 잇는 구조](/images/study-supervised-learning/18-interpretation-map-dark.png)

마지막으로 가장 자주 저지르는 오해를 못박는다. <strong>중요도(importance)는 인과(causation)가 아니다.</strong> SHAP·permutation·PDP가 말하는 것은 "이 모델이 예측을 만들 때 이 피처에 이만큼 의존한다"일 뿐, "이 피처를 바꾸면 결과가 이만큼 바뀐다"가 아니다. 상관되거나 교란된 피처는 인과 없이도 높은 중요도를 받는다. 예컨대 "아이스크림 판매량"이 익사 사고 예측에서 중요하게 나와도, 아이스크림을 금지한다고 사고가 줄지 않는다 — 둘 다 "여름"이라는 교란 변수의 결과다. 모델 해석은 <strong>모델의 동작</strong>을 설명하는 도구이지 <strong>세상의 인과</strong>를 밝히는 도구가 아니며, 정책 결정으로 넘어가려면 별도의 인과 추론이 필요하다.

::: tip 핵심 정리
- 모델 해석은 디버깅(누수·엉뚱한 신호 탐지)·신뢰(근거 제시)·규제(설명 의무) 때문에 필요하다.
- impurity importance는 고카디널리티 편향과 train 기준 함정이 있어(12장 재방문) 빠른 스케치용으로만 쓴다.
- permutation importance는 검증셋에서 계산하고, 상관 피처가 서로의 중요도를 감추는 착시를 조심한다.
- SHAP은 협력 게임의 Shapley 값으로 개별 예측을 기준값 + 피처 기여의 합으로 분해하며, TreeSHAP 덕에 GBDT에서 빠르다.
- summary(전역 방향·분포)·dependence(관계 형태)·waterfall(개별 설명) plot을 목적에 맞게 골라 읽는다.
- PDP·ICE로 피처-예측 관계를 보되, 전역/국소를 구분하고 "importance는 인과가 아니다"를 항상 새긴다.
:::

## 다음 챕터

해석까지 끝내면 이제 "그래서 어떤 모델을 언제 쓰나"를 정리할 차례다. [모델 선택 실전 가이드](/study/supervised-learning/19-model-selection-guide)에서는 문제 특성별 선택 기준, tabular에서 GBDT가 여전히 강한 이유, 딥러닝으로 넘어가는 경계, 그리고 스터디 전체를 관통하는 실무 워크플로우를 정리한다.
