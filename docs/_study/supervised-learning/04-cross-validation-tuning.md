---
title: "교차 검증과 하이퍼파라미터 튜닝"
description: "hold-out 한 번의 분할이 왜 불안정한지에서 출발해 k-fold와 stratified k-fold, 그리고 실무 leakage의 1순위 원인인 잘못된 분할을 막는 GroupKFold·TimeSeriesSplit을 다룬다. 전처리·타깃 leakage 유형, grid/random/bayesian(Optuna) 탐색, 파라미터와 하이퍼파라미터 구분, 튜닝이 평가를 오염시키지 않게 하는 중첩 교차 검증까지 정리한다."
date: 2026-07-03
tags: [Machine Learning, Supervised Learning, Cross Validation, Hyperparameter Tuning, Data Leakage, Optuna]
prev: /study/supervised-learning/03-evaluation-metrics
next: /study/supervised-learning/05-knn
---

# 교차 검증과 하이퍼파라미터 튜닝

::: info 학습 목표
- hold-out 한 번의 분할이 왜 불안정한지 이해하고 k-fold가 이를 어떻게 완화하는지 안다.
- stratified k-fold, GroupKFold, TimeSeriesSplit을 언제 써야 하는지 구분한다.
- 실무 leakage의 1순위 원인이 잘못된 분할임을 이해하고 전처리·타깃 leakage를 막는다.
- grid / random / bayesian(Optuna) 탐색의 트레이드오프를 파악한다.
- 파라미터와 하이퍼파라미터를 구분하고, 튜닝이 평가를 오염시키지 않는 중첩 교차 검증을 안다.
:::

## 1. hold-out 한 번의 분할은 불안정하다

[02장](/study/supervised-learning/02-generalization-overfitting)에서 데이터를 train/valid/test로 나눠 일반화를 측정했다. 그런데 데이터가 수천 건 수준이면 <strong>단 한 번의 분할(hold-out)</strong>로 얻은 점수는 운에 크게 흔들린다. 어떤 샘플이 우연히 검증셋에 몰렸느냐에 따라 정확도가 몇 %p씩 오르내리고, 그 점수 하나로 모델 A가 B보다 낫다고 결론 내리면 재현되지 않는다.

<strong>k-fold 교차 검증(cross validation)</strong>은 데이터를 k개 폴드로 나눠, 각 폴드를 한 번씩 검증셋으로 쓰고 나머지 k-1개로 학습한다. k번의 점수를 평균 내면 분할 운의 영향이 줄고, 표준편차로 안정성까지 볼 수 있다. 대신 학습을 k번 반복하므로 비용은 k배다.

```python
from sklearn.model_selection import cross_val_score, KFold
from sklearn.ensemble import RandomForestClassifier

kf = KFold(n_splits=5, shuffle=True, random_state=42)
scores = cross_val_score(RandomForestClassifier(), X, y, cv=kf, scoring="f1")
print(f"{scores.mean():.3f} ± {scores.std():.3f}")  # 평균과 흔들림을 함께 본다
```

## 2. stratified k-fold — 클래스 비율을 지킨다

분류에서 단순 KFold로 무작위 분할하면 폴드마다 클래스 비율이 흔들린다. 양성 클래스가 5%인 불균형 데이터라면 어떤 폴드에는 양성이 거의 안 들어가 [03장](/study/supervised-learning/03-evaluation-metrics)에서 본 F1 같은 지표가 요동친다. <strong>StratifiedKFold</strong>는 각 폴드가 전체와 같은 클래스 비율을 유지하도록 나눈다. sklearn의 분류용 `cross_val_score`는 기본으로 stratified를 쓴다.

```python
from sklearn.model_selection import StratifiedKFold

skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
scores = cross_val_score(model, X, y, cv=skf, scoring="roc_auc")
```

분류에서는 특별한 이유가 없으면 stratified가 기본값이라고 생각하면 된다.

## 3. GroupKFold·TimeSeriesSplit — leakage 1순위는 잘못된 분할

여기가 이 장에서 가장 중요하다. 실무에서 검증 점수는 높은데 배포하면 무너지는 사고의 <strong>1순위 원인은 모델이 아니라 잘못된 분할</strong>이다. 무작위 k-fold는 "모든 행이 서로 독립"이라는 가정을 깔고 있는데, 현실 데이터는 그렇지 않은 경우가 많다.

<strong>유저 단위 데이터 — GroupKFold.</strong> 한 유저가 여러 행을 갖는 데이터(세션 로그, 반복 측정, 환자별 여러 검사)를 무작위로 나누면, 같은 유저의 일부는 train에 일부는 검증에 들어간다. 모델은 그 유저의 습관을 train에서 외워 검증에서 맞히므로 점수가 부풀고, 정작 <strong>본 적 없는 새 유저</strong>에는 약하다. GroupKFold는 같은 그룹(유저)이 통째로 한 폴드에만 들어가도록 보장한다.

<strong>시계열 — TimeSeriesSplit.</strong> 시간 순서가 있는 데이터를 무작위로 섞으면 미래로 학습해 과거를 맞히는 꼴이 된다. TimeSeriesSplit은 항상 과거로 학습하고 그 뒤 구간으로 검증하며, 검증 이후의 미래는 쓰지 않는다.

![세 가지 교차 검증 분할 전략 비교 — KFold는 검증 블록이 순서대로 회전하는 무작위 균등 분할, GroupKFold는 같은 그룹(A·B·C·D 유저)이 통째로 한 폴드에만 검증으로 들어가 그룹이 train과 검증에 쪼개지지 않음, TimeSeriesSplit은 앞쪽 과거를 train으로 쓰고 바로 뒤 구간을 검증으로 쓰며 그보다 미래 구간은 미사용으로 비워 두는 확장 윈도우 방식](/images/study-supervised-learning/04-cv-strategies-light.png)
![세 가지 교차 검증 분할 전략 비교 — KFold는 검증 블록이 순서대로 회전하는 무작위 균등 분할, GroupKFold는 같은 그룹(A·B·C·D 유저)이 통째로 한 폴드에만 검증으로 들어가 그룹이 train과 검증에 쪼개지지 않음, TimeSeriesSplit은 앞쪽 과거를 train으로 쓰고 바로 뒤 구간을 검증으로 쓰며 그보다 미래 구간은 미사용으로 비워 두는 확장 윈도우 방식](/images/study-supervised-learning/04-cv-strategies-dark.png)

```python
from sklearn.model_selection import GroupKFold, TimeSeriesSplit

# 유저 단위: groups에 유저 id를 넘기면 같은 유저는 한 폴드에만 들어간다
gkf = GroupKFold(n_splits=5)
scores = cross_val_score(model, X, y, groups=user_ids, cv=gkf)

# 시계열: 시간순으로 정렬된 데이터에 대해 과거→미래로만 검증
tss = TimeSeriesSplit(n_splits=5)
scores = cross_val_score(model, X_sorted_by_time, y_sorted, cv=tss)
```

::: warning 분할 기준을 먼저 정하라
모델을 고르기 전에 "이 데이터의 행들은 서로 독립인가, 아니면 유저·시간·매장 같은 공유 구조가 있는가"를 먼저 물어야 한다. 분할이 배포 상황(새 유저·미래 시점)을 흉내 내지 못하면, 아무리 좋은 모델도 검증 점수만 화려하고 실전에서 무너진다.
:::

## 4. data leakage 유형

leakage는 <strong>학습 시점에 알 수 없어야 할 정보가 모델에 새어 든 것</strong>이다. 잘못된 분할(3절) 외에 두 유형이 흔하다.

<strong>전처리 leakage.</strong> 스케일링·결측치 대치·인코딩 같은 전처리를 <strong>분할 전에 전체 데이터로</strong> 하면, 검증셋의 평균·분산 같은 통계가 train에 스며든다. 반드시 각 폴드의 train으로만 전처리를 학습(`fit`)하고 검증셋에는 적용(`transform`)만 해야 한다. sklearn `Pipeline`으로 묶어 `cross_val_score`에 넘기면 폴드마다 전처리가 train에만 fit되어 이 문제가 자동으로 막힌다([16장](/study/supervised-learning/16-feature-engineering-pipeline)에서 심화).

```python
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

# 스케일러가 각 폴드의 train에만 fit → 전처리 leakage 방지
pipe = make_pipeline(StandardScaler(), model)
scores = cross_val_score(pipe, X, y, cv=skf)
```

<strong>타깃 leakage.</strong> 예측 시점에는 존재하지 않는, 정답과 사실상 같은 피처가 섞인 경우다. "해지 여부"를 예측하는데 "해지 사유 코드"가 피처로 들어가 있거나, 미래에야 채워지는 값이 과거 행에 들어간 경우다. 점수가 비현실적으로 높으면(예: AUC 0.99) 성능을 기뻐하기 전에 타깃 leakage부터 의심해야 한다.

## 5. 파라미터 vs 하이퍼파라미터

둘을 구분해야 튜닝의 대상이 분명해진다.

- <strong>파라미터(parameter)</strong>는 <strong>학습으로 데이터에서 추정</strong>되는 값이다. 선형 회귀의 가중치, 트리의 분할 기준이 여기 속한다. 사람이 정하지 않는다.
- <strong>하이퍼파라미터(hyperparameter)</strong>는 <strong>학습 전에 사람이 정하는</strong> 설정값이다. k-NN의 k, 트리의 최대 깊이, 정규화 강도, 학습률이 여기 속한다. 이걸 데이터에 맞게 고르는 작업이 튜닝이다.

핵심 규칙: 하이퍼파라미터는 <strong>test셋을 절대 보지 않고</strong> 골라야 한다. test로 튜닝하면 그 점수는 더 이상 일반화 성능이 아니다. 그래서 교차 검증의 검증 점수로 하이퍼파라미터를 고른다.

## 6. 탐색 전략 — grid / random / bayesian

하이퍼파라미터 조합을 어떻게 뒤질 것인가.

- <strong>Grid search</strong>는 후보 값을 격자로 만들어 모든 조합을 시험한다. 재현성 있고 단순하지만 하이퍼파라미터가 늘면 조합 수가 폭발한다(차원의 저주).
- <strong>Random search</strong>는 정해진 예산만큼 무작위로 뽑아 시험한다. 중요한 하이퍼파라미터가 소수일 때, 같은 예산으로 grid보다 좋은 값을 자주 찾는다([Bergstra & Bengio, 2012](https://www.jmlr.org/papers/v13/bergstra12a.html)).
- <strong>Bayesian optimization</strong>은 지금까지의 시도 결과로 "좋아 보이는 영역"을 추정해 다음 시도를 그쪽으로 몬다. [Optuna](https://optuna.org/) 같은 도구가 대표적이며, 평가 비용이 비싼 GBDT 튜닝에서 특히 효율적이다.

![grid·random·bayesian 탐색이 두 하이퍼파라미터 공간에서 시험하는 지점 분포 비교 — Grid Search는 규칙적인 격자 위 점들, Random Search는 공간 전체에 넓게 흩뿌려진 점들, Bayesian은 초반에 몇 점을 탐색한 뒤 진짜 최적점(별) 근방으로 시도가 점점 몰리는 분포](/images/study-supervised-learning/04-search-methods-light.png)
![grid·random·bayesian 탐색이 두 하이퍼파라미터 공간에서 시험하는 지점 분포 비교 — Grid Search는 규칙적인 격자 위 점들, Random Search는 공간 전체에 넓게 흩뿌려진 점들, Bayesian은 초반에 몇 점을 탐색한 뒤 진짜 최적점(별) 근방으로 시도가 점점 몰리는 분포](/images/study-supervised-learning/04-search-methods-dark.png)

```python
from sklearn.model_selection import RandomizedSearchCV
from scipy.stats import randint

search = RandomizedSearchCV(
    RandomForestClassifier(),
    param_distributions={"max_depth": randint(3, 20),
                         "n_estimators": randint(100, 500)},
    n_iter=30, cv=skf, scoring="f1", random_state=42)
search.fit(X, y)
print(search.best_params_, search.best_score_)
```

```python
import optuna  # bayesian: 과거 시도를 반영해 유망한 영역을 집중 탐색

def objective(trial):
    params = {"max_depth": trial.suggest_int("max_depth", 3, 20),
              "n_estimators": trial.suggest_int("n_estimators", 100, 500)}
    return cross_val_score(RandomForestClassifier(**params), X, y,
                           cv=skf, scoring="f1").mean()

study = optuna.create_study(direction="maximize")
study.optimize(objective, n_trials=30)
```

## 7. 중첩 교차 검증 (nested CV)

같은 교차 검증 점수로 하이퍼파라미터를 고르고 그 점수를 다시 성능으로 보고하면, 검증셋에 맞춰 튜닝한 만큼 점수가 낙관적으로 부풀어 있다. <strong>중첩 교차 검증</strong>은 두 역할을 분리한다. 바깥 루프는 성능을 <strong>평가</strong>하고, 각 바깥-train 안의 안쪽 루프가 하이퍼파라미터를 <strong>선택</strong>한다. 튜닝은 바깥의 test를 한 번도 보지 않으므로 평가가 오염되지 않는다.

![중첩 교차 검증의 두 루프 구조 — 바깥 루프는 데이터를 여러 바깥 폴드로 나눠 각 폴드를 test로 성능을 평가하고, 각 바깥-train 영역을 다시 안쪽 k-fold로 쪼개 후보 하이퍼파라미터를 검증한 뒤 최적값을 골라 바깥-train 전체로 재학습하는 흐름](/images/study-supervised-learning/04-nested-cv-light.png)
![중첩 교차 검증의 두 루프 구조 — 바깥 루프는 데이터를 여러 바깥 폴드로 나눠 각 폴드를 test로 성능을 평가하고, 각 바깥-train 영역을 다시 안쪽 k-fold로 쪼개 후보 하이퍼파라미터를 검증한 뒤 최적값을 골라 바깥-train 전체로 재학습하는 흐름](/images/study-supervised-learning/04-nested-cv-dark.png)

```python
from sklearn.model_selection import GridSearchCV, cross_val_score

inner = StratifiedKFold(n_splits=3, shuffle=True, random_state=1)
outer = StratifiedKFold(n_splits=5, shuffle=True, random_state=2)

# 안쪽: 하이퍼파라미터 선택 / 바깥: 편향 없는 성능 추정
clf = GridSearchCV(model, param_grid, cv=inner, scoring="f1")
nested_scores = cross_val_score(clf, X, y, cv=outer, scoring="f1")
print(f"편향 없는 추정: {nested_scores.mean():.3f} ± {nested_scores.std():.3f}")
```

중첩 CV는 비용이 크므로 항상 쓰지는 않는다. "이 모델·튜닝 절차의 진짜 성능이 얼마인가"를 정직하게 보고해야 하는 논문·벤치마크·모델 비교 상황에서 특히 유용하다. 실무에서는 바깥 hold-out test 한 벌 + 안쪽 교차 검증 튜닝의 조합으로 타협하는 경우가 많다.

::: tip 핵심 정리
- hold-out 한 번의 분할은 운에 흔들리므로, k-fold로 여러 번 나눠 평균과 표준편차로 안정성을 본다.
- 분류는 StratifiedKFold로 폴드마다 클래스 비율을 지키는 것이 기본이다.
- 실무 leakage의 1순위는 잘못된 분할이다 — 유저 단위는 GroupKFold, 시계열은 TimeSeriesSplit으로 배포 상황을 흉내 내야 한다.
- 전처리는 Pipeline으로 폴드 train에만 fit해 leakage를 막고, 비현실적으로 높은 점수는 타깃 leakage를 의심한다.
- 하이퍼파라미터는 test를 보지 않고 검증 점수로 고르며, grid→random→bayesian(Optuna) 순으로 예산 효율이 좋아진다.
- 튜닝 점수를 그대로 성능으로 보고하면 낙관 편향이 생기므로, 정직한 평가가 필요하면 중첩 교차 검증을 쓴다.
:::

## 다음 챕터

교차 검증과 leakage 없는 튜닝이라는 안전한 실험 틀을 갖췄으니, 이제 실제 모델로 들어간다. [kNN](/study/supervised-learning/05-knn)은 "학습이 없는" 가장 직관적인 모델로, 거리 계산과 스케일링·차원의 저주를 통해 이후 모든 거리 기반·선형 모델의 기초 감각을 잡아 준다.
