---
title: "지도 학습 (Supervised Learning)"
description: "kNN부터 GBDT까지 클래식 머신러닝 지도 학습 완전 정복. 일반화·평가 지표·교차 검증의 기초 위에 거리 기반·선형 모델을 쌓고, 결정 트리에서 랜덤 포레스트·그래디언트 부스팅(XGBoost·LightGBM·CatBoost)까지 앙상블을 심화한 뒤, 피처 엔지니어링·불균형 처리·SHAP 해석·모델 선택의 실전 감각으로 마무리한다."
date: 2026-07-03
tags: [Machine Learning, Supervised Learning, kNN, GBDT, XGBoost, LightGBM, scikit-learn]
---

# 지도 학습 (Supervised Learning)

<strong>지도 학습(supervised learning)</strong>은 입력과 정답 쌍으로 이루어진 데이터에서 입력→출력의 규칙을 학습해, 본 적 없는 입력의 출력을 예측하는 머신러닝 패러다임이다. 표 형태(tabular) 데이터가 지배하는 실무 예측 문제에서는 여전히 딥러닝이 아니라 <strong>클래식 지도 학습 — 특히 GBDT(Gradient Boosted Decision Trees)</strong>가 기본 무기다. 이 스터디는 kNN처럼 직관적인 모델에서 시작해 선형 모델·SVM·나이브 베이즈를 거쳐, 결정 트리 → 배깅/부스팅 → 랜덤 포레스트 → 그래디언트 부스팅 → XGBoost·LightGBM·CatBoost로 이어지는 앙상블의 계보를 원리부터 실전 튜닝까지 파고든다.

각 장은 [scikit-learn](https://scikit-learn.org/stable/), [XGBoost](https://xgboost.readthedocs.io/), [LightGBM](https://lightgbm.readthedocs.io/), [CatBoost](https://catboost.ai/docs/) 공식 문서와 원 논문을 기준으로 개념을 설명하고, Python 코드로 확인한다. 대상은 ML 비전공 실무 개발자이며, 수식 나열보다 "왜 그런가 · 트레이드오프 · 실무 함정 · 실전 코드"에 무게를 둔다.

이 스터디에서 배우는 것:

- **기초** — 지도 학습 문제의 형식화, 일반화와 과적합, 편향-분산 트레이드오프, 평가 지표 선택, 교차 검증과 leakage 없는 튜닝
- **거리·선형 모델** — kNN의 거리 계산과 차원의 저주, 선형/로지스틱 회귀와 정규화, SVM·나이브 베이즈의 개요와 쓰임새
- **트리와 앙상블** — 결정 트리의 분할 원리, 배깅 vs 부스팅, 랜덤 포레스트, 그래디언트 부스팅의 잔차 학습, XGBoost·LightGBM·CatBoost 비교, GBDT 튜닝 체크리스트
- **실전** — 피처 엔지니어링과 sklearn Pipeline, 불균형 데이터·캘리브레이션, SHAP 기반 모델 해석, 상황별 모델 선택 가이드

## 학습 로드맵

![학습 로드맵 — 기초(01~04)에서 거리·선형 모델(05~09), 트리와 앙상블(10~15)을 거쳐 실전(16~19)으로 이어지는 4단계 체인](/images/study-supervised-learning/readme-roadmap-light.png)
![학습 로드맵 — 기초(01~04)에서 거리·선형 모델(05~09), 트리와 앙상블(10~15)을 거쳐 실전(16~19)으로 이어지는 4단계 체인](/images/study-supervised-learning/readme-roadmap-dark.png)

## 전체 목차

### 기초 (01~04)

| 챕터 | 제목 | 한줄 설명 |
|------|------|-----------|
| 01 | [지도 학습이란](/study/supervised-learning/01-what-is-supervised-learning) | 회귀/분류 문제의 형식화, 지도·비지도·강화 학습 비교 |
| 02 | [일반화와 과적합](/study/supervised-learning/02-generalization-overfitting) | train/valid/test 분할, 편향-분산 트레이드오프 |
| 03 | [모델 평가 지표](/study/supervised-learning/03-evaluation-metrics) | 회귀·분류 지표, ROC/PR 곡선, 지표 선택 기준 |
| 04 | [교차 검증과 하이퍼파라미터 튜닝](/study/supervised-learning/04-cross-validation-tuning) | k-fold, 그룹/시계열 분할, grid/random/bayesian search, leakage |

### 거리·선형 모델 (05~09)

| 챕터 | 제목 | 한줄 설명 |
|------|------|-----------|
| 05 | [kNN](/study/supervised-learning/05-knn) | 거리 척도, k 선택, 차원의 저주, kd-tree/ANN |
| 06 | [선형 회귀와 정규화](/study/supervised-learning/06-linear-regression) | OLS, 경사하강법, 릿지/라쏘/엘라스틱넷 |
| 07 | [로지스틱 회귀](/study/supervised-learning/07-logistic-regression) | 시그모이드/소프트맥스, 크로스엔트로피, 다중 클래스 전략 |
| 08 | [SVM](/study/supervised-learning/08-svm) | 마진 최대화, soft margin, 커널 트릭 개요 |
| 09 | [나이브 베이즈](/study/supervised-learning/09-naive-bayes) | 베이즈 정리, 조건부 독립 가정, 텍스트 분류 |

### 트리와 앙상블 (10~15)

| 챕터 | 제목 | 한줄 설명 |
|------|------|-----------|
| 10 | [결정 트리](/study/supervised-learning/10-decision-tree) | 불순도 기반 분할, 회귀 트리, 가지치기 |
| 11 | [앙상블 기초](/study/supervised-learning/11-ensemble-basics) | 배깅 vs 부스팅 vs 스태킹, 편향-분산 관점 |
| 12 | [랜덤 포레스트](/study/supervised-learning/12-random-forest) | 부트스트랩, 피처 무작위성, OOB, feature importance |
| 13 | [그래디언트 부스팅 원리](/study/supervised-learning/13-gradient-boosting) | 잔차 학습, 함수 공간 경사하강, 학습률 |
| 14 | [XGBoost·LightGBM·CatBoost](/study/supervised-learning/14-xgboost-lightgbm-catboost) | 2차 근사, 히스토그램 분할, GOSS/EFB, ordered boosting |
| 15 | [GBDT 실전 튜닝](/study/supervised-learning/15-gbdt-tuning) | 하이퍼파라미터 상호작용, early stopping, 과적합 제어 |

### 실전 (16~19)

| 챕터 | 제목 | 한줄 설명 |
|------|------|-----------|
| 16 | [피처 엔지니어링과 파이프라인](/study/supervised-learning/16-feature-engineering-pipeline) | 스케일링, 인코딩, 결측치, Pipeline으로 leakage 방지 |
| 17 | [불균형 데이터와 캘리브레이션](/study/supervised-learning/17-imbalanced-calibration) | class weight, 리샘플링, threshold, probability calibration |
| 18 | [모델 해석](/study/supervised-learning/18-model-interpretation) | importance의 함정, permutation, SHAP, PDP |
| 19 | [모델 선택 실전 가이드](/study/supervised-learning/19-model-selection-guide) | 상황별 모델 선택, tabular에서 GBDT가 강한 이유 |

### 부록

| | 제목 | 설명 |
|--|------|------|
| | [용어집](/study/supervised-learning/appendix-glossary) | 지도 학습 핵심 용어 정리 |
| | [scikit-learn 치트시트](/study/supervised-learning/appendix-cheatsheet) | 자주 쓰는 API·패턴 모음 |
| | [참고 자료](/study/supervised-learning/appendix-references) | 공식 문서·원 논문·심화 학습 링크 |

## 대상

ML을 전공하지 않은 실무 개발자를 대상으로 한다. 수학은 필요한 최소한(미분·확률 기초)만 쓰고, 개념 나열보다 "왜 그런가 · 트레이드오프 · 실무 함정 · 실전 코드"에 집중한다. 예측 문제를 받아든 백엔드 개발자가 kNN 같은 베이스라인부터 GBDT 튜닝·해석까지 스스로 해낼 수 있게 되는 것이 목표다.
