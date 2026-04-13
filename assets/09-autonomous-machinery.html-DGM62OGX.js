import{_ as n,c as l,e as r,o as a}from"./app-BTUxan41.js";const e={};function i(s,t){return a(),l("div",null,t[0]||(t[0]=[r(`<div class="hint-container info"><p class="hint-container-title">학습 목표</p><ul><li>자동차 자율주행과 농기계 자율주행의 차이점을 설명할 수 있다.</li><li>SAE J3016 자율주행 레벨(0~5)을 농기계 맥락에 적용할 수 있다.</li><li>농기계 자율주행의 핵심 기술 구성 요소를 열거하고 역할을 설명할 수 있다.</li><li>AB 직선·나선형·등고선 경로 패턴의 특성과 적용 상황을 비교할 수 있다.</li><li>ISO 18497 안전 표준의 주요 요구사항을 설명할 수 있다.</li></ul></div><h2 id="농기계-자율주행-개요" tabindex="-1"><a class="header-anchor" href="#농기계-자율주행-개요"><span>농기계 자율주행 개요</span></a></h2><p>자율주행이라 하면 도심 도로를 달리는 로보택시를 먼저 떠올리기 쉽다. 그러나 농기계 자율주행은 자동차 자율주행과 근본적으로 다른 환경에서 작동한다.</p><p><strong>통제된 환경</strong>: 농지는 폐쇄된 공간이다. 신호등, 횡단보도, 일반 차량이 없으며 예측 불가능한 돌발 상황이 도로에 비해 현저히 적다. 이는 자율주행 구현 난도를 낮추는 요인이다.</p><p><strong>정형화된 작업 패턴</strong>: 경운, 파종, 방제, 수확 등 농기계 작업은 반복적인 직선 경로나 정해진 패턴으로 수행된다. 경로의 예측 가능성이 높아 경로 계획이 상대적으로 단순하다.</p><p><strong>저속 대형 장비</strong>: 트랙터나 콤바인의 작업 속도는 일반적으로 시속 5~15km 수준이다. 저속이지만 장비 자체의 중량과 부피가 크기 때문에 충돌 시 피해가 심각하다. 또한 구동 관성이 커서 제동 거리가 길다.</p><p>이러한 특성 덕분에 농기계 자율주행은 자동차 자율주행보다 먼저 실용화 단계에 진입했다.</p><h3 id="sae-j3016-레벨을-농기계에-적용" tabindex="-1"><a class="header-anchor" href="#sae-j3016-레벨을-농기계에-적용"><span>SAE J3016 레벨을 농기계에 적용</span></a></h3><p>SAE J3016은 자율주행 레벨을 0~5의 6단계로 정의한다. 농기계 분야에서는 이 레벨이 실제 제품으로 어떻게 구현되는지 살펴본다.</p><table><thead><tr><th>레벨</th><th>명칭</th><th>인간의 역할</th><th>농기계 적용 사례</th></tr></thead><tbody><tr><td>0</td><td>자동화 없음</td><td>전체 운전 담당</td><td>재래식 트랙터</td></tr><tr><td>1</td><td>운전자 보조</td><td>대부분 직접 운전</td><td>자동 조향 보조(핸들 교정)</td></tr><tr><td>2</td><td>부분 자동화</td><td>상시 감시 필요</td><td>RTK-GPS 직선 자동 주행</td></tr><tr><td>3</td><td>조건부 자동화</td><td>필요시 개입 대기</td><td>특정 필지 내 완전 자동 작업</td></tr><tr><td>4</td><td>고도 자동화</td><td>지정 구역 내 불필요</td><td>울타리 구역 내 무인 트랙터</td></tr><tr><td>5</td><td>완전 자동화</td><td>전혀 불필요</td><td>(상용화 미도달)</td></tr></tbody></table><p>현재 상용 제품 대부분은 레벨 2~3 수준이다. John Deere의 AutoTrac, Kubota의 KSAS 등이 레벨 2에 해당하며, 일부 시범 사업 제품이 레벨 4에 근접해 있다.</p><pre class="mermaid">flowchart LR
    L0[레벨 0&lt;br&gt;수동 운전] --&gt; L1[레벨 1&lt;br&gt;조향 보조]
    L1 --&gt; L2[레벨 2&lt;br&gt;직선 자동 주행&lt;br&gt;상시 감시 필요]
    L2 --&gt; L3[레벨 3&lt;br&gt;필지 내 자동 작업&lt;br&gt;개입 대기]
    L3 --&gt; L4[레벨 4&lt;br&gt;구역 내 무인&lt;br&gt;시범 단계]
    L4 --&gt; L5[레벨 5&lt;br&gt;완전 무인&lt;br&gt;미래 목표]
    style L2 fill:#d4edda
    style L3 fill:#d4edda
    style L4 fill:#fff3cd
    style L5 fill:#f8d7da
</pre><h2 id="핵심-기술-요소" tabindex="-1"><a class="header-anchor" href="#핵심-기술-요소"><span>핵심 기술 요소</span></a></h2><p>농기계 자율주행은 위치 파악, 자세 측정, 장애물 감지, 경로 계획, 조향 제어의 5개 기술 모듈이 유기적으로 연동되어 작동한다.</p><p><strong>RTK-GPS (위치 측위)</strong>: Real-Time Kinematic GPS는 기준국 보정 신호를 활용해 2~3cm 수준의 고정밀 위치 정보를 제공한다. 일반 GPS의 오차가 수 미터인 것과 대조적이다. 트랙터가 이전 패스와 정확히 일치하는 경로로 주행하려면 이 수준의 정밀도가 필수다.</p><p><strong>IMU (자세 측정)</strong>: Inertial Measurement Unit은 가속도계와 자이로스코프로 농기계의 기울기(경사지)와 방위각을 측정한다. 경사지에서 GPS 위치만으로는 실제 트랙터 자세를 알 수 없으므로, IMU가 RTK-GPS를 보완한다.</p><p><strong>LiDAR / 카메라 (장애물 감지)</strong>: 전방 LiDAR는 포인트 클라우드로 장애물 유무와 거리를 실시간 탐지한다. 카메라는 사람, 동물, 농기구 등 물체를 분류하는 데 활용된다. 두 센서를 융합하면 감지 신뢰성이 높아진다.</p><p><strong>경로 플래너</strong>: 작업 필지 형상, 작업 폭, 헤드랜드 여백 등을 입력받아 최적 주행 경로를 사전 계산한다. 실시간으로 장애물 회피 경로를 재계산하기도 한다.</p><p><strong>조향 컨트롤러</strong>: 계산된 경로와 현재 위치 오차를 입력으로 받아 조향각을 제어한다. Pure Pursuit, Stanley Method 등의 기하학적 제어 알고리즘이 널리 쓰인다.</p><pre class="mermaid">flowchart TD
    subgraph 센서층
        A[RTK-GPS&lt;br&gt;위치 2~3cm 정밀도]
        B[IMU&lt;br&gt;자세·기울기]
        C[LiDAR&lt;br&gt;장애물 거리]
        D[카메라&lt;br&gt;물체 분류]
    end
    subgraph 처리층
        E[센서 융합&lt;br&gt;Kalman Filter]
        F[경로 플래너&lt;br&gt;AB / 나선 / 등고선]
        G[장애물 감지기&lt;br&gt;실시간 경보]
    end
    subgraph 제어층
        H[조향 컨트롤러&lt;br&gt;Pure Pursuit / Stanley]
        I[작업기 제어&lt;br&gt;ISOBUS 명령]
    end
    A --&gt; E
    B --&gt; E
    C --&gt; G
    D --&gt; G
    E --&gt; F
    G --&gt; F
    F --&gt; H
    H --&gt; I
</pre><h2 id="경로-계획" tabindex="-1"><a class="header-anchor" href="#경로-계획"><span>경로 계획</span></a></h2><p>경로 계획은 농기계 자율주행의 핵심 소프트웨어 모듈이다. 어떤 경로를 선택하느냐에 따라 작업 효율, 연료 소모, 토양 압밀 등이 달라진다.</p><h3 id="ab-직선-패턴" tabindex="-1"><a class="header-anchor" href="#ab-직선-패턴"><span>AB 직선 패턴</span></a></h3><p>가장 기본적인 경로 패턴이다. 작업자가 시작점 A와 방향 B를 지정하면, 시스템이 작업 폭 간격으로 평행한 직선 경로를 자동 생성한다. 평탄하고 규칙적인 직사각형 필지에 최적이다.</p><h3 id="나선형-spiral-패턴" tabindex="-1"><a class="header-anchor" href="#나선형-spiral-패턴"><span>나선형(Spiral) 패턴</span></a></h3><p>필지 외곽에서 안쪽으로 나선형으로 수렴하는 경로다. 헤드랜드 턴 횟수를 줄일 수 있어 대형 정사각형 필지에서 효율적이다. 다만 나선이 좁아질수록 곡률이 커져 조향 정밀도 요구가 높아진다.</p><h3 id="등고선-contour-패턴" tabindex="-1"><a class="header-anchor" href="#등고선-contour-패턴"><span>등고선(Contour) 패턴</span></a></h3><p>경사지에서 등고선을 따라 주행하는 패턴이다. 경사면을 횡으로 가로질러 작업하면 토양 침식을 줄이고 작업기가 일정한 깊이를 유지하기 쉽다. 지형 DEM(수치고도모델) 데이터가 필요하다.</p><h3 id="헤드랜드-두렁-턴-전략" tabindex="-1"><a class="header-anchor" href="#헤드랜드-두렁-턴-전략"><span>헤드랜드(두렁) 턴 전략</span></a></h3><p>필지 끝에서 방향을 전환하는 구역을 헤드랜드라 한다. 턴 방식에는 U-턴(단순하지만 넓은 공간 필요), Fishtail-턴(좁은 헤드랜드에 적합), 오메가(Ω)-턴(3점 방향 전환) 등이 있다. 헤드랜드 폭과 기계 회전반경에 따라 최적 턴 방식을 자동 선택한다.</p><pre class="mermaid">flowchart LR
    subgraph 경로패턴선택
        P1{필지 형태}
        P1 --&gt;|직사각형 평탄지| P2[AB 직선 패턴]
        P1 --&gt;|대형 정사각형| P3[나선형 패턴]
        P1 --&gt;|경사지| P4[등고선 패턴]
    end
    subgraph 헤드랜드전략
        P2 --&gt; T1{헤드랜드 폭}
        P3 --&gt; T1
        P4 --&gt; T1
        T1 --&gt;|충분히 넓음| T2[U-턴]
        T1 --&gt;|중간| T3[Fishtail-턴]
        T1 --&gt;|좁음| T4[Omega-턴]
    end
    T2 --&gt; OUT[최적 경로 확정]
    T3 --&gt; OUT
    T4 --&gt; OUT
</pre><p>경로 최적화의 목표는 단순히 최단 거리가 아니다. 중복 작업 면적 최소화, 헤드랜드 주행 거리 최소화, 연료 효율 최대화, 토양 압밀 분산을 종합적으로 고려한 다목적 최적화 문제다.</p><h2 id="안전-표준" tabindex="-1"><a class="header-anchor" href="#안전-표준"><span>안전 표준</span></a></h2><p>자율주행 농기계는 무인 또는 부분 무인으로 작동하므로, 사람·동물과의 충돌 방지가 가장 중요한 설계 요구사항이다.</p><h3 id="iso-18497" tabindex="-1"><a class="header-anchor" href="#iso-18497"><span>ISO 18497</span></a></h3><p>ISO 18497은 농림용 기계의 부분 자동화 안전 요구사항을 규정하는 국제 표준이다. 주요 내용은 다음과 같다.</p><ul><li><strong>위험 구역 정의</strong>: 기계 주변에 즉각 정지가 필요한 위험 구역(경보 구역, 정지 구역)을 설정한다.</li><li><strong>감지 시스템 요건</strong>: 사람·동물을 지정된 거리 내에서 신뢰성 있게 감지해야 한다.</li><li><strong>비상 정지</strong>: 감지 신호 수신 후 규정 시간 내에 안전 상태(정지)에 도달해야 한다.</li><li><strong>원격 모니터링</strong>: 작업자가 언제든지 기계 상태를 확인하고 개입할 수 있어야 한다.</li></ul><h3 id="비상-정지-프로토콜" tabindex="-1"><a class="header-anchor" href="#비상-정지-프로토콜"><span>비상 정지 프로토콜</span></a></h3><p>비상 정지는 계층적으로 설계된다.</p><ol><li><strong>소프트웨어 정지</strong>: 센서가 장애물을 감지하면 제어 소프트웨어가 엔진 출력을 줄이고 브레이크를 작동한다.</li><li><strong>하드웨어 정지</strong>: 소프트웨어 경로와 독립적인 하드웨어 회로가 전자 신호로 직접 브레이크를 잠근다.</li><li><strong>기계적 정지</strong>: 모든 전자 시스템이 고장나도 기계적 브레이크가 작동하도록 설계한다.</li></ol><h3 id="통신-두절-시-대응" tabindex="-1"><a class="header-anchor" href="#통신-두절-시-대응"><span>통신 두절 시 대응</span></a></h3><p>RTK 보정 신호나 원격 모니터링 통신이 두절되면 자동으로 안전 모드에 진입한다.</p><table><thead><tr><th>상황</th><th>대응</th></tr></thead><tbody><tr><td>RTK 신호 손실</td><td>작업 정지, 현 위치에서 대기</td></tr><tr><td>원격 모니터링 두절</td><td>경보 발령 후 N초 내 작업 정지</td></tr><tr><td>센서 오작동 감지</td><td>즉시 안전 정지</td></tr><tr><td>배터리/전원 이상</td><td>제어된 감속 후 정지</td></tr></tbody></table><div class="hint-container tip"><p class="hint-container-title">핵심 정리</p><ul><li>농기계 자율주행은 통제된 환경, 정형화된 패턴, 저속 대형 장비라는 특성 덕분에 도로 자율주행보다 먼저 실용화됐다.</li><li>현재 상용 농기계는 SAE 레벨 2~3 수준이며, 레벨 4 시범 사업이 진행 중이다.</li><li>RTK-GPS(위치), IMU(자세), LiDAR/카메라(장애물)의 센서 융합이 정밀 자율주행의 핵심이다.</li><li>경로 패턴은 필지 형태와 지형에 따라 AB 직선, 나선형, 등고선 중 선택하며 헤드랜드 턴 전략과 연계한다.</li><li>ISO 18497은 농기계 자율주행 안전의 국제 표준으로, 계층적 비상 정지와 통신 두절 대응을 요구한다.</li></ul></div><h2 id="다음-챕터" tabindex="-1"><a class="header-anchor" href="#다음-챕터"><span>다음 챕터</span></a></h2><ul><li>다음 : <a href="/study/smart-agriculture/10-agri-robotics">농업 로보틱스</a></li></ul>`,46)]))}const h=n(e,[["render",i],["__file","09-autonomous-machinery.html.vue"]]),o=JSON.parse('{"path":"/study/smart-agriculture/09-autonomous-machinery.html","title":"자율주행 농기계","lang":"en-US","frontmatter":{"title":"자율주행 농기계","description":"농기계 자율주행의 레벨 분류, 경로 계획 알고리즘, 안전 표준을 이해한다.","date":"2026-04-13T00:00:00.000Z","tags":["스마트농업","자율주행","트랙터","경로계획","안전"]},"headers":[{"level":2,"title":"농기계 자율주행 개요","slug":"농기계-자율주행-개요","link":"#농기계-자율주행-개요","children":[{"level":3,"title":"SAE J3016 레벨을 농기계에 적용","slug":"sae-j3016-레벨을-농기계에-적용","link":"#sae-j3016-레벨을-농기계에-적용","children":[]}]},{"level":2,"title":"핵심 기술 요소","slug":"핵심-기술-요소","link":"#핵심-기술-요소","children":[]},{"level":2,"title":"경로 계획","slug":"경로-계획","link":"#경로-계획","children":[{"level":3,"title":"AB 직선 패턴","slug":"ab-직선-패턴","link":"#ab-직선-패턴","children":[]},{"level":3,"title":"나선형(Spiral) 패턴","slug":"나선형-spiral-패턴","link":"#나선형-spiral-패턴","children":[]},{"level":3,"title":"등고선(Contour) 패턴","slug":"등고선-contour-패턴","link":"#등고선-contour-패턴","children":[]},{"level":3,"title":"헤드랜드(두렁) 턴 전략","slug":"헤드랜드-두렁-턴-전략","link":"#헤드랜드-두렁-턴-전략","children":[]}]},{"level":2,"title":"안전 표준","slug":"안전-표준","link":"#안전-표준","children":[{"level":3,"title":"ISO 18497","slug":"iso-18497","link":"#iso-18497","children":[]},{"level":3,"title":"비상 정지 프로토콜","slug":"비상-정지-프로토콜","link":"#비상-정지-프로토콜","children":[]},{"level":3,"title":"통신 두절 시 대응","slug":"통신-두절-시-대응","link":"#통신-두절-시-대응","children":[]}]},{"level":2,"title":"다음 챕터","slug":"다음-챕터","link":"#다음-챕터","children":[]}],"git":{},"filePathRelative":"_study/smart-agriculture/09-autonomous-machinery.md"}');export{h as comp,o as data};
