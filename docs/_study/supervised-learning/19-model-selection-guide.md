---
title: "모델 선택 실전 가이드"
description: "문제 특성(데이터 크기·피처 타입·해석 요구·지연 제약)별 모델 선택 기준과 로지스틱→GBDT 베이스라인 전략을 정리하고, tabular에서 여전히 GBDT가 강한 이유와 딥러닝으로 넘어가는 경계를 짚은 뒤, 전체 모델 비교 표와 문제 정의부터 배포 감시까지의 실무 워크플로우로 스터디를 마무리한다."
date: 2026-07-03
tags: [Machine Learning, Supervised Learning, Model Selection, GBDT, Workflow]
prev: /study/supervised-learning/18-model-interpretation
next: /study/supervised-learning/appendix-glossary
---

# 모델 선택 실전 가이드

::: info 학습 목표
- 데이터 크기·피처 타입·해석 요구·지연 제약이라는 축으로 모델 선택을 구조화한다.
- 로지스틱/kNN 베이스라인에서 GBDT로 올려가는 단계적 전략을 세운다.
- tabular 데이터에서 딥러닝이 아니라 GBDT가 여전히 기본인 이유를 근거와 함께 설명한다.
- 딥러닝으로 넘어가야 하는 경계(이미지·텍스트·초대규모·표현 학습)를 구분한다.
- kNN부터 GBDT까지 전체 모델을 전처리 요구·해석성·속도·강점으로 비교한다.
- 문제 정의부터 배포 감시까지의 실무 워크플로우를 하나의 흐름으로 꿴다.
:::

## 1. 선택을 가르는 네 가지 축

"어떤 모델이 제일 좋은가"에는 정답이 없다. 대신 문제의 성격을 네 축으로 읽으면 후보가 좁혀진다.

- <strong>데이터 크기</strong> — 수백~수천 행이면 분산이 큰 복잡한 모델은 과적합한다. 규제 선형 모델이나 얕은 트리가 안전하다. 수만~수백만 행이면 GBDT가 편향·분산을 함께 다루며 빛을 본다.
- <strong>피처 타입</strong> — 수치·범주가 섞이고 스케일이 제각각인 <strong>불균질(heterogeneous)</strong> tabular라면 트리 계열이 강하다. 반대로 픽셀·토큰·파형처럼 균질하고 공간·순서 구조가 있는 데이터는 딥러닝의 영역이다.
- <strong>해석 요구</strong> — 규제·심사처럼 근거 제시가 필수면 선형 모델의 계수나 GBDT + SHAP([18장](/study/supervised-learning/18-model-interpretation))이 필요하다. 블랙박스가 허용되는 내부 랭킹 문제라면 제약이 느슨하다.
- <strong>지연시간 제약</strong> — 실시간 광고 입찰처럼 수 밀리초 안에 응답해야 하면, 추론이 무거운 kNN(질의마다 전체 탐색)이나 거대한 앙상블은 부담이다. 선형 모델이나 트리 수를 제한한 GBDT가 현실적이다.

같은 축을 실제 문제에 대보면 선택이 갈리는 게 보인다. <strong>신용 스코어링</strong>은 규제·심사 때문에 해석이 최우선이라 로지스틱 회귀나 GBDT + SHAP이 자연스럽고, <strong>실시간 추천</strong>은 저지연이 최우선이라 무거운 앙상블 대신 가벼운 선형·경량 GBDT로 기운다. <strong>스팸 필터</strong>는 고차원 희소 텍스트라 나이브 베이즈·선형 SVM이 여전히 강하고, <strong>이탈 예측</strong>은 불균질 tabular에 중간 규모라 GBDT의 전형적 무대다. 하나의 정답이 아니라 축의 조합이 답을 정한다.

## 2. 베이스라인 전략 — 낮은 데서 올린다

처음부터 가장 강한 모델을 튜닝하는 것은 흔한 실수다. 먼저 <strong>싸고 견고한 베이스라인</strong>을 세우고 단계적으로 올린다.

1. <strong>단순 베이스라인</strong> — 분류면 로지스틱 회귀, 회귀면 규제 선형 회귀. 학습이 빠르고, 계수로 해석이 되며, 데이터 파이프라인·평가 지표·분할이 제대로 도는지 검증하는 기준선이 된다. kNN도 거리 감각을 잡는 참고선으로 좋다.
2. <strong>지표를 기록한다</strong> — 이 베이스라인 점수가 이후 모든 개선의 비교 대상이다. 복잡한 모델이 베이스라인을 유의미하게 못 넘으면, 그 복잡도는 값을 못 한다.
3. <strong>GBDT로 올린다</strong> — tabular라면 다음 단계는 거의 항상 GBDT다. 기본 하이퍼파라미터만으로도 선형 베이스라인을 크게 앞서는 경우가 많고, 이후 [15장 튜닝](/study/supervised-learning/15-gbdt-tuning)으로 성능을 끌어올린다.

```python
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from lightgbm import LGBMClassifier

# 1) 베이스라인 — 파이프라인·지표·분할 검증
base = LogisticRegression(max_iter=1000)
print("baseline", cross_val_score(base, X, y, scoring="roc_auc", cv=5).mean())

# 2) GBDT로 올린다 — 기본값만으로 먼저 비교
gbdt = LGBMClassifier(n_estimators=500, learning_rate=0.05)
print("gbdt", cross_val_score(gbdt, X, y, scoring="roc_auc", cv=5).mean())
```

이 "로지스틱 → GBDT" 순서는 위험을 통제하면서 성능을 올리는 안전한 사다리다. 각 단계에서 얻는 것(파이프라인 검증 → 기준 점수 → 성능)이 명확하다. GBDT가 베이스라인을 못 넘으면, 피처나 데이터에 문제가 있다는 신호이지 모델을 더 키울 이유가 아니다.

## 3. tabular에서는 왜 여전히 GBDT인가

이미지·언어를 딥러닝이 평정한 지 오래인데, tabular 예측에서는 GBDT가 기본 무기 자리를 지킨다. 여러 벤치마크 연구(대표적으로 Grinsztajn 등의 2022년 "Why do tree-based models still outperform deep learning on tabular data?")가 같은 결론을 반복한다. 이유는 세 가지다.

- <strong>불균질 피처에 강하다</strong> — tabular는 단위·스케일·분포가 다른 컬럼이 섞여 있다. 트리는 각 피처를 독립적으로 임계값에서 쪼개므로 스케일링이 사실상 불필요하고, 신경망이 어려워하는 "제각각인 피처"를 자연스럽게 다룬다.
- <strong>비평활(non-smooth) 타깃 함수에 강하다</strong> — tabular의 결정 경계는 계단처럼 급격히 꺾이는 경우가 많다. 신경망은 매끄러운 함수에 편향(inductive bias)돼 있어 이런 불규칙한 경계를 학습하기 어렵지만, 트리의 축 정렬 분할은 계단 함수를 그대로 표현한다.
- <strong>표본 효율이 높다</strong> — 딥러닝은 대개 대량의 데이터가 있어야 제 성능을 낸다. tabular 문제는 수천~수십만 행 규모가 흔한데, 이 영역에서 GBDT는 적은 데이터로도 안정적으로 좋은 성능을 내고 튜닝도 덜 예민하다.

여기에 학습·추론이 빠르고, 전처리가 간단하며, SHAP으로 해석까지 잘 되는 실무적 이점이 더해진다. 그래서 "tabular면 일단 GBDT"가 합리적 기본값이다.

물론 tabular 전용 딥러닝 연구(TabNet, FT-Transformer, SAINT 등)도 활발하다. 다만 공정한 벤치마크에서는 이들이 잘 튜닝된 GBDT를 확실히·일관되게 앞서지는 못하며, 대개 더 무거운 학습 비용과 더 예민한 튜닝을 요구한다. 특히 데이터가 초대규모가 아니고 피처가 불균질한 전형적 실무 환경에서는, 딥러닝을 얹는 복잡도가 성능 이득을 정당화하지 못하는 경우가 많다. 그래서 tabular 딥러닝은 "지켜볼 후보"이지 아직 "기본값"은 아니다.

## 4. 언제 딥러닝으로 넘어가는가

그렇다고 GBDT가 만능은 아니다. 다음 신호가 보이면 딥러닝이 정답에 가깝다.

- <strong>비정형 데이터</strong> — 이미지·텍스트·음성·비디오처럼 공간·순서 구조가 핵심인 데이터. CNN·Transformer가 이 구조를 표현하도록 설계됐다.
- <strong>표현 학습이 필요할 때</strong> — 원시 입력에서 유용한 피처를 <strong>스스로 학습</strong>해야 하는 문제(임베딩, 사전학습-미세조정). 수작업 피처 엔지니어링으로는 한계가 뚜렷한 영역이다.
- <strong>초대규모 데이터</strong> — 수천만~수억 샘플에서는 딥러닝의 표현력과 GPU 확장성이 GBDT의 표본 효율 이점을 상쇄한다.
- <strong>멀티모달·전이 학습</strong> — 이미지 + 텍스트를 함께 다루거나, 사전학습된 대형 모델을 재활용해야 하는 문제.

![모델 선택 결정 트리 — '데이터가 어떤 형태?'에서 이미지·텍스트·음성이면 딥러닝(표현 학습)으로, 정형(tabular)이면 우선순위에 따라 빠른 베이스라인(로지스틱·kNN)·최고 예측 성능(GBDT)·강한 해석성(규제 선형·얕은 트리)·고차원 희소 BoW(선형 SVM·나이브 베이즈)로 갈리는 구조](/images/study-supervised-learning/19-model-selection-tree-light.png)
![모델 선택 결정 트리 — '데이터가 어떤 형태?'에서 이미지·텍스트·음성이면 딥러닝(표현 학습)으로, 정형(tabular)이면 우선순위에 따라 빠른 베이스라인(로지스틱·kNN)·최고 예측 성능(GBDT)·강한 해석성(규제 선형·얕은 트리)·고차원 희소 BoW(선형 SVM·나이브 베이즈)로 갈리는 구조](/images/study-supervised-learning/19-model-selection-tree-dark.png)

## 5. 전체 모델 비교 총정리

스터디에서 다룬 모델을 한 표로 모은다. "무엇이 제일 좋은가"가 아니라 "언제 무엇을 꺼내는가"의 지도다.

| 모델 | 전처리 요구 | 해석성 | 속도(학습/추론) | 강점 / 쓰임새 |
|---|---|---|---|---|
| [kNN](/study/supervised-learning/05-knn) | 높음(스케일링 필수) | 중(이웃 제시) | 없음 / 느림 | 직관적 베이스라인, 국소 패턴, 저차원 |
| [선형 회귀](/study/supervised-learning/06-linear-regression) | 높음(스케일·인코딩) | 높음(계수) | 빠름 / 빠름 | 선형 관계, 해석·기준선, 외삽 |
| [로지스틱 회귀](/study/supervised-learning/07-logistic-regression) | 높음 | 높음(계수·오즈비) | 빠름 / 빠름 | 분류 베이스라인, 확률 출력, 규제 대응 |
| [SVM](/study/supervised-learning/08-svm) | 높음(스케일 필수) | 낮음(커널 시) | 느림(대규모) / 중 | 고차원·명확한 마진, 중소규모 |
| [나이브 베이즈](/study/supervised-learning/09-naive-bayes) | 중 | 중 | 매우 빠름 / 빠름 | 텍스트 분류, 고차원 희소, 초경량 |
| [결정 트리](/study/supervised-learning/10-decision-tree) | 낮음 | 높음(규칙 시각화) | 빠름 / 빠름 | 규칙 해석, 앙상블의 기본 블록 |
| [랜덤 포레스트](/study/supervised-learning/12-random-forest) | 낮음 | 중 | 중 / 중 | 안정적 기본값, OOB, 튜닝 부담 적음 |
| [GBDT](/study/supervised-learning/14-xgboost-lightgbm-catboost) | 낮음 | 중(+SHAP) | 중 / 빠름 | tabular 최고 성능, 실무 기본 무기 |

전처리 요구가 "낮음"인 트리 계열과 "높음"인 거리·선형 계열의 대비, 그리고 해석성과 성능의 트레이드오프가 표에서 드러난다. tabular 실무의 기본 축은 <strong>로지스틱(해석·기준) ↔ GBDT(성능)</strong>이고, 나머지는 특정 상황(텍스트·고차원·저지연·강한 선형성)에서 꺼내는 카드다.

마지막 한 수가 더 필요하면, 성격이 다른 모델들의 예측을 [스태킹](/study/supervised-learning/11-ensemble-basics)으로 결합할 수 있다. 다만 대회에서는 흔해도 실무에서는 운영·해석 부담이 커, GBDT 하나를 잘 튜닝하는 편이 비용 대비 효과가 좋은 경우가 대부분이다. 표를 외우기보다, 문제를 만나면 네 축으로 후보를 좁히고 베이스라인부터 사다리를 타는 습관이 남으면 이 스터디의 목표는 이룬 것이다.

## 6. 실무 워크플로우 — 문제 정의에서 배포 감시까지

모델 선택은 더 큰 흐름의 한 단계일 뿐이다. 스터디 전체가 이 파이프라인의 각 마디였다.

![실무 워크플로우 체인 — 문제 정의(지표·제약 확정)→데이터 분할(leakage 차단)→베이스라인(로지스틱→GBDT)→피처 엔지니어링(Pipeline 내부)→튜닝(CV·early stop)→해석(permutation·SHAP)→배포·감시(드리프트 추적)로 이어지고, 튜닝·해석·피처 사이의 반복 루프와 배포·감시에서 관측성 스터디로의 연결을 표시](/images/study-supervised-learning/19-workflow-chain-light.png)
![실무 워크플로우 체인 — 문제 정의(지표·제약 확정)→데이터 분할(leakage 차단)→베이스라인(로지스틱→GBDT)→피처 엔지니어링(Pipeline 내부)→튜닝(CV·early stop)→해석(permutation·SHAP)→배포·감시(드리프트 추적)로 이어지고, 튜닝·해석·피처 사이의 반복 루프와 배포·감시에서 관측성 스터디로의 연결을 표시](/images/study-supervised-learning/19-workflow-chain-dark.png)

- <strong>문제 정의</strong> — 회귀/분류를 정하고, 비즈니스 목표에 맞는 [평가 지표](/study/supervised-learning/03-evaluation-metrics)와 지연·해석 제약을 먼저 못박는다. 지표를 나중에 정하면 튜닝이 엉뚱한 방향으로 간다.
- <strong>데이터 분할</strong> — train/valid/test를 나누고 [leakage](/study/supervised-learning/04-cross-validation-tuning)를 차단한다. 여기서 새면 이후 모든 점수가 거짓말이 된다.
- <strong>베이스라인</strong> — 2절의 로지스틱 → GBDT 사다리를 탄다.
- <strong>피처 엔지니어링</strong> — 스케일링·인코딩·결측 처리를 [Pipeline 내부](/study/supervised-learning/16-feature-engineering-pipeline)에 넣어 분할 경계를 넘지 않게 한다. [불균형·캘리브레이션](/study/supervised-learning/17-imbalanced-calibration)도 이 단계에서 다룬다.
- <strong>튜닝</strong> — 교차 검증과 early stopping으로 과적합을 통제하며 하이퍼파라미터를 조정한다.
- <strong>해석</strong> — permutation importance·SHAP로 모델이 무엇에 의존하는지 확인하고, 누수·편향을 잡는다. 여기서 발견한 문제는 피처·튜닝 단계로 되돌아가는 반복 루프를 만든다.
- <strong>배포·감시</strong> — 배포 후 입력 분포·성능의 드리프트를 지속적으로 추적한다. 모델은 배포 순간 낡기 시작하므로, 운영 관측이 마지막이자 계속되는 단계다 — 이 감시를 어떻게 설계하는지는 [관측성 스터디](/study/observability/)로 이어진다.

이 흐름을 관통하는 원칙 하나가 <strong>재현성</strong>이다. 분할·전처리·튜닝의 모든 무작위성에 시드를 고정하고, 데이터 버전·피처 정의·하이퍼파라미터·평가 점수를 실험마다 기록해 둔다. 그래야 "어제의 좋은 모델"을 내일 다시 만들 수 있고, 배포된 모델이 감시 단계에서 흔들릴 때 어느 마디로 되돌아가야 하는지 추적할 수 있다. 모델 선택은 한 번의 결정이 아니라, 이 워크플로우를 여러 번 도는 과정에서 데이터가 스스로 답을 좁혀 주는 일에 가깝다.

::: tip 핵심 정리
- 모델 선택은 데이터 크기·피처 타입·해석 요구·지연 제약이라는 네 축으로 좁힌다.
- 로지스틱/kNN 베이스라인으로 파이프라인을 검증하고 기준 점수를 잡은 뒤 GBDT로 올린다.
- tabular에서 GBDT가 강한 이유는 불균질 피처·비평활 타깃·높은 표본 효율이며, 벤치마크가 이를 반복 확인한다.
- 이미지·텍스트·초대규모·표현 학습이 필요한 문제에서만 딥러닝으로 넘어간다.
- 전체 모델 비교의 실무 기본 축은 로지스틱(해석)↔GBDT(성능)이고, 나머지는 상황별 카드다.
- 워크플로우는 문제 정의→분할→베이스라인→피처→튜닝→해석→배포 감시로 이어지며, 감시는 관측성으로 연결된다.
:::

## 다음 챕터

본편은 여기서 마무리된다. 이제 필요할 때 꺼내 보는 참고 자료가 남았다. [용어집](/study/supervised-learning/appendix-glossary)에서 지도 학습 핵심 용어를 한자리에 정리하고, [scikit-learn 치트시트](/study/supervised-learning/appendix-cheatsheet)에서 자주 쓰는 API·패턴을 모으며, [참고 자료](/study/supervised-learning/appendix-references)에서 공식 문서·원 논문·심화 학습 링크를 안내한다.
