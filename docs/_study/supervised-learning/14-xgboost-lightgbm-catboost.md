---
title: "XGBoost·LightGBM·CatBoost"
description: "그래디언트 부스팅의 원리가 세 주요 구현체에서 어떻게 진화했는지를 XGBoost의 2차 근사·정규화·결측치 처리, LightGBM의 히스토그램 분할·leaf-wise 성장·GOSS·EFB, CatBoost의 ordered boosting·범주형 네이티브 처리로 짚고, 속도·메모리·범주형·기본값 견고성 비교와 선택 기준을 정리한다."
date: 2026-07-03
tags: [Machine Learning, Supervised Learning, XGBoost, LightGBM, CatBoost, GBDT]
prev: /study/supervised-learning/13-gradient-boosting
next: /study/supervised-learning/15-gbdt-tuning
---

# XGBoost·LightGBM·CatBoost

::: info 학습 목표
- [13장](/study/supervised-learning/13-gradient-boosting)의 그래디언트 부스팅 원리가 실전 구현체에서 어떤 방향으로 진화했는지 이해한다.
- XGBoost의 2차 근사 목적함수, 정규화 항 내장, 결측치 기본 방향 학습, level-wise 성장을 안다.
- LightGBM의 히스토그램 기반 분할, leaf-wise 성장과 num_leaves, GOSS·EFB가 왜 대규모에서 빠른지 이해한다.
- CatBoost의 ordered boosting이 타깃 leakage를 어떻게 완화하는지, 범주형 네이티브 처리의 장점과 함정을 안다.
- 속도·메모리·범주형·기본값 견고성 기준으로 세 구현체를 비교하고 상황별로 고를 수 있다.
:::

## 1. 같은 원리, 다른 진화

세 라이브러리는 모두 [13장](/study/supervised-learning/13-gradient-boosting)에서 다룬 <strong>그래디언트 부스팅</strong>을 구현한다. 즉 약한 학습기(결정 트리)를 순차적으로 더해가며, 각 트리가 앞선 모델의 손실 그래디언트(사실상 잔차)를 학습하는 큰 틀은 동일하다. 그렇다면 왜 세 개나 필요한가. 원리는 같아도 <strong>어떻게 분할점을 찾고, 어떻게 트리를 키우고, 어떻게 과적합을 막고, 범주형을 어떻게 다루느냐</strong>가 다르기 때문이다. 이 차이가 학습 속도, 메모리, 정확도, 손이 가는 정도를 결정한다.

역사적으로는 XGBoost(2014)가 먼저 GBM을 대규모에서 실용화하며 캐글을 지배했고, LightGBM(2017, Microsoft)이 히스토그램과 leaf-wise로 속도를 끌어올렸으며, CatBoost(2017, Yandex)가 범주형과 타깃 leakage 문제를 정면으로 다뤘다. 셋은 경쟁하며 서로의 좋은 아이디어를 흡수해 왔다 — 오늘날 XGBoost도 히스토그램 모드를 지원하고, LightGBM도 범주형을 네이티브로 다룬다. 그래도 각자의 <strong>기본 철학과 기본값</strong>은 여전히 뚜렷하다.

## 2. XGBoost — 정규화된 2차 근사

XGBoost의 핵심 기여는 목적함수를 <strong>2차 테일러 근사</strong>로 전개하고, 거기에 <strong>정규화 항</strong>을 명시적으로 넣은 것이다. 13장의 기본 GBM은 손실의 1차 그래디언트(잔차)만 썼지만, XGBoost는 각 데이터의 1차 그래디언트 `g`와 2차 그래디언트(헤시안) `h`를 함께 사용한다. 그 결과 한 리프의 최적 출력값과 분할 이득(gain)이 닫힌 형태로 유도된다. 이때 목적함수는 대략 <strong>`손실(1차·2차 근사) + γ·(리프 수) + ½λ·(리프 가중치 제곱합)`</strong> 형태가 된다. 여기서 `γ`는 리프를 늘릴 때 무는 벌점, `λ`는 리프 가중치에 대한 L2 벌점이다.

즉 XGBoost는 "손실을 줄이되, 트리가 복잡해지거나 리프 값이 커지면 벌점을 문다"는 원칙을 목적함수 자체에 새겨 넣었다. 이것이 XGBoost가 기본적으로 과적합에 비교적 견고한 이유다.

XGBoost의 다른 두 특징:

- <strong>결측치 기본 방향 학습</strong> — 결측값을 별도로 채우지 않아도, 각 분할에서 결측 샘플을 왼쪽/오른쪽 중 이득이 큰 쪽으로 보내는 <strong>기본 방향(default direction)</strong>을 학습한다. 결측이 정보를 담고 있을 때 이 방식이 단순 대치보다 유리하다.
- <strong>level-wise 성장</strong> — 트리를 깊이 단위로, 같은 레벨의 모든 노드를 함께 확장한다. 균형 잡힌 트리가 되고 `max_depth`로 복잡도를 직관적으로 통제할 수 있다.

![level-wise(XGBoost)와 leaf-wise(LightGBM) 트리 성장 비교 — 왼쪽은 모든 노드를 같은 깊이로 확장해 균형 트리가 되고 max_depth로 제어, 오른쪽은 손실 감소가 가장 큰 잎만 골라 비대칭·깊게 성장하며 num_leaves로 제어](/images/study-supervised-learning/14-tree-growth-light.png)
![level-wise(XGBoost)와 leaf-wise(LightGBM) 트리 성장 비교 — 왼쪽은 모든 노드를 같은 깊이로 확장해 균형 트리가 되고 max_depth로 제어, 오른쪽은 손실 감소가 가장 큰 잎만 골라 비대칭·깊게 성장하며 num_leaves로 제어](/images/study-supervised-learning/14-tree-growth-dark.png)

## 3. LightGBM — 히스토그램과 leaf-wise

LightGBM의 목표는 한마디로 <strong>속도와 메모리</strong>다. 분할점을 찾을 때 XGBoost의 원래 방식(정렬 기반 exact greedy)은 연속 피처의 정렬된 값 사이 모든 지점을 후보로 평가한다 — 정확하지만 데이터가 커지면 느리다. LightGBM은 연속 피처를 미리 <strong>히스토그램(bin)</strong>으로 묶고, bin 경계만 분할 후보로 본다. 후보 수가 `max_bin`(기본 255) 수준으로 줄고, 정렬 대신 히스토그램 누적으로 이득을 계산하므로 메모리와 속도가 크게 개선된다.

![정렬 기반 정확 분할과 히스토그램 기반 분할 비교 — 위쪽은 정렬된 모든 값 사이가 분할 후보(n-1개)라 정확하지만 느리고, 아래쪽은 값을 bin으로 묶어 bin 경계만 후보(max_bin개)로 삼아 메모리·속도를 대폭 개선](/images/study-supervised-learning/14-histogram-split-light.png)
![정렬 기반 정확 분할과 히스토그램 기반 분할 비교 — 위쪽은 정렬된 모든 값 사이가 분할 후보(n-1개)라 정확하지만 느리고, 아래쪽은 값을 bin으로 묶어 bin 경계만 후보(max_bin개)로 삼아 메모리·속도를 대폭 개선](/images/study-supervised-learning/14-histogram-split-dark.png)

트리를 키우는 방식도 다르다. LightGBM은 <strong>leaf-wise(best-first)</strong> 성장을 쓴다 — 현재 리프들 중 손실 감소가 가장 큰 하나만 골라 확장한다. 같은 리프 수라면 leaf-wise가 level-wise보다 손실을 더 줄이므로 정확도가 높은 경향이 있다. 대신 트리가 비대칭적으로 깊어지기 쉬워 <strong>과적합 위험이 크다</strong>. 그래서 LightGBM에서는 `max_depth`보다 <strong>`num_leaves`</strong>가 핵심 복잡도 손잡이다. num_leaves를 키우면 표현력이 오르지만 과적합도 함께 오른다 — [15장](/study/supervised-learning/15-gbdt-tuning)에서 다룰 튜닝의 첫 번째 대상이다.

LightGBM은 대규모 최적화 두 가지를 더 넣었다:

- <strong>GOSS(Gradient-based One-Side Sampling)</strong> — 그래디언트가 큰(즉 아직 잘 못 맞추는) 샘플은 모두 남기고, 그래디언트가 작은 샘플은 일부만 무작위로 추려 학습량을 줄인다. 정보가 많은 샘플에 계산을 집중하는 전략이다.
- <strong>EFB(Exclusive Feature Bundling)</strong> — 원-핫 인코딩처럼 동시에 0이 아닌 값을 거의 갖지 않는(상호 배타적인) 희소 피처들을 하나로 묶어 피처 수를 줄인다. 고차원 희소 데이터에서 특히 효과적이다.

## 4. CatBoost — ordered boosting과 범주형

CatBoost는 두 가지 문제를 정면으로 다룬다. 하나는 <strong>타깃 leakage</strong>, 다른 하나는 <strong>범주형 처리</strong>이며, 사실 둘은 연결돼 있다.

범주형을 수치로 바꾸는 흔한 방법이 <strong>target encoding</strong>(각 범주를 그 범주의 타깃 평균으로 치환)이다. 그런데 어떤 행을 인코딩할 때 <strong>그 행 자신의 타깃까지 평균에 포함</strong>하면, 피처가 정답을 몰래 훔쳐보는 꼴이 된다 — 학습 성능은 좋아 보여도 검증에서 무너지는 전형적 leakage다. 카디널리티가 높은 범주(예: 사용자 ID)일수록 심하다.

CatBoost의 <strong>ordered boosting</strong>은 이 문제를 시간 순서 개념으로 푼다. 데이터에 인위적 순열(ordering)을 부여하고, 각 샘플의 통계량과 그래디언트를 계산할 때 <strong>그 샘플보다 앞에 온 데이터만</strong> 사용한다. 자기 자신의 타깃은 절대 쓰지 않으므로 leakage가 구조적으로 차단된다. 범주형 인코딩도 같은 원리의 <strong>ordered target statistics</strong>로 처리해, 앞선 행들의 타깃만으로 범주 통계를 만든다.

덕분에 CatBoost는 범주형 컬럼을 문자열 그대로 넘겨도 되고(원-핫이나 수동 인코딩 불필요), 기본값이 견고해 튜닝을 거의 하지 않아도 괜찮은 결과가 나오는 경우가 많다. 트리 구조도 특이한데, 모든 분할이 같은 조건을 쓰는 <strong>대칭 트리(oblivious tree)</strong>를 써서 예측이 빠르고 정규화 효과가 있다. 단, ordered boosting은 계산이 무거워 <strong>학습 속도는 LightGBM보다 느린</strong> 경우가 많다는 것이 트레이드오프다.

여기서 실무 함정 하나. CatBoost의 범주형 처리가 편하다고 해서, 다른 라이브러리에서 <strong>직접 target encoding을 할 때도 안전한 것은 아니다</strong>. 직접 인코딩한다면 반드시 교차 검증 폴드 내부에서, 학습 폴드의 타깃만으로 인코딩을 학습해야 한다([04장 leakage](/study/supervised-learning/04-cross-validation-tuning)와 [16장 파이프라인](/study/supervised-learning/16-feature-engineering-pipeline)에서 이어진다). 전체 데이터로 미리 인코딩해 두면 CatBoost가 막으려던 바로 그 leakage를 스스로 만드는 셈이다.

## 5. 세 구현체 비교

| 기준 | XGBoost | LightGBM | CatBoost |
|---|---|---|---|
| 트리 성장 | level-wise (기본) | leaf-wise | 대칭(oblivious) 트리 |
| 복잡도 손잡이 | `max_depth` | `num_leaves` | `depth` |
| 분할 방식 | exact / hist | 히스토그램 (기본) | 히스토그램 |
| 학습 속도 | 중간 (hist는 빠름) | 매우 빠름 | 느린 편 |
| 메모리 | 중간 | 적음 | 중간 |
| 범주형 처리 | 최근 버전 네이티브 지원 | 네이티브 지원 | 네이티브 + ordered TS (최강) |
| 결측치 | 기본 방향 학습 | 기본 방향 학습 | 자동 처리 |
| 기본값 견고성 | 좋음 | 튜닝 필요(num_leaves 민감) | 매우 좋음 |
| 과적합 경향 | 상대적으로 낮음 | 높음(leaf-wise) | 낮음 |
| 대표 강점 | 안정성·생태계 | 대규모 속도 | 범주형·기본값 |

핵심만 요약하면, <strong>속도가 급하고 데이터가 크면 LightGBM</strong>, <strong>범주형이 많고 튜닝에 시간을 덜 쓰고 싶으면 CatBoost</strong>, <strong>안정성과 성숙한 생태계·안전한 기본값이 우선이면 XGBoost</strong>다.

## 6. 선택 기준

몇 가지 축으로 판단하면 결정이 쉬워진다.

- <strong>데이터가 크고 학습을 자주 반복하는가</strong> — LightGBM의 히스토그램·leaf-wise·GOSS 조합이 가장 빠르다. 반복 실험·재학습이 잦은 파이프라인에 유리하다.
- <strong>고카디널리티 범주형이 많은가</strong> — CatBoost가 ordered target statistics로 leakage 없이 처리해 준다. 수동 인코딩의 함정을 피하고 싶을 때 첫 선택지다.
- <strong>튜닝에 쓸 시간이 적은가</strong> — CatBoost의 기본값이 가장 견고하다. XGBoost도 무난하다. LightGBM은 `num_leaves`를 잘못 두면 쉽게 과적합하므로 손이 조금 더 간다.
- <strong>안정성·문서·커뮤니티가 중요한가</strong> — XGBoost가 가장 오래됐고 생태계가 넓다. 프로덕션에서 검증된 기본값이 필요할 때 무난하다.
- <strong>결국 셋 다 비슷하다면</strong> — 세 라이브러리를 같은 검증 셋으로 짧게 돌려보고 고르는 것이 가장 확실하다. tabular에서는 어느 것이 이길지 데이터마다 다르다.

## 7. 세 라이브러리 코드

같은 이진 분류 문제를 세 API로 학습하는 예다. 범주형 처리와 조기 종료 방식의 차이에 주목하라.

::: tabs
@tab XGBoost
```python
import xgboost as xgb
from sklearn.model_selection import train_test_split

X_train, X_val, y_train, y_val = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42)

model = xgb.XGBClassifier(
    n_estimators=2000,
    learning_rate=0.03,
    max_depth=6,            # level-wise 복잡도 손잡이
    subsample=0.8,
    colsample_bytree=0.8,
    reg_lambda=1.0,         # L2 (목적함수 내장)
    tree_method="hist",     # 히스토그램 모드
    early_stopping_rounds=100,
    eval_metric="auc",
)
model.fit(X_train, y_train, eval_set=[(X_val, y_val)], verbose=False)
print("best_iteration:", model.best_iteration)
```
@tab LightGBM
```python
import lightgbm as lgb

train_set = lgb.Dataset(X_train, y_train,
                        categorical_feature=cat_cols)  # 범주형 네이티브
valid_set = lgb.Dataset(X_val, y_val, reference=train_set)

params = dict(
    objective="binary",
    learning_rate=0.03,
    num_leaves=31,          # leaf-wise 핵심 손잡이
    feature_fraction=0.8,   # = colsample
    bagging_fraction=0.8,   # = subsample
    metric="auc",
)
model = lgb.train(
    params, train_set, num_boost_round=2000,
    valid_sets=[valid_set],
    callbacks=[lgb.early_stopping(100), lgb.log_evaluation(0)],
)
print("best_iteration:", model.best_iteration)
```
@tab CatBoost
```python
from catboost import CatBoostClassifier, Pool

train_pool = Pool(X_train, y_train, cat_features=cat_cols)  # 문자열 그대로
val_pool = Pool(X_val, y_val, cat_features=cat_cols)

model = CatBoostClassifier(
    iterations=2000,
    learning_rate=0.03,
    depth=6,                # 대칭 트리 깊이
    l2_leaf_reg=3.0,
    eval_metric="AUC",
    early_stopping_rounds=100,
    verbose=0,
)
model.fit(train_pool, eval_set=val_pool)
print("best_iteration:", model.get_best_iteration())
```
:::

세 코드가 공통으로 쓰는 패턴이 보인다 — <strong>낮은 learning_rate + 큰 n_estimators + early stopping</strong>이다. 이것이 GBDT 튜닝의 기본 공식이며, 다음 장의 핵심 주제다.

::: tip 핵심 정리
- 세 라이브러리는 같은 그래디언트 부스팅 원리를 구현하지만, 분할 탐색·트리 성장·범주형 처리·기본값 철학이 다르다.
- XGBoost는 정규화 항을 넣은 2차 근사 목적함수, 결측치 기본 방향 학습, level-wise 성장으로 안정성이 강점이다.
- LightGBM은 히스토그램 분할과 leaf-wise 성장(num_leaves), GOSS·EFB로 대규모에서 가장 빠르지만 과적합에 주의해야 한다.
- CatBoost는 ordered boosting으로 타깃 leakage를 구조적으로 막고 범주형을 네이티브로 처리해 기본값이 견고하나 학습이 느린 편이다.
- 선택은 데이터 크기(LightGBM), 범주형 비중과 튜닝 시간(CatBoost), 안정성·생태계(XGBoost)를 축으로 판단하고, 애매하면 셋을 직접 비교한다.
- 직접 target encoding을 할 때는 폴드 내부에서만 학습해야 하며, 전체 데이터로 인코딩하면 leakage가 생긴다.
:::

## 다음 챕터

어떤 구현체를 고르든, 성능을 끌어내려면 하이퍼파라미터를 제대로 다뤄야 한다. [GBDT 실전 튜닝](/study/supervised-learning/15-gbdt-tuning)에서는 하이퍼파라미터를 역할군으로 정리하고, learning_rate와 early stopping을 축으로 한 튜닝 공식, 과적합 제어 체크리스트, Optuna 실전 코드를 다룬다.
