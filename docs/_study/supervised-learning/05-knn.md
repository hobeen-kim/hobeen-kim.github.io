---
title: "kNN"
description: "학습 단계가 없는 게으른 학습 kNN을 다룬다. 유클리드·맨해튼·코사인 거리, 피처 단위가 다르면 거리가 왜곡되므로 스케일링이 왜 필수인지, k 선택과 편향-분산, 차원의 저주, brute/kd-tree/ball-tree 탐색과 대규모에서의 ANN(HNSW)·벡터 검색 연결, 회귀 kNN, 그리고 kNN을 언제 쓰는가까지 정리한다."
date: 2026-07-03
tags: [Machine Learning, Supervised Learning, kNN, Distance Metric, Curse of Dimensionality, ANN]
prev: /study/supervised-learning/04-cross-validation-tuning
next: /study/supervised-learning/06-linear-regression
---

# kNN

::: info 학습 목표
- kNN이 왜 "게으른 학습"이며 학습 단계에서 무엇을 하는지(사실상 저장만) 이해한다.
- 유클리드·맨해튼·코사인 거리의 차이와 쓰임새를 안다.
- 피처 단위가 다르면 거리가 왜곡되는 이유를 이해하고 스케일링이 필수임을 안다.
- k 선택이 편향-분산과 어떻게 얽히는지, 차원의 저주가 왜 kNN을 무너뜨리는지 파악한다.
- brute/kd-tree/ball-tree 탐색과 대규모에서의 ANN(HNSW)·벡터 검색 연결을 안다.
:::

## 1. 게으른 학습 — 학습이 없다

<strong>kNN(k-Nearest Neighbors)</strong>은 새 입력이 들어오면 <strong>가장 가까운 k개의 학습 데이터를 찾아 다수결(분류)하거나 평균(회귀)</strong>내어 예측한다. 특이한 점은 <strong>학습 단계가 사실상 없다</strong>는 것이다. `fit`은 데이터를 그냥 저장할 뿐이고, 모든 계산은 예측 시점에 미룬다. 그래서 <strong>게으른 학습(lazy learning)</strong> 혹은 인스턴스 기반 학습이라 부른다. 선형 회귀처럼 데이터를 요약한 파라미터를 학습하는 <strong>eager learning</strong>과 대비된다.

![2차원 특징 공간에서 kNN의 다수결 예측 — 두 클래스(A·B)의 점들이 흩어져 있고 질의점(별)을 중심으로 가장 가까운 5개 이웃을 점선 원으로 감싼 뒤, 원 안 이웃 중 클래스 A가 4개 B가 1개이므로 다수결로 A를 예측하는 과정](/images/study-supervised-learning/05-knn-decision-light.png)
![2차원 특징 공간에서 kNN의 다수결 예측 — 두 클래스(A·B)의 점들이 흩어져 있고 질의점(별)을 중심으로 가장 가까운 5개 이웃을 점선 원으로 감싼 뒤, 원 안 이웃 중 클래스 A가 4개 B가 1개이므로 다수결로 A를 예측하는 과정](/images/study-supervised-learning/05-knn-decision-dark.png)

학습은 O(1)로 즉시 끝나지만, 예측 때마다 모든 학습 데이터와의 거리를 계산해야 하므로 <strong>예측이 느리고 메모리를 많이 쓴다</strong>. "학습이 없다"는 장점이 곧 "예측이 비싸다"는 단점으로 이어지는 구조다.

```python
from sklearn.neighbors import KNeighborsClassifier

knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(X_train, y_train)   # 사실상 데이터 저장만 한다
pred = knn.predict(X_test)  # 여기서 비로소 거리를 계산한다
```

## 2. 거리 척도 — 무엇을 "가깝다"고 볼 것인가

kNN의 핵심은 거리 정의다. 어떤 거리를 쓰느냐에 따라 이웃이 달라진다.

- <strong>유클리드 거리(Euclidean, L2)</strong> — 두 점을 잇는 직선 거리. 가장 흔한 기본값이며 연속형 피처에 자연스럽다.
- <strong>맨해튼 거리(Manhattan, L1)</strong> — 축을 따라 이동한 거리의 합. 고차원이나 이상치가 있을 때 L2보다 덜 민감하게 반응한다.
- <strong>코사인 거리(Cosine)</strong> — 크기를 무시하고 <strong>방향(각도)</strong>만 본다. 텍스트 임베딩·문서 벡터처럼 크기보다 성분 비율이 중요할 때 쓴다.

```python
knn = KNeighborsClassifier(n_neighbors=5, metric="manhattan")  # p=1
# 유클리드는 metric="minkowski", p=2 (기본값)
```

거리 선택은 데이터의 성질에 달렸다. 표 형태 수치 데이터면 대개 유클리드로 시작하고, 임베딩 벡터를 다룬다면 코사인이 자연스럽다.

## 3. 왜 스케일링이 필요한가

kNN에서 <strong>스케일링은 선택이 아니라 필수</strong>다. 거리는 모든 피처를 함께 더해 계산하는데, 피처마다 단위와 범위가 다르면 <strong>범위가 큰 피처가 거리를 독점</strong>한다.

예를 들어 나이(20~60)와 연봉(3000~9000만원)으로 사람 사이 거리를 재면, 유클리드 거리의 제곱합에서 연봉 항이 나이 항보다 수백만 배 크다. 결국 "나이 차이"는 거의 무시되고 <strong>사실상 연봉 한 축만으로 이웃이 정해진다</strong>. 나이가 중요한 피처였어도 모델은 그걸 볼 기회조차 없다.

![스케일링 전후로 최근접 이웃이 바뀌는 예시 — 왼쪽은 나이(20~60)와 연봉(3000~9000만원)을 원래 단위로 두어 거리가 사실상 연봉 축에 지배당해 엉뚱한 점이 최근접 이웃으로 잡히고, 오른쪽은 두 피처를 표준화(z-score)해 두 축이 동등해지자 질의점의 최근접 이웃이 바뀌는 모습](/images/study-supervised-learning/05-scaling-light.png)
![스케일링 전후로 최근접 이웃이 바뀌는 예시 — 왼쪽은 나이(20~60)와 연봉(3000~9000만원)을 원래 단위로 두어 거리가 사실상 연봉 축에 지배당해 엉뚱한 점이 최근접 이웃으로 잡히고, 오른쪽은 두 피처를 표준화(z-score)해 두 축이 동등해지자 질의점의 최근접 이웃이 바뀌는 모습](/images/study-supervised-learning/05-scaling-dark.png)

해법은 모든 피처를 비슷한 범위로 맞추는 것이다. `StandardScaler`(평균 0, 분산 1)나 `MinMaxScaler`(0~1)를 쓴다. 이때 [04장](/study/supervised-learning/04-cross-validation-tuning)에서 강조한 대로 스케일러는 <strong>train에만 fit</strong>해야 leakage가 없다. sklearn `Pipeline`으로 묶으면 이 규칙이 자동으로 지켜진다([16장](/study/supervised-learning/16-feature-engineering-pipeline)에서 심화).

```python
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

# 스케일러가 train에만 fit → 거리 왜곡·leakage 동시 방지
pipe = make_pipeline(StandardScaler(), KNeighborsClassifier(n_neighbors=5))
pipe.fit(X_train, y_train)
```

## 4. k 선택과 편향-분산

k는 대표적인 하이퍼파라미터다. 값에 따라 [02장](/study/supervised-learning/02-generalization-overfitting)의 편향-분산 트레이드오프가 그대로 드러난다.

- <strong>k가 작으면(k=1)</strong> 바로 옆 한두 점에만 의존해 결정 경계가 들쭉날쭉해진다. 노이즈까지 외우는 <strong>고분산·과적합</strong> 상태다.
- <strong>k가 크면</strong> 넓은 이웃을 평균해 경계가 매끈해지지만, 지역적 패턴을 뭉개는 <strong>고편향·과평활</strong>로 간다. 극단적으로 k가 전체 데이터 수면 항상 다수 클래스만 예측한다.

![k 값에 따른 kNN 결정 경계 변화 — 같은 두 클래스 데이터에 대해 왼쪽 k=1은 개별 점을 따라 결정 경계가 들쭉날쭉하게 꺾여 노이즈까지 반영하는 고분산·과적합, 오른쪽 k=25는 넓은 이웃을 평균해 경계가 하나의 매끄러운 곡선으로 단순해지는 고편향·과평활](/images/study-supervised-learning/05-k-bias-variance-light.png)
![k 값에 따른 kNN 결정 경계 변화 — 같은 두 클래스 데이터에 대해 왼쪽 k=1은 개별 점을 따라 결정 경계가 들쭉날쭉하게 꺾여 노이즈까지 반영하는 고분산·과적합, 오른쪽 k=25는 넓은 이웃을 평균해 경계가 하나의 매끄러운 곡선으로 단순해지는 고편향·과평활](/images/study-supervised-learning/05-k-bias-variance-dark.png)

적절한 k는 교차 검증으로 고른다. 분류에서 투표 동점을 피하려고 이진 분류면 홀수 k를 쓰는 관습이 있다. 거리가 가까운 이웃에 더 큰 표를 주는 `weights="distance"`도 자주 도움이 된다.

```python
from sklearn.model_selection import GridSearchCV

grid = GridSearchCV(pipe, {"kneighborsclassifier__n_neighbors": range(1, 31, 2)},
                    cv=5, scoring="f1")
grid.fit(X_train, y_train)
print(grid.best_params_)
```

## 5. 차원의 저주

kNN은 <strong>고차원에서 급격히 무너진다</strong>. 차원이 늘수록 데이터는 공간에 희박하게 흩어지고, 임의의 두 점 사이 거리가 서로 비슷해진다. <strong>"가장 가까운 점"과 "가장 먼 점"의 거리 차이가 사라지면</strong> 이웃이라는 개념 자체가 무의미해진다.

직관적으로, 100차원 공간에서 각 축의 10% 이내에 있는 이웃을 찾으려면 전체의 0.1의 100제곱만큼만 남아 사실상 아무도 없다. 그래서 피처가 수십~수백 개로 많으면 kNN은 거리 기반 판단력을 잃는다. 대응책은 정말 중요한 피처만 남기는 피처 선택, 혹은 PCA 같은 차원 축소다.

## 6. 이웃 탐색 자료구조와 대규모 ANN

kNN은 예측마다 이웃을 찾아야 하므로, "어떻게 빨리 찾느냐"가 실전 성능을 좌우한다.

- <strong>brute-force</strong> — 모든 점과의 거리를 다 계산한다. 정확하지만 데이터 수 n에 비례해 느리다. 고차원에서는 오히려 이게 가장 안전하다.
- <strong>kd-tree</strong> — 축을 번갈아 자르며 공간을 분할해 탐색을 가지친다. 저차원(대략 20차원 이하)에서 빠르지만 차원이 높아지면 이점이 사라진다.
- <strong>ball-tree</strong> — 초구(hypersphere)로 공간을 나눠 kd-tree보다 중고차원에서 낫다.

sklearn은 `algorithm="auto"`로 데이터에 맞는 방식을 고른다.

```python
knn = KNeighborsClassifier(n_neighbors=5, algorithm="kd_tree")  # auto가 기본
```

<strong>대규모에서는 근사 최근접 이웃(ANN, Approximate Nearest Neighbor).</strong> 데이터가 수백만~수십억 벡터면 정확한 최근접을 포기하고 <strong>거의 가까운</strong> 이웃을 훨씬 빠르게 찾는다. 대표적으로 그래프 기반 <strong>HNSW</strong>(Hierarchical Navigable Small World)가 있고, 이는 오늘날 <strong>벡터 검색·벡터 DB</strong>의 핵심 엔진이다. 임베딩으로 문서·이미지를 벡터화한 뒤 HNSW로 유사 항목을 검색하는 구조는, 결국 kNN의 "가까운 이웃 찾기"를 초대규모로 확장한 것이다. FAISS·hnswlib·pgvector 같은 도구가 이를 구현한다.

## 7. 회귀 kNN

kNN은 회귀에도 그대로 쓴다. 다수결 대신 <strong>k개 이웃의 타깃 값을 평균</strong>(또는 거리 가중 평균)한다. 국소적으로 부드러운 함수를 근사할 때 쓸 만하지만, 학습 데이터 범위 밖을 외삽하지 못하고 이웃 값의 평균만 내므로 경계에서 계단처럼 튀는 한계가 있다.

```python
from sklearn.neighbors import KNeighborsRegressor

reg = KNeighborsRegressor(n_neighbors=5, weights="distance")
reg.fit(X_train, y_train)
```

## 8. 장단점과 언제 쓰는가

<strong>장점.</strong> 개념이 단순하고 구현이 쉽다. 학습이 없어 데이터 추가가 즉각적이고, 결정 경계에 대한 가정이 없어 복잡한 비선형 경계도 데이터만 충분하면 잡는다.

<strong>단점.</strong> 예측이 느리고 메모리를 많이 쓴다. 스케일링에 민감하고, 차원의 저주에 취약하며, 관련 없는 피처가 섞이면 거리가 오염된다.

<strong>언제 쓰는가.</strong> 저차원·중소규모 데이터에서 빠르게 세우는 <strong>베이스라인</strong>으로 좋다. 실무 표 데이터의 본선 모델로는 이후 배울 GBDT 계열에 대개 밀리지만, "거리로 유사도를 판단한다"는 kNN의 사고방식은 추천 시스템과 벡터 검색으로 곧장 이어지므로 반드시 몸에 익혀 둘 가치가 있다.

::: tip 핵심 정리
- kNN은 학습이 사실상 없는 게으른 학습으로, 예측 시점에 가장 가까운 k개를 찾아 다수결·평균한다 — 학습은 빠르지만 예측이 비싸다.
- 유클리드는 기본, 맨해튼은 고차원·이상치에 강하고, 코사인은 방향이 중요한 임베딩에 쓴다.
- 피처 단위가 다르면 큰 범위 피처가 거리를 독점하므로 스케일링은 필수이며, Pipeline으로 train에만 fit한다.
- k가 작으면 과적합(고분산), 크면 과평활(고편향) — 교차 검증으로 고른다.
- 차원의 저주로 고차원에서 거리가 무의미해지므로 피처를 줄이거나 차원 축소가 필요하다.
- 탐색은 kd-tree/ball-tree로 가속하고, 초대규모에서는 HNSW 같은 ANN이 벡터 검색의 엔진으로 이어진다.
:::

## 다음 챕터

kNN은 데이터를 요약하지 않고 통째로 들고 다니는 모델이었다. 반대로 [선형 회귀와 정규화](/study/supervised-learning/06-linear-regression)는 데이터를 소수의 가중치로 압축해 학습하는 eager learning의 출발점이다. 거리 대신 가중합으로 예측하는 선형 모델의 세계로 넘어간다.
