import{_ as d,c as r,e as a,o as n}from"./app-Br1t_Uml.js";const e={};function l(i,t){return n(),r("div",null,t[0]||(t[0]=[a(`<div class="hint-container info"><p class="hint-container-title">학습 목표</p><ul><li>농업에서 사용되는 센서를 토양·기상·작물·기계 4개 범주로 분류하고 설명할 수 있다.</li><li>LoRa, NB-IoT 등 주요 IoT 통신 기술의 특성과 농업 적용 이유를 비교할 수 있다.</li><li>센서 노드 → 게이트웨이 → 클라우드 3계층 아키텍처를 도식으로 설명할 수 있다.</li><li>엣지 컴퓨팅의 필요성과 역할을 이해한다.</li></ul></div><h2 id="농업-센서의-종류" tabindex="-1"><a class="header-anchor" href="#농업-센서의-종류"><span>농업 센서의 종류</span></a></h2><p>농업 현장에서는 수많은 물리·화학적 변수를 측정해야 한다. 센서는 측정 대상에 따라 토양, 기상, 작물, 기계의 4개 범주로 나뉜다.</p><h3 id="토양-센서" tabindex="-1"><a class="header-anchor" href="#토양-센서"><span>토양 센서</span></a></h3><table><thead><tr><th>센서 종류</th><th>측정 항목</th><th>활용 목적</th></tr></thead><tbody><tr><td>수분 센서(TDR/FDR)</td><td>체적 수분 함량(%)</td><td>관개 시점·양 결정</td></tr><tr><td>EC 센서</td><td>전기전도도(mS/cm)</td><td>토양 염류 농도, 비료 잔류량 파악</td></tr><tr><td>pH 센서</td><td>토양 산도(pH)</td><td>석회 시용량 결정</td></tr><tr><td>온도 센서</td><td>지온(°C)</td><td>파종 시기, 뿌리 생육 모니터링</td></tr><tr><td>질소 센서</td><td>질산태 질소(mg/kg)</td><td>추비 의사결정</td></tr></tbody></table><h3 id="기상-센서" tabindex="-1"><a class="header-anchor" href="#기상-센서"><span>기상 센서</span></a></h3><table><thead><tr><th>센서 종류</th><th>측정 항목</th><th>활용 목적</th></tr></thead><tbody><tr><td>온도·습도 센서</td><td>기온(°C), 상대습도(%)</td><td>병해충 발생 예측, 관개 조정</td></tr><tr><td>강수량 센서</td><td>강수량(mm)</td><td>관개 스케줄 조정</td></tr><tr><td>풍속·풍향 센서</td><td>풍속(m/s), 풍향</td><td>드론 비행 가부, 농약 살포 시기</td></tr><tr><td>일사량 센서</td><td>광합성 유효 방사(PAR, W/m2)</td><td>증산량 추정, 관개량 계산</td></tr><tr><td>이슬점 센서</td><td>이슬점 온도(°C)</td><td>결로·서리 예측</td></tr></tbody></table><h3 id="작물-센서" tabindex="-1"><a class="header-anchor" href="#작물-센서"><span>작물 센서</span></a></h3><table><thead><tr><th>센서 종류</th><th>측정 항목</th><th>활용 목적</th></tr></thead><tbody><tr><td>NDVI 센서</td><td>정규화 식생 지수</td><td>생육 상태·수세 파악</td></tr><tr><td>엽면적 지수(LAI) 센서</td><td>단위 면적당 잎 면적</td><td>광합성·수량 예측</td></tr><tr><td>엽온 센서(열적외선)</td><td>잎 표면 온도(°C)</td><td>수분 스트레스 감지</td></tr><tr><td>과실 성숙도 센서</td><td>당도(Brix), 색상</td><td>수확 적기 판단</td></tr></tbody></table><h3 id="기계-센서" tabindex="-1"><a class="header-anchor" href="#기계-센서"><span>기계 센서</span></a></h3><table><thead><tr><th>센서 종류</th><th>측정 항목</th><th>활용 목적</th></tr></thead><tbody><tr><td>유량 센서</td><td>농약·비료 살포량(L/min)</td><td>가변살포 정확도 검증</td></tr><tr><td>압력 센서</td><td>노즐 압력(bar)</td><td>살포 품질 관리</td></tr><tr><td>RPM 센서</td><td>엔진·PTO 회전수(rpm)</td><td>작업 최적화, 연료 효율</td></tr><tr><td>수확량 센서</td><td>곡물 유량(t/h)</td><td>수확량 맵 생성</td></tr></tbody></table><h2 id="iot-통신-기술" tabindex="-1"><a class="header-anchor" href="#iot-통신-기술"><span>IoT 통신 기술</span></a></h2><p>센서가 수집한 데이터는 통신 기술을 통해 게이트웨이 또는 클라우드로 전송된다. 농업 환경은 전파 장애물이 많고 전력 공급이 어려우며 넓은 면적을 커버해야 하므로, 통신 기술 선택이 매우 중요하다.</p><table><thead><tr><th>기술</th><th>전송 거리</th><th>전력 소비</th><th>데이터 속도</th><th>비용</th><th>농업 적합성</th></tr></thead><tbody><tr><td>LoRa/LoRaWAN</td><td>2~15 km</td><td>매우 낮음</td><td>매우 낮음(~50 kbps)</td><td>낮음</td><td>매우 높음 - 저전력 장거리</td></tr><tr><td>NB-IoT</td><td>1~10 km</td><td>낮음</td><td>낮음(~250 kbps)</td><td>중간(통신사 요금)</td><td>높음 - 이동통신망 활용</td></tr><tr><td>Sigfox</td><td>3~50 km</td><td>매우 낮음</td><td>매우 낮음(100 bps)</td><td>낮음</td><td>중간 - 초소량 데이터만</td></tr><tr><td>Wi-Fi</td><td>50~100 m</td><td>높음</td><td>높음(수백 Mbps)</td><td>낮음</td><td>시설농업 내부 한정</td></tr><tr><td>Bluetooth/BLE</td><td>10~100 m</td><td>낮음</td><td>중간(1~3 Mbps)</td><td>낮음</td><td>근거리 센서 연결</td></tr><tr><td>Zigbee</td><td>10~100 m</td><td>낮음</td><td>낮음(250 kbps)</td><td>낮음</td><td>시설농업 메시 네트워크</td></tr><tr><td>셀룰러(LTE/5G)</td><td>수 km</td><td>높음</td><td>매우 높음</td><td>높음(요금)</td><td>영상 스트리밍, 드론</td></tr></tbody></table><p>농업 노지에서는 <strong>LoRaWAN이 사실상 표준</strong>으로 자리잡았다. 배터리로 수년간 운영 가능한 저전력 특성과 수 킬로미터에 달하는 장거리 전송 능력이 농업 환경에 최적화되어 있다.</p><pre class="mermaid">quadrantChart
    title IoT 통신 기술 비교 (전송 거리 vs 전력 소비)
    x-axis 낮은 전력 소비 --&gt; 높은 전력 소비
    y-axis 짧은 전송 거리 --&gt; 긴 전송 거리
    quadrant-1 장거리·고전력
    quadrant-2 장거리·저전력(농업 최적)
    quadrant-3 단거리·저전력
    quadrant-4 단거리·고전력
    LoRa/LoRaWAN: [0.15, 0.80]
    NB-IoT: [0.30, 0.70]
    Sigfox: [0.10, 0.85]
    셀룰러 LTE: [0.85, 0.75]
    Wi-Fi: [0.70, 0.20]
    Bluetooth: [0.35, 0.15]
    Zigbee: [0.30, 0.20]
</pre><h2 id="센서-네트워크-아키텍처" tabindex="-1"><a class="header-anchor" href="#센서-네트워크-아키텍처"><span>센서 네트워크 아키텍처</span></a></h2><p>농업 IoT 시스템은 3계층 구조로 설계된다. 각 계층은 역할이 명확히 구분된다.</p><pre class="mermaid">flowchart TD
    subgraph field[농지 - 필드 계층]
        S1[토양 수분 센서 노드]
        S2[기상 관측 센서 노드]
        S3[작물 생육 센서 노드]
        S4[기계 센서 노드]
    end

    subgraph edge[엣지 계층]
        GW[LoRa 게이트웨이&lt;br&gt;데이터 집계·전처리&lt;br&gt;이상값 필터링&lt;br&gt;로컬 알림 발송]
    end

    subgraph cloud[클라우드 계층]
        DB[(시계열 DB)]
        AI[AI 분석 엔진]
        FMIS[FMIS 농장관리시스템]
        APP[모바일·웹 앱]
    end

    S1 --&gt;|LoRa 무선| GW
    S2 --&gt;|LoRa 무선| GW
    S3 --&gt;|LoRa 무선| GW
    S4 --&gt;|LoRa 무선| GW
    GW --&gt;|LTE/이더넷| DB
    DB --&gt; AI
    AI --&gt; FMIS
    FMIS --&gt; APP
</pre><p>각 계층의 역할은 다음과 같다.</p><ul><li><strong>필드 계층(센서 노드)</strong>: 실제 물리 데이터를 측정하고 LoRa 등의 무선 통신으로 게이트웨이에 전송한다. 배터리 구동이 일반적이며, 측정 주기는 분~시간 단위로 설정한다.</li><li><strong>엣지 계층(게이트웨이)</strong>: 수십~수백 개 센서 노드로부터 데이터를 수집하고 1차 전처리를 수행한다. 인터넷이 끊겨도 로컬에서 기본 알림을 발송할 수 있다.</li><li><strong>클라우드 계층</strong>: 장기 데이터 저장, AI 분석, 사용자 인터페이스 제공을 담당한다. 시계열 데이터베이스(InfluxDB, TimescaleDB 등)를 주로 사용한다.</li></ul><h2 id="엣지-컴퓨팅" tabindex="-1"><a class="header-anchor" href="#엣지-컴퓨팅"><span>엣지 컴퓨팅</span></a></h2><p>모든 센서 데이터를 클라우드로 직접 전송하면 여러 문제가 발생한다. 엣지 컴퓨팅은 이를 해결하기 위해 클라우드로 보내기 전 현장(엣지)에서 데이터를 처리하는 접근법이다.</p><p><strong>클라우드 직접 전송의 문제점</strong>:</p><ul><li><strong>지연(Latency)</strong>: 토양 과습 경보처럼 즉각적인 반응이 필요한 상황에서 클라우드 왕복 지연은 치명적이다.</li><li><strong>통신 비용</strong>: 수백 개 센서가 수초 간격으로 데이터를 전송하면 통신 트래픽과 비용이 급증한다.</li><li><strong>오프라인 취약성</strong>: 농촌 지역은 통신 인프라가 불안정하다. 클라우드 의존도가 높으면 통신 장애 시 시스템 전체가 마비된다.</li></ul><p><strong>엣지 컴퓨팅의 처리 방식</strong>:</p><pre class="mermaid">flowchart LR
    A[센서 원시 데이터&lt;br&gt;1초 간격, 고빈도] --&gt; B{엣지 게이트웨이&lt;br&gt;전처리}
    B --&gt; C[이상값 제거&lt;br&gt;노이즈 필터링]
    B --&gt; D[통계 집계&lt;br&gt;5분 평균·최대·최소]
    B --&gt; E[임계값 비교&lt;br&gt;즉시 알림 발송]
    C --&gt; F[요약 데이터만 클라우드 전송&lt;br&gt;데이터량 95% 감소]
    D --&gt; F
    E --&gt; G[로컬 경보&lt;br&gt;인터넷 불필요]
</pre><p>엣지 게이트웨이에서 1초 간격 원시 데이터를 5분 평균으로 집계하면 데이터량이 약 300분의 1로 줄어든다. 이상값 필터링과 국소 알림 처리까지 엣지에서 수행하면 클라우드는 핵심 분석과 장기 저장에만 집중할 수 있다.</p><div class="hint-container tip"><p class="hint-container-title">핵심 정리</p><ul><li>농업 센서는 토양(수분·EC·pH), 기상(온도·습도·일사량), 작물(NDVI·엽온), 기계(유량·압력·RPM) 4개 범주로 구분된다.</li><li>노지 농업의 IoT 통신은 저전력·장거리 특성의 LoRaWAN이 사실상 표준이다.</li><li>센서 네트워크는 필드(노드) → 엣지(게이트웨이) → 클라우드의 3계층 구조로 설계된다.</li><li>엣지 컴퓨팅은 지연 감소, 통신 비용 절감, 오프라인 대응을 위해 현장에서 데이터를 1차 처리한다.</li></ul></div><h2 id="다음-챕터" tabindex="-1"><a class="header-anchor" href="#다음-챕터"><span>다음 챕터</span></a></h2><ul><li>다음 : <a href="/study/smart-agriculture/04-aerial-satellite">항공·위성 센싱</a></li></ul>`,31)]))}const h=d(e,[["render",l],["__file","03-iot-sensors.html.vue"]]),o=JSON.parse('{"path":"/study/smart-agriculture/03-iot-sensors.html","title":"농업 IoT와 센서","lang":"en-US","frontmatter":{"title":"농업 IoT와 센서","description":"농업 현장에서 사용되는 센서의 종류, IoT 통신 기술, 엣지 컴퓨팅의 역할을 이해한다.","date":"2026-04-13T00:00:00.000Z","tags":["스마트농업","IoT","센서","LoRa","엣지컴퓨팅"]},"headers":[{"level":2,"title":"농업 센서의 종류","slug":"농업-센서의-종류","link":"#농업-센서의-종류","children":[{"level":3,"title":"토양 센서","slug":"토양-센서","link":"#토양-센서","children":[]},{"level":3,"title":"기상 센서","slug":"기상-센서","link":"#기상-센서","children":[]},{"level":3,"title":"작물 센서","slug":"작물-센서","link":"#작물-센서","children":[]},{"level":3,"title":"기계 센서","slug":"기계-센서","link":"#기계-센서","children":[]}]},{"level":2,"title":"IoT 통신 기술","slug":"iot-통신-기술","link":"#iot-통신-기술","children":[]},{"level":2,"title":"센서 네트워크 아키텍처","slug":"센서-네트워크-아키텍처","link":"#센서-네트워크-아키텍처","children":[]},{"level":2,"title":"엣지 컴퓨팅","slug":"엣지-컴퓨팅","link":"#엣지-컴퓨팅","children":[]},{"level":2,"title":"다음 챕터","slug":"다음-챕터","link":"#다음-챕터","children":[]}],"git":{},"filePathRelative":"_study/smart-agriculture/03-iot-sensors.md"}');export{h as comp,o as data};
