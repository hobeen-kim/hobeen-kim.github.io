---
title: "참고 자료"
description: "지도 학습 학습을 이어갈 공식 문서·원 논문·심화 도서·커뮤니티 자료 모음. scikit-learn User Guide와 XGBoost/LightGBM/CatBoost 공식 docs, XGBoost·LightGBM·CatBoost·Random Forests·Gradient Boosting·SHAP·tabular 딥러닝 비교 원 논문, ESL/ISL·Hands-On ML 심화 도서를 카테고리별로 정리했다."
date: 2026-07-03
tags: [Supervised Learning, References]
prev: /study/supervised-learning/appendix-cheatsheet
next: false
---

# 참고 자료

스터디를 마친 뒤 더 깊이 파고들 수 있는 공식 문서·원 논문·심화 자료를 카테고리별로 모았다. 1차 출처는 언제나 공식 문서와 원 논문이므로 그것부터 둔다.

## scikit-learn 공식 문서

- [scikit-learn User Guide](https://scikit-learn.org/stable/user_guide.html) — 지도 학습 전반을 관통하는 표준 레퍼런스
- [Cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html) — KFold·Stratified·Group·TimeSeries 분할 전략
- [Model Selection (Grid/Randomized Search)](https://scikit-learn.org/stable/modules/grid_search.html) — 하이퍼파라미터 탐색 API
- [Metrics and Scoring](https://scikit-learn.org/stable/modules/model_evaluation.html) — 분류·회귀 지표와 scoring 문자열
- [Pipeline and ColumnTransformer](https://scikit-learn.org/stable/modules/compose.html) — 전처리+모델 조립과 leakage 방지
- [Preprocessing](https://scikit-learn.org/stable/modules/preprocessing.html) — 스케일링·인코딩·결측치 전처리
- [Ensemble methods](https://scikit-learn.org/stable/modules/ensemble.html) — 랜덤 포레스트·그래디언트 부스팅·스태킹
- [Probability Calibration](https://scikit-learn.org/stable/modules/calibration.html) — Platt/isotonic 확률 보정
- [Inspection (Permutation Importance·PDP)](https://scikit-learn.org/stable/modules/inspection.html) — 모델 해석 도구

## 그래디언트 부스팅 라이브러리 문서

- [XGBoost Documentation](https://xgboost.readthedocs.io/) — 파라미터·튜닝·API 전체 문서
- [XGBoost Parameters](https://xgboost.readthedocs.io/en/stable/parameter.html) — 트리·규제·학습 파라미터 레퍼런스
- [LightGBM Documentation](https://lightgbm.readthedocs.io/) — leaf-wise 성장·GOSS·EFB 문서
- [LightGBM Parameters Tuning](https://lightgbm.readthedocs.io/en/latest/Parameters-Tuning.html) — 과적합·정확도·속도 튜닝 가이드
- [CatBoost Documentation](https://catboost.ai/docs/) — ordered boosting·범주형 처리 문서
- [Optuna Documentation](https://optuna.readthedocs.io/) — 베이지안 하이퍼파라미터 최적화 프레임워크
- [imbalanced-learn](https://imbalanced-learn.org/stable/) — SMOTE 등 불균형 데이터 리샘플링 라이브러리
- [SHAP Documentation](https://shap.readthedocs.io/) — Shapley 값 기반 모델 해석 라이브러리

## 원 논문

- [XGBoost: A Scalable Tree Boosting System (Chen & Guestrin, 2016)](https://arxiv.org/abs/1603.02754) — 2차 근사·정규화·희소 인지 분할·시스템 설계
- [LightGBM: A Highly Efficient Gradient Boosting Decision Tree (Ke et al., 2017)](https://papers.nips.cc/paper/2017/hash/6449f44a102fde848669bdd9eb6b76fa-Abstract.html) — GOSS와 EFB로 속도·메모리를 개선한 GBDT
- [CatBoost: unbiased boosting with categorical features (Prokhorenkova et al., 2018)](https://arxiv.org/abs/1706.09516) — ordered boosting과 target encoding의 누수 제거
- [Random Forests (Breiman, 2001)](https://link.springer.com/article/10.1023/A:1010933404324) — 배깅+피처 무작위성으로 분산을 줄인 앙상블의 원전
- [Greedy Function Approximation: A Gradient Boosting Machine (Friedman, 2001)](https://projecteuclid.org/euclid.aos/1013203451) — 함수 공간 경사하강으로서의 그래디언트 부스팅 원전
- [A Unified Approach to Interpreting Model Predictions (SHAP; Lundberg & Lee, 2017)](https://arxiv.org/abs/1705.07874) — SHAP 값으로 예측 기여를 일관되게 분해
- [Why do tree-based models still outperform deep learning on tabular data? (Grinsztajn et al., 2022)](https://arxiv.org/abs/2207.08815) — tabular에서 GBDT가 딥러닝을 앞서는 이유를 실증 분석

## 심화 도서

- [The Elements of Statistical Learning (ESL; Hastie·Tibshirani·Friedman)](https://hastie.su.domains/ElemStatLearn/) — 통계적 학습의 이론적 표준서, 무료 PDF 공개
- [An Introduction to Statistical Learning (ISL; James et al.)](https://www.statlearning.com/) — ESL의 실습 지향 입문판, R/Python 판 모두 무료 공개
- [Hands-On Machine Learning (Géron)](https://www.oreilly.com/library/view/hands-on-machine-learning/9781098125967/) — scikit-learn 실전 중심 베스트셀러
- [Interpretable Machine Learning (Molnar)](https://christophm.github.io/interpretable-ml-book/) — permutation importance·PDP·SHAP 등 해석 기법 무료 온라인 도서
- [Feature Engineering for Machine Learning (O'Reilly)](https://www.oreilly.com/library/view/feature-engineering-for/9781491953235/) — 피처 가공·인코딩 실전서

## 커뮤니티·심화 자료

- [Kaggle](https://www.kaggle.com/) — tabular 대회·노트북·데이터셋으로 GBDT 실전 감각을 기르는 최적 창구
- [Kaggle: Intermediate Machine Learning](https://www.kaggle.com/learn/intermediate-machine-learning) — 파이프라인·XGBoost·leakage 실습 미니 코스
- [scikit-learn: Common pitfalls and recommended practices](https://scikit-learn.org/stable/common_pitfalls.html) — leakage·재현성 등 흔한 함정 정리
- [Laurae++: xgboost / LightGBM parameters](https://sites.google.com/view/lauraepp/parameters) — GBDT 파라미터를 상세히 비교·해설한 커뮤니티 레퍼런스
- [Distill.pub](https://distill.pub/) — 머신러닝 개념을 시각적으로 풀어낸 아티클 모음

이것으로 지도 학습 스터디 전체를 마친다. 일반화·평가·교차 검증의 기초 위에 kNN·선형·SVM·나이브 베이즈를 쌓고, 결정 트리에서 랜덤 포레스트·그래디언트 부스팅·XGBoost·LightGBM·CatBoost로 이어지는 앙상블의 계보를 원리부터 튜닝까지 훑은 뒤, 피처 엔지니어링·불균형·캘리브레이션·SHAP·모델 선택의 실전 감각으로 마무리했다. 본문으로 돌아가려면 [스터디 목차](/study/supervised-learning/)를 참고한다.
