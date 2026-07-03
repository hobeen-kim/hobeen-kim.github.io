---
title: "scikit-learn 치트시트"
description: "지도 학습 실무에서 자주 쓰는 scikit-learn 패턴을 코드 예제로 모은 레퍼런스. train_test_split·cross_val_score·StratifiedKFold/GroupKFold/TimeSeriesSplit, Pipeline+ColumnTransformer 골격, GridSearchCV/RandomizedSearchCV, 주요 모델 인스턴스화, 평가 지표, XGBoost/LightGBM/CatBoost early stopping, Optuna 최소 예제까지 다룬다."
date: 2026-07-03
tags: [scikit-learn, XGBoost, LightGBM, CatBoost, Cheatsheet]
prev: /study/supervised-learning/appendix-glossary
next: /study/supervised-learning/appendix-references
---

# scikit-learn 치트시트

지도 학습 실무에서 손에 익혀두면 시간을 아끼는 코드 패턴을 모았다. 개념 배경은 [교차 검증과 튜닝](/study/supervised-learning/04-cross-validation-tuning), [피처 엔지니어링과 파이프라인](/study/supervised-learning/16-feature-engineering-pipeline), [GBDT 실전 튜닝](/study/supervised-learning/15-gbdt-tuning)에서 더 깊이 다룬다. 버전에 따라 인자 이름이 바뀔 수 있으니 최종 확인은 공식 문서로 한다.

## 데이터 분할 — train_test_split

가장 기본이 되는 홀드아웃 분할이다. 분류에서는 클래스 비율을 유지하도록 `stratify`를 반드시 넘긴다.

```python
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42,
    stratify=y,          # 분류: 클래스 비율 유지
)
```

## 교차 검증 — cross_val_score / cross_validate

`cross_val_score`는 단일 지표를, `cross_validate`는 여러 지표와 학습 시간을 함께 돌려준다. `scoring`은 큰 값이 좋은 쪽으로 통일된다(오차 지표는 `neg_` 접두사).

```python
from sklearn.model_selection import cross_val_score, cross_validate

scores = cross_val_score(model, X, y, cv=5, scoring="f1_macro")
print(scores.mean(), scores.std())

results = cross_validate(
    model, X, y, cv=5,
    scoring=["accuracy", "roc_auc"],
    return_train_score=True,     # train/valid 격차로 과적합 진단
)
```

## 교차 검증 분할기 — Stratified / Group / TimeSeries

문제 성격에 맞는 분할기를 `cv`에 직접 넘긴다. 잘못 고르면 leakage로 성능이 부풀려진다.

```python
from sklearn.model_selection import (
    StratifiedKFold, GroupKFold, TimeSeriesSplit,
)

# 불균형 분류: fold마다 클래스 비율 유지
skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# 그룹 누수 방지: 같은 사용자/기기는 한 fold에만
gkf = GroupKFold(n_splits=5)
for tr, va in gkf.split(X, y, groups=groups):
    ...

# 시계열: 과거로 학습, 미래로 검증
tss = TimeSeriesSplit(n_splits=5)
```

## 전처리 파이프라인 — Pipeline + ColumnTransformer

전처리를 모델과 한 객체로 묶으면 교차 검증·튜닝의 매 fold에서 fit이 train에만 적용돼 leakage가 원천 차단된다. 수치·범주 열에 서로 다른 전처리를 병렬로 건다.

```python
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression

num_cols = ["age", "income"]
cat_cols = ["city", "grade"]

num_pipe = Pipeline([
    ("impute", SimpleImputer(strategy="median")),
    ("scale", StandardScaler()),
])
cat_pipe = Pipeline([
    ("impute", SimpleImputer(strategy="most_frequent")),
    ("onehot", OneHotEncoder(handle_unknown="ignore")),
])

pre = ColumnTransformer([
    ("num", num_pipe, num_cols),
    ("cat", cat_pipe, cat_cols),
])

clf = Pipeline([
    ("pre", pre),
    ("model", LogisticRegression(max_iter=1000)),
])
clf.fit(X_train, y_train)
```

## 하이퍼파라미터 탐색 — GridSearchCV / RandomizedSearchCV

Pipeline 스텝 이름에 `__`를 붙여 파라미터를 지정한다. 탐색 공간이 넓으면 Grid보다 Randomized가 효율적이다.

```python
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
from scipy.stats import loguniform

param_grid = {
    "model__C": [0.01, 0.1, 1, 10],
}
gs = GridSearchCV(clf, param_grid, cv=5, scoring="roc_auc", n_jobs=-1)
gs.fit(X_train, y_train)
print(gs.best_params_, gs.best_score_)

param_dist = {
    "model__C": loguniform(1e-3, 1e2),
}
rs = RandomizedSearchCV(
    clf, param_dist, n_iter=50, cv=5,
    scoring="roc_auc", n_jobs=-1, random_state=42,
)
rs.fit(X_train, y_train)
```

## 주요 모델 인스턴스화

베이스라인부터 앙상블까지 한 줄씩 모았다. 대부분 `random_state`를 고정해 재현성을 확보한다.

```python
from sklearn.dummy import DummyClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression, Ridge, Lasso, ElasticNet
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier

dummy = DummyClassifier(strategy="most_frequent")            # 베이스라인
knn   = KNeighborsClassifier(n_neighbors=15, weights="distance")
logit = LogisticRegression(C=1.0, max_iter=1000)
ridge = Ridge(alpha=1.0)                                     # 회귀 L2
lasso = Lasso(alpha=0.01)                                    # 회귀 L1
enet  = ElasticNet(alpha=0.01, l1_ratio=0.5)
svc   = SVC(C=1.0, kernel="rbf", probability=True)
nb    = GaussianNB()
tree  = DecisionTreeClassifier(max_depth=6, random_state=42)
rf    = RandomForestClassifier(n_estimators=400, n_jobs=-1, random_state=42)
gb    = GradientBoostingClassifier(learning_rate=0.05, n_estimators=300)
```

## 평가 지표 함수

혼동 행렬에서 파생되는 분류 지표와 회귀 지표를 함수로 바로 뽑는다. `classification_report`는 클래스별 정밀도·재현율·F1을 한눈에 보여준다.

```python
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score,      # ROC-AUC / PR-AUC
    confusion_matrix, classification_report,
    mean_absolute_error, mean_squared_error, r2_score,
)

y_pred = clf.predict(X_test)
y_prob = clf.predict_proba(X_test)[:, 1]         # 양성 클래스 확률

print(classification_report(y_test, y_pred))
print("ROC-AUC:", roc_auc_score(y_test, y_prob))
print("PR-AUC :", average_precision_score(y_test, y_prob))

# 회귀
rmse = mean_squared_error(y_test, y_pred, squared=False)
print("RMSE:", rmse, "R2:", r2_score(y_test, y_pred))
```

## 임계값 조정

기본 임계값 0.5가 최적인 경우는 드물다. PR 곡선을 훑어 비용에 맞는 임계값을 고른다.

```python
import numpy as np
from sklearn.metrics import precision_recall_curve

prec, rec, thr = precision_recall_curve(y_test, y_prob)
f1 = 2 * prec * rec / (prec + rec + 1e-12)
best_thr = thr[np.argmax(f1[:-1])]               # F1 최대 임계값
y_pred_adj = (y_prob >= best_thr).astype(int)
```

## 확률 캘리브레이션 — CalibratedClassifierCV

트리·SVM 등은 확률이 왜곡되기 쉽다. isotonic(비선형)이나 sigmoid(Platt)로 보정한다.

```python
from sklearn.calibration import CalibratedClassifierCV

calibrated = CalibratedClassifierCV(
    estimator=rf, method="isotonic", cv=5,
)
calibrated.fit(X_train, y_train)
```

## 모델 해석 — permutation importance / SHAP

분할 기반 중요도는 고카디널리티 피처에 편향되므로, 모델 불문인 permutation importance나 SHAP로 교차 검증한다.

```python
from sklearn.inspection import permutation_importance

r = permutation_importance(
    clf, X_test, y_test, n_repeats=10,
    scoring="roc_auc", random_state=42, n_jobs=-1,
)
for i in r.importances_mean.argsort()[::-1]:
    print(X_test.columns[i], round(r.importances_mean[i], 4))

# SHAP (트리 모델)
import shap
explainer = shap.TreeExplainer(rf)
shap_values = explainer.shap_values(X_test)
shap.summary_plot(shap_values, X_test)
```

## XGBoost — early stopping

검증셋을 넘겨 early stopping으로 최적 트리 수를 자동으로 찾는다. sklearn 래퍼에서는 `early_stopping_rounds`를 생성자에 둔다(2.x 기준).

```python
from xgboost import XGBClassifier

xgb = XGBClassifier(
    n_estimators=2000,
    learning_rate=0.03,
    max_depth=6,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_lambda=1.0,
    eval_metric="auc",
    early_stopping_rounds=100,
    n_jobs=-1,
    random_state=42,
)
xgb.fit(X_train, y_train, eval_set=[(X_valid, y_valid)], verbose=False)
print("best_iteration:", xgb.best_iteration)
```

## LightGBM — early stopping

콜백으로 early stopping과 로그 주기를 제어한다. leaf-wise 성장이라 `num_leaves`가 핵심 규제 노브다.

```python
import lightgbm as lgb
from lightgbm import LGBMClassifier, early_stopping, log_evaluation

lgbm = LGBMClassifier(
    n_estimators=3000,
    learning_rate=0.03,
    num_leaves=63,
    subsample=0.8,
    colsample_bytree=0.8,
    reg_lambda=1.0,
    n_jobs=-1,
    random_state=42,
)
lgbm.fit(
    X_train, y_train,
    eval_set=[(X_valid, y_valid)],
    eval_metric="auc",
    callbacks=[early_stopping(100), log_evaluation(0)],
)
```

## CatBoost — early stopping

범주형 피처를 `cat_features`로 직접 넘기면 인코딩 없이 ordered target encoding을 내부에서 처리한다.

```python
from catboost import CatBoostClassifier

cat = CatBoostClassifier(
    iterations=3000,
    learning_rate=0.03,
    depth=6,
    l2_leaf_reg=3.0,
    eval_metric="AUC",
    random_seed=42,
    verbose=0,
)
cat.fit(
    X_train, y_train,
    cat_features=cat_cols,           # 범주형 열 이름/인덱스
    eval_set=(X_valid, y_valid),
    early_stopping_rounds=100,
)
```

## Optuna — 하이퍼파라미터 최적화 최소 예제

베이지안 탐색으로 넓은 공간을 효율적으로 훑는다. objective가 교차 검증 점수를 돌려주게 하고 `study.optimize`로 반복한다.

```python
import optuna
from sklearn.model_selection import cross_val_score

def objective(trial):
    params = {
        "n_estimators": 3000,
        "learning_rate": trial.suggest_float("lr", 1e-3, 0.3, log=True),
        "num_leaves": trial.suggest_int("num_leaves", 15, 255),
        "subsample": trial.suggest_float("subsample", 0.5, 1.0),
        "colsample_bytree": trial.suggest_float("colsample", 0.5, 1.0),
        "reg_lambda": trial.suggest_float("reg_lambda", 1e-3, 10.0, log=True),
    }
    model = LGBMClassifier(**params, n_jobs=-1, random_state=42)
    score = cross_val_score(model, X, y, cv=5, scoring="roc_auc").mean()
    return score

study = optuna.create_study(direction="maximize")
study.optimize(objective, n_trials=50)
print(study.best_params, study.best_value)
```

이어지는 [참고 자료](/study/supervised-learning/appendix-references)에서는 여기 쓴 API의 공식 레퍼런스와 원 논문, 더 깊이 파고들 자료를 모았다.
