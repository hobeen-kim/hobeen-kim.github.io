---
title: "피처 엔지니어링과 파이프라인"
description: "모델보다 피처가 성능을 좌우한다는 관점에서 수치형 스케일링·범주형 인코딩·결측치 처리·파생 피처를 정리하고, sklearn Pipeline과 ColumnTransformer로 전처리 leakage를 원천 차단하며 교차 검증 안에 파이프라인을 통째로 넣는 실전 구성을 다룬다."
date: 2026-07-03
tags: [SupervisedLearning, FeatureEngineering, Pipeline, ColumnTransformer, Sklearn]
prev: /study/supervised-learning/15-gbdt-tuning
next: /study/supervised-learning/17-imbalanced-calibration
---

# 피처 엔지니어링과 파이프라인

::: info 학습 목표
- 모델 선택보다 피처 표현이 성능을 더 크게 좌우하는 경우가 많다는 점을 이해한다.
- 수치형 스케일링의 종류와, 모델별로 스케일링이 필수인지 무의미한지를 구분한다.
- 범주형 인코딩(원핫·ordinal·target encoding)의 선택 기준과 target encoding의 leakage 위험을 안다.
- 결측치를 단순 대치·지시자·트리 계열 네이티브 처리로 다루는 방법을 비교한다.
- 날짜 분해·집계·상호작용 같은 파생 피처 설계의 기본 패턴을 익힌다.
- sklearn `Pipeline`과 `ColumnTransformer`로 전처리를 캡슐화해 leakage를 원천 차단하고, 그 파이프라인을 교차 검증 안에 통째로 넣는다.
:::

## 1. 피처가 성능을 좌우한다

같은 데이터셋에 같은 알고리즘을 써도, 피처를 어떻게 표현하느냐에 따라 성능은 크게 갈린다. 로그 스케일이 자연스러운 변수를 그대로 넣으면 선형 모델이 관계를 못 잡고, 날짜를 문자열로 두면 요일·계절 신호가 통째로 버려진다. 반대로 잘 설계된 파생 피처 하나가 하이퍼파라미터 튜닝 며칠보다 큰 이득을 주기도 한다. 그래서 실무의 상당 부분은 "어떤 모델을 쓸까"가 아니라 "데이터를 모델이 이해할 수 있는 형태로 어떻게 바꿀까"에 쓰인다.

핵심은 <strong>전처리도 학습의 일부</strong>라는 관점이다. 스케일러의 평균·분산, 인코더가 본 범주 목록, 결측 대치에 쓰는 중앙값 — 이 모든 것은 데이터로부터 <strong>학습되는 파라미터</strong>다. 따라서 이들은 반드시 train에서만 학습되어야 하며, 이 원칙이 무너지는 순간 [4장 교차 검증](/study/supervised-learning/04-cross-validation-tuning)에서 경계했던 leakage가 전처리 단계에서 발생한다. 이 장의 절반은 피처를 어떻게 만들지, 나머지 절반은 그 전처리를 어떻게 leakage 없이 배치할지를 다룬다.

## 2. 수치형 스케일링 — 모델에 따라 필수이거나 무의미하다

수치형 피처의 스케일을 맞추는 대표적인 방법은 세 가지다.

- <strong>StandardScaler</strong>: 평균 0, 분산 1로 표준화한다. 대체로 무난한 기본값이다.
- <strong>MinMaxScaler</strong>: 정해진 범위(보통 0~1)로 선형 압축한다. 분포 모양은 그대로 두되 경계가 명확해야 할 때 쓴다.
- <strong>RobustScaler</strong>: 중앙값과 IQR을 기준으로 조정해 이상치의 영향을 덜 받는다.

중요한 건 <strong>스케일링이 모든 모델에 필요한 게 아니다</strong>라는 점이다. 거리·내적에 기반한 모델은 스케일에 민감하다. [5장 kNN](/study/supervised-learning/05-knn)은 유클리드 거리로 이웃을 찾으므로 스케일이 큰 피처가 거리를 지배해버리고, 선형·로지스틱 회귀나 SVM, 그리고 정규화가 걸린 모델은 계수와 페널티가 스케일에 얽혀 있어 스케일링이 사실상 필수다. 반면 <strong>트리 계열</strong>(결정 트리·랜덤 포레스트·GBDT)은 각 피처를 독립적으로 임계값 기준으로 분할하기 때문에, 단조 변환에 불변이고 스케일링을 해도 결과가 바뀌지 않는다. 트리 모델에 StandardScaler를 붙이는 건 해롭지는 않아도 무의미한 연산이다.

## 3. 범주형 인코딩

범주형 변수는 숫자로 바꿔야 대부분의 모델이 받아들인다. 방식에 따라 성격이 다르다.

- <strong>One-Hot Encoding</strong>: 각 범주를 0/1 더미 컬럼으로 편다. 순서가 없는 명목형에 안전한 기본값이다. 카디널리티(범주 수)가 크면 컬럼이 폭발하는 게 단점이다.
- <strong>Ordinal Encoding</strong>: 범주를 정수로 매핑한다. `저 < 중 < 고`처럼 <strong>실제 순서가 있는</strong> 순서형에 적합하다. 순서 없는 변수에 쓰면 모델이 존재하지 않는 대소 관계를 학습해버린다. 다만 트리 계열은 정수 인코딩된 범주도 분할로 잘라내므로 ordinal을 실용적으로 쓰기도 한다.
- <strong>Target Encoding</strong>: 각 범주를 그 범주의 타깃 평균(예: 범주별 양성 비율)으로 치환한다. 고카디널리티 변수를 한 컬럼으로 압축하면서 신호를 살리는 강력한 방법이지만, <strong>타깃을 직접 쓰기 때문에 leakage 위험이 가장 크다</strong>.

::: warning target encoding의 leakage
target encoding은 인코딩 값 자체가 타깃에서 유도되므로, 전체 데이터로 한 번에 인코딩하면 각 행이 자기 자신의 타깃 정보를 피처로 들여다보게 된다. 반드시 <strong>교차 검증 fold 안에서 train 부분으로만 통계를 계산</strong>하거나, out-of-fold 방식·스무딩을 적용해야 한다. sklearn의 `TargetEncoder`는 내부적으로 교차 적합(cross-fitting)으로 이 위험을 완화하지만, 그래도 파이프라인에 넣어 CV 밖으로 통계가 새지 않게 하는 것이 안전하다.
:::

## 4. 결측치 처리

결측을 다루는 방법은 크게 세 갈래다.

첫째, <strong>단순 대치(imputation)</strong>다. 수치형은 평균·중앙값, 범주형은 최빈값이나 `"MISSING"` 같은 상수로 채운다. `SimpleImputer`가 담당하며, 중앙값 대치는 이상치에 강해 수치형의 무난한 선택이다.

둘째, <strong>결측 지시자(indicator)</strong>다. "이 값이 원래 결측이었다"는 사실 자체가 신호일 때가 많다. 예를 들어 소득 미기재가 특정 집단과 상관될 수 있다. `SimpleImputer(add_indicator=True)`로 대치와 동시에 결측 여부 이진 컬럼을 추가하면 이 정보를 모델에 남길 수 있다.

셋째, <strong>트리 계열의 네이티브 처리</strong>다. LightGBM·XGBoost·HistGradientBoosting 등은 결측을 별도 값으로 취급해 분할 시 어느 쪽으로 보낼지 스스로 학습한다. 이 경우 억지로 대치하지 않고 결측을 그대로 두는 편이 더 나을 수 있다. 어떤 방식이든 대치에 쓰는 통계(평균·중앙값)는 train에서만 계산해야 하므로, 결측 처리 역시 파이프라인 안에 넣어야 한다.

## 5. 파생 피처

원본 컬럼을 조합·변형해 새 신호를 만드는 것이 파생 피처다. 자주 쓰는 패턴은 다음과 같다.

- <strong>날짜 분해</strong>: 타임스탬프에서 연·월·요일·시간대·주말 여부·공휴일 여부를 뽑아낸다. 주기성(요일·계절)은 sin/cos 변환으로 순환 구조를 보존하기도 한다.
- <strong>집계</strong>: 그룹 단위 통계를 붙인다. 사용자별 과거 구매 횟수·평균 결제액, 상품별 최근 판매량처럼 엔티티의 이력을 요약한다. 시계열이라면 미래 정보가 섞이지 않도록 시점 기준을 엄격히 지켜야 한다.
- <strong>상호작용</strong>: 두 변수의 곱·비율·차이를 만든다. `면적 = 가로 × 세로`, `단가 = 총액 / 수량`처럼 도메인 지식이 담긴 조합은 선형 모델에서 특히 효과가 크다.
- <strong>비선형 변환</strong>: 왜도가 큰 변수에 로그·제곱근을 적용해 분포를 완만하게 만든다.

파생 피처는 도메인 이해에서 나오지만, 만든 뒤에는 반드시 검증셋에서 실제로 성능을 올리는지 확인해야 한다. 무작정 늘린 피처는 차원만 키우고 과적합을 부른다.

## 6. Pipeline과 ColumnTransformer — leakage 원천 차단

이 장의 중심이다. 지금까지의 전처리는 모두 "데이터로부터 무언가를 학습(fit)"한다. 그리고 그 학습은 <strong>오직 train에서만</strong> 일어나야 한다. 문제는 실무에서 흔히 저지르는 실수 — 전체 데이터에 스케일러·인코더를 먼저 fit해두고 그다음에 train/test로 나누는 것 — 가 바로 이 원칙을 깬다는 점이다.

![전처리 leakage 비교 — 위쪽은 전체 데이터에 scaler·encoder를 먼저 fit_transform한 뒤 train/test split하고 학습·평가해서 test 통계가 전처리에 새어 낙관적 점수가 나오는 잘못된 순서, 아래쪽은 먼저 train/test split한 뒤 train에만 fit하고 test는 transform만 적용하는 올바른 순서](/images/study-supervised-learning/16-leakage-order-light.png)
![전처리 leakage 비교 — 위쪽은 전체 데이터에 scaler·encoder를 먼저 fit_transform한 뒤 train/test split하고 학습·평가해서 test 통계가 전처리에 새어 낙관적 점수가 나오는 잘못된 순서, 아래쪽은 먼저 train/test split한 뒤 train에만 fit하고 test는 transform만 적용하는 올바른 순서](/images/study-supervised-learning/16-leakage-order-dark.png)

전체 데이터로 스케일러를 fit하면 test의 평균·분산이 스케일링에 반영되고, 전체로 target encoding을 하면 test의 타깃이 인코딩 값에 스며든다. 그 결과 검증 점수는 실제 배포 성능보다 낙관적으로 부풀고, 모델 선택 자체가 틀어진다.

`Pipeline`은 전처리 단계와 최종 추정기를 하나의 객체로 묶는다. `pipe.fit(X_train, y_train)`을 호출하면 각 단계가 순서대로 train에만 fit되고, `pipe.predict(X_test)`는 그 학습된 파라미터로 transform만 적용한다. leakage가 구조적으로 불가능해진다.

`ColumnTransformer`는 컬럼 타입별로 서로 다른 전처리를 병렬 적용하고 결과를 다시 합친다.

![ColumnTransformer 분기 흐름 — 원본 DataFrame이 ColumnTransformer 안에서 수치형(SimpleImputer median → StandardScaler)·범주형(SimpleImputer 상수 → OneHotEncoder)·고카디널리티(TargetEncoder, fold 안에서만 fit) 세 갈래로 갈라져 전처리된 뒤 hstack으로 피처가 결합되고 최종 Estimator의 fit/predict로 이어진다](/images/study-supervised-learning/16-column-transformer-light.png)
![ColumnTransformer 분기 흐름 — 원본 DataFrame이 ColumnTransformer 안에서 수치형(SimpleImputer median → StandardScaler)·범주형(SimpleImputer 상수 → OneHotEncoder)·고카디널리티(TargetEncoder, fold 안에서만 fit) 세 갈래로 갈라져 전처리된 뒤 hstack으로 피처가 결합되고 최종 Estimator의 fit/predict로 이어진다](/images/study-supervised-learning/16-column-transformer-dark.png)

두 도구를 결합하면 전처리 전체가 하나의 추정기처럼 동작한다.

```python
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression

numeric = ["age", "income", "n_purchases"]
categorical = ["city", "device"]

numeric_pipe = Pipeline([
    ("impute", SimpleImputer(strategy="median", add_indicator=True)),
    ("scale", StandardScaler()),
])

categorical_pipe = Pipeline([
    ("impute", SimpleImputer(strategy="constant", fill_value="MISSING")),
    ("onehot", OneHotEncoder(handle_unknown="ignore")),
])

preprocess = ColumnTransformer([
    ("num", numeric_pipe, numeric),
    ("cat", categorical_pipe, categorical),
])

model = Pipeline([
    ("prep", preprocess),
    ("clf", LogisticRegression(max_iter=1000)),
])

model.fit(X_train, y_train)      # 전처리·모델 모두 train에만 fit
preds = model.predict(X_test)    # test는 transform만
```

`handle_unknown="ignore"`는 train에 없던 범주가 test에 등장해도 에러 대신 0 벡터로 처리하게 해준다. 트리 모델을 쓸 때는 스케일러를 빼고 인코더만 두거나, HistGradientBoosting처럼 결측을 네이티브로 다루는 추정기로 교체하면 된다.

## 7. 교차 검증 안에 파이프라인 통째로 넣기

파이프라인의 진짜 가치는 [4장](/study/supervised-learning/04-cross-validation-tuning)의 교차 검증·튜닝과 결합할 때 드러난다. 파이프라인을 하나의 추정기로 넘기면, CV가 매 fold마다 train 부분으로만 전처리를 fit하고 validation 부분은 transform만 하게 된다. 전처리 통계가 fold 경계를 넘지 않으므로 target encoding·스케일링·대치까지 전부 leakage 없이 평가된다.

```python
from sklearn.model_selection import GridSearchCV

param_grid = {
    "prep__num__impute__strategy": ["median", "mean"],
    "clf__C": [0.1, 1.0, 10.0],
}

search = GridSearchCV(model, param_grid, cv=5, scoring="roc_auc")
search.fit(X_train, y_train)     # fold마다 전처리 재적합 → leakage 차단
print(search.best_params_)
```

`prep__num__impute__strategy`처럼 `단계명__하위단계명__파라미터`로 파이프라인 깊숙한 곳의 하이퍼파라미터까지 한 번에 탐색할 수 있다. 여기서 대치 전략이나 인코더 종류까지 튜닝 대상에 올릴 수 있다는 점이 중요하다 — 전처리 선택도 결국 성능에 영향을 주는 하이퍼파라미터이기 때문이다. 반대로, 파이프라인 밖에서 전처리를 미리 해두고 그 결과를 CV에 넣으면 모든 fold가 전체 train 통계를 공유하게 되어 검증 점수가 낙관적으로 오염된다.

::: tip 핵심 정리
- 전처리(스케일러·인코더·대치기)는 데이터로부터 파라미터를 학습하므로, 반드시 train에서만 fit해야 한다.
- 스케일링은 kNN·선형·SVM·정규화 모델엔 필수, 트리 계열엔 무의미하다.
- 범주형은 명목형이면 원핫, 순서형이면 ordinal, 고카디널리티면 target encoding을 쓰되 target encoding은 leakage에 가장 취약하다.
- 결측은 단순 대치·결측 지시자·트리 네이티브 처리 중 상황에 맞게 고르고, 대치 통계도 train에서만 계산한다.
- `Pipeline`+`ColumnTransformer`로 전처리를 캡슐화하면 fit이 train에만 적용되어 leakage가 구조적으로 불가능해진다.
- 파이프라인을 통째로 교차 검증·`GridSearchCV`에 넣으면 fold마다 전처리가 재적합되어, 전처리 하이퍼파라미터까지 leakage 없이 튜닝된다.
:::

## 다음 챕터

파이프라인으로 전처리를 정돈했더라도, 타깃 분포가 한쪽으로 크게 치우쳐 있으면 정확도 지표부터 무너진다. [불균형 데이터와 캘리브레이션](/study/supervised-learning/17-imbalanced-calibration)에서는 불균형에서 지표를 어떻게 다시 봐야 하는지, class_weight·리샘플링·threshold 조정의 우선순위, 그리고 모델이 내놓는 확률을 신뢰할 수 있게 만드는 probability calibration을 다룬다.
