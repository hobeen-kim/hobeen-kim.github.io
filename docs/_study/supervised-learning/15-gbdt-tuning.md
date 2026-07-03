---
title: "GBDT 실전 튜닝"
description: "GBDT 하이퍼파라미터를 구조·샘플링·정규화·속도품질 네 역할군으로 정리하고, learning_rate를 낮추고 n_estimators를 키운 뒤 early stopping으로 라운드 수를 자동 결정하는 기본 공식, 검증셋 분리로 leakage를 막는 올바른 early stopping, 과적합 제어 체크리스트, Optuna 튜닝 실전 코드와 튜닝 순서 권장안을 다룬다."
date: 2026-07-03
tags: [Machine Learning, Supervised Learning, GBDT, Hyperparameter Tuning, Optuna, XGBoost]
prev: /study/supervised-learning/14-xgboost-lightgbm-catboost
next: /study/supervised-learning/16-feature-engineering-pipeline
---

# GBDT 실전 튜닝

::: info 학습 목표
- GBDT 하이퍼파라미터를 구조·샘플링·정규화·속도품질의 역할군으로 나눠 이해한다.
- learning_rate를 낮추고 n_estimators를 키운 뒤 early stopping으로 라운드 수를 정하는 기본 공식을 안다.
- early stopping을 올바르게 쓰는 법 — 검증셋 분리와 [leakage 방지](/study/supervised-learning/04-cross-validation-tuning) — 을 익힌다.
- 과적합 신호를 읽고 어떤 손잡이를 어느 방향으로 돌릴지 체크리스트로 정리한다.
- Optuna로 GBDT를 튜닝하는 실전 코드와 권장 튜닝 순서를 안다.
:::

## 1. 하이퍼파라미터를 역할군으로

GBDT의 하이퍼파라미터는 수십 개지만, <strong>역할군</strong>으로 묶으면 손에 잡힌다. 이름은 라이브러리마다 조금씩 다르나([14장](/study/supervised-learning/14-xgboost-lightgbm-catboost) 비교 표 참고) 역할은 같다. 크게 네 묶음이다.

![GBDT 하이퍼파라미터 역할군 지도 — 구조(max_depth·num_leaves·min_child), 샘플링(subsample·colsample), 정규화(reg_lambda·reg_alpha·min_split_gain), 속도-품질(learning_rate·n_estimators·early_stopping) 네 그룹과, 복잡도를 올리고 규제를 낮추면 과적합·반대면 과소적합이 되는 방향축](/images/study-supervised-learning/15-param-groups-light.png)
![GBDT 하이퍼파라미터 역할군 지도 — 구조(max_depth·num_leaves·min_child), 샘플링(subsample·colsample), 정규화(reg_lambda·reg_alpha·min_split_gain), 속도-품질(learning_rate·n_estimators·early_stopping) 네 그룹과, 복잡도를 올리고 규제를 낮추면 과적합·반대면 과소적합이 되는 방향축](/images/study-supervised-learning/15-param-groups-dark.png)

- <strong>구조 (모델 복잡도)</strong> — 트리 하나가 얼마나 복잡해질 수 있는가. `max_depth`(XGBoost/CatBoost), `num_leaves`(LightGBM), 그리고 리프가 되기 위한 최소 데이터·가중치인 `min_child_samples`/`min_child_weight`. 이 묶음이 과적합에 가장 직접적이다. 특히 LightGBM은 leaf-wise라 `num_leaves`가 크면 순식간에 과적합한다 — 대략 `num_leaves < 2^max_depth`를 지키는 것이 안전하다.
- <strong>샘플링 (다양성)</strong> — 각 트리가 데이터·피처의 일부만 보게 해 무작위성을 준다. `subsample`(행 샘플링), `colsample_bytree`(열 샘플링). 값을 0.7~0.9로 낮추면 트리끼리 덜 닮아 일반화가 좋아지고 속도도 붙는다.
- <strong>정규화 (벌점)</strong> — 리프 가중치나 분할 자체에 벌점을 문다. `reg_lambda`(L2), `reg_alpha`(L1), `min_split_gain`(이 이득 미만이면 분할 안 함). 구조 손잡이로 부족할 때 추가로 조이는 용도다.
- <strong>속도-품질 (수렴)</strong> — `learning_rate`(각 트리 기여의 축소 비율)와 `n_estimators`(트리 수). 이 둘이 다음 절의 기본 공식의 주인공이다.

## 2. 기본 공식 — learning_rate ↓, n_estimators ↑, early stopping

GBDT 튜닝에서 <strong>가장 먼저, 그리고 거의 항상 통하는 원칙</strong>은 이것이다.

<strong>learning_rate를 낮추고(예: 0.01~0.05), n_estimators를 크게 잡은 뒤(예: 2000~10000), early stopping으로 실제 라운드 수를 자동 결정한다.</strong>

이유는 [13장](/study/supervised-learning/13-gradient-boosting)의 학습률 개념에서 나온다. learning_rate가 작으면 각 트리가 조금씩만 기여하므로, 더 많은 트리를 더해야 하지만 <strong>더 촘촘하고 안정적으로 수렴</strong>한다. 큰 learning_rate로 트리 수를 줄이면 학습은 빠르지만 최적점을 건너뛰기 쉽다. 그래서 "작은 learning_rate + 충분히 큰 n_estimators"를 깔아두고, 몇 개의 트리가 실제로 필요한지는 <strong>early stopping</strong>에 맡긴다. n_estimators를 손으로 맞출 필요가 사라진다 — 넉넉히 크게 주고 멈춤 시점을 데이터가 정하게 하면 된다.

물론 공짜는 아니다. learning_rate를 낮추면 필요한 트리 수가 늘어 <strong>학습 시간이 길어진다</strong>. 그래서 실무에서는 탐색 단계에서는 0.05 정도로 다소 크게 두어 실험을 빠르게 돌리고, 최종 모델을 만들 때만 0.01~0.02로 낮춰 마지막 성능을 짜내는 2단계 전략을 흔히 쓴다. 속도와 품질 사이의 이 저울질이 곧 역할군 지도에서 learning_rate가 "속도-품질" 묶음에 놓인 이유다.

## 3. early stopping을 올바르게 쓰기

early stopping은 <strong>검증 손실이 일정 라운드(patience) 동안 개선되지 않으면 학습을 멈추고, 검증 손실이 가장 좋았던 시점(best_iteration)의 모델을 채택</strong>하는 기법이다. 트리를 더 추가해도 검증 성능이 나빠지기만 하는 <strong>과적합 시작 지점</strong>을 자동으로 찾아준다.

![early stopping 곡선 — train 손실은 라운드가 늘수록 계속 감소하지만 valid 손실은 감소하다 best_iteration에서 최소를 찍고 다시 상승하며, patience가 소진되는 지점에서 학습을 멈추고 best_iteration의 모델을 채택](/images/study-supervised-learning/15-early-stopping-light.png)
![early stopping 곡선 — train 손실은 라운드가 늘수록 계속 감소하지만 valid 손실은 감소하다 best_iteration에서 최소를 찍고 다시 상승하며, patience가 소진되는 지점에서 학습을 멈추고 best_iteration의 모델을 채택](/images/study-supervised-learning/15-early-stopping-dark.png)

여기서 <strong>가장 흔하고 치명적인 실수</strong>가 [leakage](/study/supervised-learning/04-cross-validation-tuning)다. early stopping의 멈춤 기준이 되는 검증셋은 <strong>모델 선택에 이미 관여</strong>했으므로, 최종 성능 보고에 그대로 쓰면 안 된다. 올바른 구조는 셋을 나누는 것이다.

- <strong>train</strong> — 트리를 학습한다.
- <strong>valid(early stopping 셋)</strong> — 언제 멈출지 결정한다. best_iteration이 여기서 정해진다.
- <strong>test</strong> — 이 둘에 전혀 관여하지 않은 데이터로, 최종 성능만 측정한다.

교차 검증과 함께 쓸 때는 각 폴드 안에서 다시 early stopping용 검증 조각을 떼거나, 폴드의 검증셋을 early stopping과 평가에 동시에 쓰되 <strong>그 폴드가 하이퍼파라미터 탐색에 쓰였다면 최종 일반화 추정에는 별도의 홀드아웃을 남겨</strong> 두어야 한다. "검증셋으로 멈춤 시점을 골랐으면, 그 검증셋 성능은 낙관적으로 부풀려져 있다"는 감각을 항상 유지하라.

patience(멈추기까지 기다릴 라운드 수)는 learning_rate와 함께 본다. learning_rate가 작을수록 개선이 완만하므로 patience도 넉넉히(예: 100~200) 줘야 진짜 정체인지 일시적 정체인지 구분된다. 반대로 너무 크게 잡으면 이미 과적합에 접어든 뒤에도 계속 도는 낭비가 생긴다. 검증 손실 곡선을 한 번 그려 보면 적절한 값이 눈에 들어온다.

## 4. 과적합 신호와 제어 체크리스트

과적합의 신호는 단순하다 — <strong>train 성능은 계속 좋아지는데 valid 성능은 정체하거나 나빠진다</strong>. 두 지표의 격차가 벌어지면 트리가 학습 데이터를 외우고 있다는 뜻이다. 이럴 때 돌릴 손잡이를 역할군 순서로 정리하면 이렇다.

- <strong>구조부터 줄인다</strong> — `max_depth`↓ 또는 `num_leaves`↓, `min_child_samples`↑. 가장 효과가 크고 직접적이다.
- <strong>샘플링으로 다양성을 준다</strong> — `subsample`, `colsample_bytree`를 0.7~0.9로 낮춘다.
- <strong>정규화를 조인다</strong> — `reg_lambda`↑, `reg_alpha`↑, `min_split_gain`↑.
- <strong>learning_rate를 더 낮추고 early stopping에 맡긴다</strong> — 느리지만 안정적인 수렴.
- <strong>데이터를 늘리거나 피처 노이즈를 줄인다</strong> — 튜닝으로 못 메우는 근본 처방.
- <strong>한 번에 하나씩 바꾼다</strong> — 여러 손잡이를 동시에 돌리면 무엇이 효과였는지 알 수 없다. 변경과 검증을 짝지어 기록해 두면 다음 문제에서 감이 쌓인다.

반대로 <strong>과소적합</strong>(train도 valid도 낮음)이면 방향을 뒤집는다 — 구조 복잡도를 키우고, 정규화를 풀고, learning_rate 대비 트리 수를 늘린다. 역할군 지도의 방향축을 그대로 반대로 읽으면 된다.

## 5. Optuna 튜닝 실전

그리드 서치는 조합 폭발로 비효율적이다([04장](/study/supervised-learning/04-cross-validation-tuning) 참고). 실무에서는 <strong>Optuna</strong> 같은 베이지안 최적화로 유망한 영역을 집중 탐색한다. LightGBM을 예로, early stopping과 교차 검증을 결합한 전형적 골격이다.

```python
import optuna
import lightgbm as lgb
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import roc_auc_score
import numpy as np


def objective(trial):
    params = dict(
        objective="binary",
        metric="auc",
        learning_rate=0.02,                     # 낮게 고정
        num_leaves=trial.suggest_int("num_leaves", 16, 255),
        max_depth=trial.suggest_int("max_depth", 3, 12),
        min_child_samples=trial.suggest_int("min_child_samples", 5, 100),
        feature_fraction=trial.suggest_float("feature_fraction", 0.6, 1.0),
        bagging_fraction=trial.suggest_float("bagging_fraction", 0.6, 1.0),
        reg_lambda=trial.suggest_float("reg_lambda", 1e-3, 10.0, log=True),
        reg_alpha=trial.suggest_float("reg_alpha", 1e-3, 10.0, log=True),
        verbose=-1,
    )
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scores = []
    for tr_idx, va_idx in cv.split(X, y):
        dtr = lgb.Dataset(X.iloc[tr_idx], y.iloc[tr_idx])
        dva = lgb.Dataset(X.iloc[va_idx], y.iloc[va_idx])
        model = lgb.train(
            params, dtr, num_boost_round=5000,   # 크게, early stopping이 결정
            valid_sets=[dva],
            callbacks=[lgb.early_stopping(100, verbose=False)],
        )
        pred = model.predict(X.iloc[va_idx], num_iteration=model.best_iteration)
        scores.append(roc_auc_score(y.iloc[va_idx], pred))
    return np.mean(scores)


study = optuna.create_study(direction="maximize")
study.optimize(objective, n_trials=100, timeout=3600)
print("best AUC:", study.best_value)
print("best params:", study.best_params)
```

두 가지가 핵심이다. 첫째, <strong>learning_rate는 탐색 대상에서 빼고 낮게 고정</strong>했다 — 실제 트리 수는 매 trial마다 early stopping이 정한다. 둘째, 점수는 <strong>각 폴드의 best_iteration 예측으로 계산</strong>해 과적합 없는 라운드에서 평가한다. 최종 모델은 best_params로 전체 학습 데이터에 다시 학습하되, 여기서도 별도 검증 조각으로 early stopping을 걸어 트리 수를 정한다.

XGBoost나 CatBoost로 바꿔도 골격은 같다. 탐색 파라미터 이름만 각 라이브러리에 맞추면 된다 — LightGBM의 `num_leaves`/`feature_fraction`/`bagging_fraction` 자리에 XGBoost는 `max_depth`/`colsample_bytree`/`subsample`, CatBoost는 `depth`/`l2_leaf_reg` 등이 들어간다. Optuna는 모델과 무관하게 objective 함수만 갈아 끼우면 그대로 쓸 수 있으니, 세 라이브러리를 같은 탐색 예산으로 비교하는 실험도 어렵지 않다. 탐색 범위는 처음엔 넓게 잡고, 몇십 trial 뒤 best 값 주변으로 좁혀 재탐색하면 예산을 아낄 수 있다.

## 6. 튜닝 순서 권장안

무작정 모든 파라미터를 한꺼번에 넣기보다, 영향이 큰 것부터 좁혀 가는 편이 효율적이다.

- <strong>1단계</strong> — learning_rate를 0.05 정도로 두고 큰 n_estimators + early stopping으로 <strong>베이스라인</strong>을 잡는다. 여기서 나오는 best_iteration과 valid 점수가 이후 비교 기준이다.
- <strong>2단계</strong> — 구조 손잡이(`num_leaves`/`max_depth`, `min_child_samples`)를 먼저 탐색한다. 과적합·과소적합에 가장 큰 영향을 준다.
- <strong>3단계</strong> — 샘플링(`subsample`, `colsample`)과 정규화(`reg_lambda`, `reg_alpha`)로 미세 조정한다.
- <strong>4단계</strong> — 마지막에 learning_rate를 더 낮추고(예: 0.01) n_estimators 상한을 키워 <strong>마무리 한 번</strong> 돌린다. 보통 소폭의 추가 이득이 있다.
- 전 과정에서 <strong>탐색은 넓게, 평가는 항상 같은 교차 검증 프로토콜로</strong> 해 비교 가능성을 유지한다.

## 7. 튜닝보다 피처가 먼저

마지막으로 실무 감각 하나. <strong>하이퍼파라미터 튜닝의 수익은 생각보다 빨리 체감한다</strong>. 잘 짜인 GBDT는 기본값만으로도 상당히 강하고, 튜닝으로 얻는 개선은 보통 몇 퍼센트포인트 안쪽이다. 반면 <strong>좋은 피처 하나</strong>는 그보다 훨씬 큰 도약을 준다 — 도메인 지식이 녹아든 파생 변수, 올바른 인코딩, leakage 없는 집계는 어떤 튜닝보다 효과가 크다.

그래서 순서를 뒤집지 말라. 튜닝에 며칠을 태우기 전에, 피처와 검증 설계에 먼저 시간을 쓰는 것이 거의 항상 더 남는 장사다. 튜닝은 그 위에 올리는 마감재다. 이 이야기가 [16장 피처 엔지니어링과 파이프라인](/study/supervised-learning/16-feature-engineering-pipeline)으로 이어진다.

::: tip 핵심 정리
- 하이퍼파라미터는 구조·샘플링·정규화·속도품질 네 역할군으로 나누면 손에 잡히고, 과적합 제어는 구조 손잡이부터 돌린다.
- 기본 공식은 learning_rate를 낮추고 n_estimators를 크게 잡은 뒤 early stopping으로 실제 라운드 수를 자동 결정하는 것이다.
- early stopping의 검증셋은 모델 선택에 관여하므로, 최종 성능은 그와 분리된 test 셋으로 측정해 leakage를 피한다.
- 과적합 신호는 train↑·valid 정체/악화이며, 구조↓ → 샘플링↓ → 정규화↑ → learning_rate↓ 순으로 대응한다.
- Optuna에서는 learning_rate를 낮게 고정하고 구조·정규화를 탐색하며, 점수는 각 폴드의 best_iteration으로 평가한다.
- 튜닝의 이득은 한계가 뚜렷하다 — 좋은 피처와 올바른 검증 설계가 튜닝보다 먼저다.
:::

## 다음 챕터

튜닝으로 얻는 이득에는 천장이 있고, 그 위를 뚫는 건 결국 피처다. [피처 엔지니어링과 파이프라인](/study/supervised-learning/16-feature-engineering-pipeline)에서는 스케일링·인코딩·결측치 처리를 sklearn Pipeline으로 묶어 leakage 없이 다루는 실전 패턴을 다룬다.
