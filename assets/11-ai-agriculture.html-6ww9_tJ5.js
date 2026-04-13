import{_ as l,c as n,e as a,o as e}from"./app-BTUxan41.js";const r={};function i(s,t){return e(),n("div",null,t[0]||(t[0]=[a(`<div class="hint-container info"><p class="hint-container-title">학습 목표</p><ul><li>규칙 기반 시스템과 AI 기반 시스템의 의사결정 방식 차이를 설명할 수 있다.</li><li>CNN을 활용한 병해충 탐지 파이프라인을 단계별로 설명할 수 있다.</li><li>수확량 예측에 사용되는 입력 데이터와 모델 유형(회귀, LSTM)을 구분할 수 있다.</li><li>처방맵 자동 생성 과정에서 클러스터링과 분류 알고리즘의 역할을 설명할 수 있다.</li></ul></div><h2 id="농업-ai-개요" tabindex="-1"><a class="header-anchor" href="#농업-ai-개요"><span>농업 AI 개요</span></a></h2><p>스마트농업의 이전 단계까지는 데이터를 수집하고 규칙으로 제어하는 시스템이 중심이었다. 예를 들어 &quot;토양 수분이 60% 이하로 내려가면 관개 밸브를 연다&quot;는 if-then 규칙이 자동화의 대부분을 담당했다. 이 방식은 단순하고 설명 가능하지만, 복수의 변수가 복잡하게 얽힌 상황에서는 최적 결정을 내리기 어렵다.</p><p>농업 AI는 이 한계를 넘어선다. 수십 개의 입력 변수를 동시에 고려하고, 변수 간 비선형 상호작용을 학습하여 사람이 규칙으로 표현하기 어려운 패턴을 발견한다.</p><table><thead><tr><th>항목</th><th>규칙 기반 시스템</th><th>AI 기반 시스템</th></tr></thead><tbody><tr><td>의사결정 방식</td><td>전문가가 작성한 if-then 규칙</td><td>데이터에서 학습한 패턴</td></tr><tr><td>변수 처리</td><td>소수의 명시적 변수</td><td>수십~수백 개 변수 동시 처리</td></tr><tr><td>환경 적응</td><td>수동으로 규칙 수정 필요</td><td>새 데이터로 자동 재학습</td></tr><tr><td>설명 가능성</td><td>높음</td><td>낮음(블랙박스 문제)</td></tr><tr><td>예외 상황 대응</td><td>규칙 외 상황에 취약</td><td>유사 패턴으로 일반화</td></tr></tbody></table><p>농업 AI의 데이터 흐름은 다음과 같이 정리할 수 있다.</p><pre class="mermaid">flowchart LR
    subgraph 입력
        S1[IoT 센서&lt;br&gt;토양·기상·수분]
        S2[위성·드론 이미지&lt;br&gt;NDVI·멀티스펙트럼]
        S3[기상청 예보&lt;br&gt;강수·기온·일사량]
        S4[농가 이력&lt;br&gt;작업 기록·수확 데이터]
    end
    subgraph AI모델
        M1[CNN&lt;br&gt;이미지 분류·탐지]
        M2[LSTM / 시계열 모델&lt;br&gt;수확량 예측]
        M3[클러스터링&lt;br&gt;처방맵 생성]
    end
    subgraph 출력
        O1[병해충 경보&lt;br&gt;종류·위치·심각도]
        O2[수확량 예측&lt;br&gt;구역별 예상 수확량]
        O3[처방맵&lt;br&gt;구역별 최적 투입량]
    end
    S1 --&gt; M2
    S2 --&gt; M1
    S2 --&gt; M3
    S3 --&gt; M2
    S4 --&gt; M3
    M1 --&gt; O1
    M2 --&gt; O2
    M3 --&gt; O3
</pre><h2 id="병해충-탐지" tabindex="-1"><a class="header-anchor" href="#병해충-탐지"><span>병해충 탐지</span></a></h2><h3 id="문제의-중요성" tabindex="-1"><a class="header-anchor" href="#문제의-중요성"><span>문제의 중요성</span></a></h3><p>병해충은 전 세계 농작물의 20~40%를 손실시키는 주요 원인이다. 조기에 발견할수록 방제 비용이 낮고 피해가 적다. 그러나 전통적으로는 육안 관찰에 의존했기 때문에 광범위한 필지에서 초기 병징을 놓치는 경우가 많았다.</p><p>스마트폰 카메라나 드론 이미지에 AI를 결합하면 대면적을 신속하게 스캔하여 초기 병징을 포착할 수 있다.</p><h3 id="cnn-기반-탐지-파이프라인" tabindex="-1"><a class="header-anchor" href="#cnn-기반-탐지-파이프라인"><span>CNN 기반 탐지 파이프라인</span></a></h3><p>CNN(Convolutional Neural Network)은 이미지에서 국소 패턴(잎 반점, 변색, 형태 이상)을 계층적으로 추출하여 병해충 종류를 분류한다.</p><pre class="mermaid">flowchart TD
    IMG[드론·스마트폰 이미지 수집] --&gt; PRE[전처리&lt;br&gt;리사이즈·정규화·증강]
    PRE --&gt; CNN[CNN 모델&lt;br&gt;특징 추출 → 분류]
    CNN --&gt; CLS{분류 결과}
    CLS --&gt;|건강| OK[정상 판정]
    CLS --&gt;|병해 탐지| ALERT[경보 발령&lt;br&gt;병해 종류·위치·심각도]
    ALERT --&gt; ACTION[방제 처방&lt;br&gt;농약 종류·살포 구역]
</pre><h3 id="plantvillage-데이터셋" tabindex="-1"><a class="header-anchor" href="#plantvillage-데이터셋"><span>PlantVillage 데이터셋</span></a></h3><p>PlantVillage는 Penn State University가 공개한 54,000장 이상의 작물 잎 이미지 데이터셋이다. 14개 작물, 26개 병해, 건강 상태를 포함한다. 이 데이터셋을 전이 학습(Transfer Learning)의 기반으로 활용하면 소규모 농가 데이터만으로도 높은 정확도의 모델을 만들 수 있다.</p><p>PlantVillage 기반 모델은 실험실 조건에서 99%에 가까운 정확도를 달성했다. 그러나 실제 필지 조건(다양한 조명, 배경 복잡도, 증상 초기 단계)에서는 80~90%대로 낮아진다. 이 간극을 줄이는 것이 현재 연구의 주요 과제다.</p><h3 id="조기-발견의-경제적-효과" tabindex="-1"><a class="header-anchor" href="#조기-발견의-경제적-효과"><span>조기 발견의 경제적 효과</span></a></h3><p>병해충을 1주 일찍 발견하면 방제 비용을 30~50% 절감할 수 있다는 연구 결과가 있다. 특히 포도 노균병, 토마토 역병처럼 확산 속도가 빠른 병해는 조기 탐지가 수확량 보존에 결정적이다.</p><h2 id="수확량-예측" tabindex="-1"><a class="header-anchor" href="#수확량-예측"><span>수확량 예측</span></a></h2><h3 id="왜-예측이-중요한가" tabindex="-1"><a class="header-anchor" href="#왜-예측이-중요한가"><span>왜 예측이 중요한가</span></a></h3><p>시즌 초기에 수확량을 예측할 수 있으면 여러 이점이 생긴다. 농가 차원에서는 수확 인력·장비 사전 수배, 저장 공간 확보, 선도 계약 판매가 가능해진다. 국가 차원에서는 식량 수급 계획 수립, 수출입 물량 조절, 식량 안보 리스크 관리에 활용된다.</p><h3 id="입력-데이터" tabindex="-1"><a class="header-anchor" href="#입력-데이터"><span>입력 데이터</span></a></h3><p>수확량 예측 모델에 투입되는 주요 데이터는 다음과 같다.</p><ul><li><strong>기상 데이터</strong>: 기온, 강수량, 일사량, 습도의 일별·주별 시계열. 꽃피는 시기의 기온이 결실에 특히 중요하다.</li><li><strong>토양 데이터</strong>: 토양 수분, 질소·인·칼리 농도, pH. 생육 기간 내 변화를 추적한다.</li><li><strong>위성 NDVI</strong>: 정규화 식생지수(NDVI)는 작물의 엽록소 밀도와 생육 활력을 반영한다. 파종 후 주기적으로 측정하면 작물 생육 궤적을 수치화할 수 있다.</li><li><strong>이전 수확 이력</strong>: 같은 필지에서 수년간 축적된 수확 데이터는 토양 특성과 미기후가 반영된 필지 고유의 기준선을 제공한다.</li></ul><h3 id="모델-유형" tabindex="-1"><a class="header-anchor" href="#모델-유형"><span>모델 유형</span></a></h3><p><strong>회귀 모델</strong>: 입력 변수와 수확량 사이의 관계를 학습한다. Random Forest, XGBoost 같은 앙상블 모델이 농업 분야에서 널리 쓰인다. 입력 변수의 중요도를 해석할 수 있어 농업인에게 설명하기 용이하다.</p><p><strong>LSTM (Long Short-Term Memory)</strong>: 기상과 식생지수 같은 시계열 데이터의 시간적 패턴을 학습하는 순환 신경망이다. 과거 N주의 NDVI 변화 추세가 최종 수확량에 미치는 영향을 모델링하는 데 적합하다. 회귀 모델보다 데이터량이 많이 필요하지만 시계열 패턴 포착 능력이 뛰어나다.</p><pre class="mermaid">flowchart LR
    subgraph 입력데이터
        D1[기상 시계열&lt;br&gt;기온·강수·일사량]
        D2[토양 측정값&lt;br&gt;수분·질소·pH]
        D3[위성 NDVI&lt;br&gt;주별 식생 지수]
        D4[이전 수확 이력&lt;br&gt;필지별 기준선]
    end
    subgraph 모델선택
        M1[회귀 모델&lt;br&gt;XGBoost / Random Forest&lt;br&gt;변수 중요도 해석 가능]
        M2[LSTM&lt;br&gt;시계열 패턴 학습&lt;br&gt;높은 데이터 요구]
    end
    D1 --&gt; M2
    D2 --&gt; M1
    D3 --&gt; M1
    D3 --&gt; M2
    D4 --&gt; M1
    M1 --&gt; OUT[구역별 수확량 예측&lt;br&gt;시즌 초기 제공]
    M2 --&gt; OUT
</pre><p>수확량 예측 모델이 제공하는 구역별 예측값은 다음 챕터의 처방맵 자동 생성과 연결된다. 수확량이 낮은 구역은 투입 자원을 늘리거나 재배 전략을 조정하는 근거가 된다.</p><h2 id="처방맵-자동-생성" tabindex="-1"><a class="header-anchor" href="#처방맵-자동-생성"><span>처방맵 자동 생성</span></a></h2><h3 id="처방맵이란" tabindex="-1"><a class="header-anchor" href="#처방맵이란"><span>처방맵이란</span></a></h3><p>처방맵(Prescription Map, 가변투입맵)은 필지를 구역으로 나누어 각 구역에 최적화된 투입량(비료, 농약, 씨앗)을 지정한 지도다. CH7 정밀농업 챕터에서 다룬 VRT(Variable Rate Technology)의 입력 데이터가 바로 처방맵이다.</p><p>과거에는 토양 분석 전문가가 수동으로 처방맵을 작성했다. AI는 이 과정을 자동화하고 고려하는 데이터 레이어를 대폭 늘린다.</p><h3 id="데이터-레이어-통합" tabindex="-1"><a class="header-anchor" href="#데이터-레이어-통합"><span>데이터 레이어 통합</span></a></h3><p>처방맵 생성에 투입되는 다중 데이터 레이어는 다음과 같다.</p><ul><li><strong>토양 분석</strong>: EC(전기전도도), 유기물 함량, pH, 질소·인·칼리 분포도</li><li><strong>수확 이력 지도</strong>: 직전 3~5년의 수확량 분포. 지속적으로 낮은 구역은 구조적 문제가 있을 가능성이 높다.</li><li><strong>식생 지수</strong>: 위성 NDVI, NDRE(적색 경계 정규화 식생지수)로 현재 생육 활력 파악</li><li><strong>지형</strong>: 경사도, 배수 방향. 낮은 곳은 과습 위험이 있고 높은 곳은 건조 위험이 있다.</li></ul><h3 id="ai-적용-클러스터링과-분류" tabindex="-1"><a class="header-anchor" href="#ai-적용-클러스터링과-분류"><span>AI 적용: 클러스터링과 분류</span></a></h3><p><strong>클러스터링(비지도 학습)</strong>: K-Means나 DBSCAN으로 유사한 특성을 가진 픽셀/셀을 자동으로 묶어 관리 구역(Management Zone)을 생성한다. 비슷한 토양·수확 특성을 가진 구역에는 동일한 처방을 적용한다.</p><p><strong>분류(지도 학습)</strong>: 과거 수확 결과가 좋았던 구역의 입력 데이터 패턴을 학습하여, 새 시즌의 투입량 카테고리(낮음/중간/높음)를 예측한다.</p><p>클러스터링은 구역 경계를 결정하고, 분류는 각 구역의 투입 수준을 결정하는 식으로 두 방법을 함께 쓰는 것이 일반적이다.</p><pre class="mermaid">flowchart TD
    L1[토양 분석 레이어&lt;br&gt;EC·pH·질소] --&gt; MERGE[다중 레이어 통합&lt;br&gt;래스터 스택]
    L2[수확 이력 레이어&lt;br&gt;3~5년 수확량 분포] --&gt; MERGE
    L3[식생 지수 레이어&lt;br&gt;NDVI·NDRE] --&gt; MERGE
    L4[지형 레이어&lt;br&gt;경사도·배수] --&gt; MERGE
    MERGE --&gt; CLUSTER[클러스터링&lt;br&gt;K-Means / DBSCAN&lt;br&gt;관리 구역 자동 생성]
    CLUSTER --&gt; CLASSIFY[분류 모델&lt;br&gt;구역별 투입 수준 결정&lt;br&gt;낮음 / 중간 / 높음]
    CLASSIFY --&gt; PMAP[처방맵 출력&lt;br&gt;VRT 장비에 업로드]
    PMAP --&gt; VRT[가변율 살포기&lt;br&gt;구역별 실시간 투입 조절]
</pre><h3 id="ch7-정밀농업과의-연결" tabindex="-1"><a class="header-anchor" href="#ch7-정밀농업과의-연결"><span>CH7 정밀농업과의 연결</span></a></h3><p>CH7에서 다룬 정밀농업 사이클(수집 → 분석 → 처방 → 실행)에서 AI는 &quot;분석 → 처방&quot; 단계를 자동화한다. 즉, 농업 AI는 정밀농업의 완성도를 높이는 핵심 엔진이다. 데이터 레이어가 많아질수록, 그리고 수확 이력이 쌓일수록 처방맵의 정확도가 향상되는 학습 효과가 발생한다.</p><div class="hint-container tip"><p class="hint-container-title">핵심 정리</p><ul><li>농업 AI는 수십 개 변수의 비선형 패턴을 학습하여 규칙 기반 시스템이 다루기 어려운 복잡한 의사결정을 자동화한다.</li><li>CNN은 작물 이미지에서 병해충을 90%+ 정확도로 분류하며, 조기 발견 시 방제 비용을 30~50% 절감한다.</li><li>수확량 예측에는 기상·토양·NDVI를 입력으로 하는 XGBoost(회귀)와 LSTM(시계열)이 주로 활용된다.</li><li>처방맵 자동 생성은 클러스터링(구역 분할)과 분류(투입 수준 결정)를 결합하며, CH7 정밀농업 VRT와 직접 연결된다.</li></ul></div><h2 id="다음-챕터" tabindex="-1"><a class="header-anchor" href="#다음-챕터"><span>다음 챕터</span></a></h2><ul><li>다음 : <a href="/study/smart-agriculture/12-agri-data">농업 데이터와 플랫폼</a></li></ul>`,47)]))}const h=l(r,[["render",i],["__file","11-ai-agriculture.html.vue"]]),d=JSON.parse('{"path":"/study/smart-agriculture/11-ai-agriculture.html","title":"AI와 농업","lang":"en-US","frontmatter":{"title":"AI와 농업","description":"작물 분석, 병해충 탐지, 수확량 예측 등 농업 분야 AI 적용 사례와 기술을 이해한다.","date":"2026-04-13T00:00:00.000Z","tags":["스마트농업","AI","딥러닝","병해충","수확량예측"]},"headers":[{"level":2,"title":"농업 AI 개요","slug":"농업-ai-개요","link":"#농업-ai-개요","children":[]},{"level":2,"title":"병해충 탐지","slug":"병해충-탐지","link":"#병해충-탐지","children":[{"level":3,"title":"문제의 중요성","slug":"문제의-중요성","link":"#문제의-중요성","children":[]},{"level":3,"title":"CNN 기반 탐지 파이프라인","slug":"cnn-기반-탐지-파이프라인","link":"#cnn-기반-탐지-파이프라인","children":[]},{"level":3,"title":"PlantVillage 데이터셋","slug":"plantvillage-데이터셋","link":"#plantvillage-데이터셋","children":[]},{"level":3,"title":"조기 발견의 경제적 효과","slug":"조기-발견의-경제적-효과","link":"#조기-발견의-경제적-효과","children":[]}]},{"level":2,"title":"수확량 예측","slug":"수확량-예측","link":"#수확량-예측","children":[{"level":3,"title":"왜 예측이 중요한가","slug":"왜-예측이-중요한가","link":"#왜-예측이-중요한가","children":[]},{"level":3,"title":"입력 데이터","slug":"입력-데이터","link":"#입력-데이터","children":[]},{"level":3,"title":"모델 유형","slug":"모델-유형","link":"#모델-유형","children":[]}]},{"level":2,"title":"처방맵 자동 생성","slug":"처방맵-자동-생성","link":"#처방맵-자동-생성","children":[{"level":3,"title":"처방맵이란","slug":"처방맵이란","link":"#처방맵이란","children":[]},{"level":3,"title":"데이터 레이어 통합","slug":"데이터-레이어-통합","link":"#데이터-레이어-통합","children":[]},{"level":3,"title":"AI 적용: 클러스터링과 분류","slug":"ai-적용-클러스터링과-분류","link":"#ai-적용-클러스터링과-분류","children":[]},{"level":3,"title":"CH7 정밀농업과의 연결","slug":"ch7-정밀농업과의-연결","link":"#ch7-정밀농업과의-연결","children":[]}]},{"level":2,"title":"다음 챕터","slug":"다음-챕터","link":"#다음-챕터","children":[]}],"git":{},"filePathRelative":"_study/smart-agriculture/11-ai-agriculture.md"}');export{h as comp,d as data};
