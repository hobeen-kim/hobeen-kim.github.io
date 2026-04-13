import{_ as e,c as n,d as o,o as r}from"./app-B4giY33Y.js";const l={};function a(s,t){return r(),n("div",null,t[0]||(t[0]=[o(`<h1 id="task-controller-tc-기초" tabindex="-1"><a class="header-anchor" href="#task-controller-tc-기초"><span>Task Controller (TC) 기초</span></a></h1><div class="hint-container info"><p class="hint-container-title">학습 목표</p><ul><li>Task Controller(TC)가 정밀 농업에서 담당하는 역할을 설명할 수 있다.</li><li>TC-Server와 TC-Client의 차이를 구분하고 각각의 위치를 식별할 수 있다.</li><li>Section Control과 Rate Control의 목적과 동작 원리를 비교할 수 있다.</li><li>GPS 위치 데이터가 TC 제어에 어떻게 활용되는지 설명할 수 있다.</li></ul></div><hr><h2 id="_1-tc란-무엇인가" tabindex="-1"><a class="header-anchor" href="#_1-tc란-무엇인가"><span>1. TC란 무엇인가</span></a></h2><p><strong>Task Controller(TC)</strong>는 ISO 11783-10에 정의된 정밀 농업의 핵심 컴포넌트이다.</p><blockquote><p><strong>ISO 11783 Part 10 — Task Controller and Management Information System Data Interchange</strong></p></blockquote><p>TC는 두 가지 핵심 기능을 수행한다.</p><ul><li><strong>자동 제어</strong>: 작업 계획(처방 맵, Prescription Map)에 따라 작업기를 자동으로 제어한다. 밭의 위치별로 미리 지정된 살포량·파종량을 GPS 위치와 연동하여 자동으로 적용한다.</li><li><strong>작업 기록</strong>: 실제 작업 결과(As-Applied Data)를 수집하고 기록한다. 어느 위치에서 얼마나 살포했는지를 나중에 분석할 수 있도록 로그로 남긴다.</li></ul><p>TC가 없던 시대에는 농민이 수동으로 살포량을 조절해야 했다. TC는 이 과정을 자동화하여 비료·농약 과용을 줄이고 생산성을 높이다.</p><hr><h2 id="_2-tc의-역할" tabindex="-1"><a class="header-anchor" href="#_2-tc의-역할"><span>2. TC의 역할</span></a></h2><p>TC는 FMIS(Farm Management Information System, 농장관리시스템)와 작업기 사이를 연결하는 중간 다리이다.</p><pre class="mermaid">flowchart TD
    FMIS[&quot;FMIS&lt;br&gt;(농장관리시스템)&quot;]
    TC[&quot;TC&lt;br&gt;(Task Controller)&quot;]
    ECU[&quot;작업기 ECU&lt;br&gt;(TC-Client)&quot;]
    LOG[&quot;작업 로그&lt;br&gt;(As-Applied)&quot;]

    FMIS --&gt;|&quot;처방 맵&lt;br&gt;(Prescription Map)&quot;| TC
    TC --&gt;|&quot;설정값 전달&lt;br&gt;(Setpoint)&quot;| ECU
    ECU --&gt;|&quot;측정값 보고&lt;br&gt;(Measurement)&quot;| TC
    TC --&gt;|&quot;작업 결과 기록&quot;| LOG
    LOG --&gt;|&quot;작업 데이터 업로드&quot;| FMIS
</pre><p>각 단계의 의미는 다음과 같다.</p><table><thead><tr><th>단계</th><th>방향</th><th>내용</th></tr></thead><tbody><tr><td>처방 맵 수신</td><td>FMIS → TC</td><td>밭의 구획별 목표 살포량·파종량이 담긴 계획 파일</td></tr><tr><td>Setpoint 전달</td><td>TC → 작업기</td><td>GPS 위치에 해당하는 목표 값을 작업기에 명령</td></tr><tr><td>Measurement 수집</td><td>작업기 → TC</td><td>실제 살포된 양, 속도 등 센서 측정값 보고</td></tr><tr><td>작업 로그 기록</td><td>TC → 저장</td><td>위치·시간·실제값을 묶어 As-Applied 파일로 저장</td></tr></tbody></table><hr><h2 id="_3-tc-client-vs-tc-server" tabindex="-1"><a class="header-anchor" href="#_3-tc-client-vs-tc-server"><span>3. TC-Client vs TC-Server</span></a></h2><p>ISOBUS에서 TC는 역할에 따라 두 가지로 구분된다.</p><table><thead><tr><th>구분</th><th>위치</th><th>역할</th></tr></thead><tbody><tr><td><strong>TC-Server</strong></td><td>트랙터(또는 별도 단말기)</td><td>처방 맵을 읽고 TC-Client에 명령을 내림</td></tr><tr><td><strong>TC-Client</strong></td><td>작업기 ECU</td><td>명령을 받아 실제 작업을 수행하고 결과를 보고</td></tr></tbody></table><pre class="mermaid">flowchart LR
    subgraph 트랙터
        TCS[&quot;TC-Server&lt;br&gt;(ISO 11783-10)&quot;]
        GNSS[&quot;GNSS 수신기&quot;]
    end

    subgraph 작업기
        TCC[&quot;TC-Client&lt;br&gt;(작업기 ECU)&quot;]
        VALVE[&quot;밸브 / 액추에이터&quot;]
        SENSOR[&quot;유량 센서&quot;]
    end

    GNSS --&gt;|&quot;GPS 위치&quot;| TCS
    TCS --&gt;|&quot;Value Command&lt;br&gt;(Setpoint)&quot;| TCC
    TCC --&gt;|&quot;Process Data Value&lt;br&gt;(Measurement)&quot;| TCS
    TCC --&gt; VALVE
    SENSOR --&gt; TCC
</pre><ul><li><strong>TC-Server</strong>는 처방 맵에서 현재 GPS 위치에 해당하는 값을 조회하고, 그 값을 TC-Client에 전달한다.</li><li><strong>TC-Client</strong>는 수신한 Setpoint에 맞게 밸브나 모터를 조절하고, 유량 센서 등으로 실제 값을 측정하여 TC-Server에 보고한다.</li></ul><hr><h2 id="_4-section-control과-rate-control" tabindex="-1"><a class="header-anchor" href="#_4-section-control과-rate-control"><span>4. Section Control과 Rate Control</span></a></h2><p>TC의 두 가지 핵심 제어 기능이다.</p><h3 id="section-control" tabindex="-1"><a class="header-anchor" href="#section-control"><span>Section Control</span></a></h3><p>작업기를 여러 <strong>구획(Section)</strong>으로 나누어 각 구획을 독립적으로 ON/OFF하는 기능이다. 이미 작업한 영역이나 작업이 필요 없는 영역의 구획을 자동으로 끈다.</p><p><strong>목적</strong>: 중복 살포(Overlap) 방지 → 비료·농약·씨앗 절감</p><pre class="mermaid">graph TD
    subgraph &quot;살포기 (9m 폭, 3구획)&quot;
        S1[&quot;Section 1&lt;br&gt;3m — ON&quot;]
        S2[&quot;Section 2&lt;br&gt;3m — ON&quot;]
        S3[&quot;Section 3&lt;br&gt;3m — OFF&lt;br&gt;(이미 살포된 구역)&quot;]
    end

    GPS[&quot;GPS 위치&quot;] --&gt; TC[&quot;TC-Server&quot;]
    TC --&gt;|&quot;Section 3 OFF&quot;| S3
    TC --&gt;|&quot;Section 1, 2 ON&quot;| S1
    TC --&gt;|&quot;Section 1, 2 ON&quot;| S2
</pre><h3 id="rate-control" tabindex="-1"><a class="header-anchor" href="#rate-control"><span>Rate Control</span></a></h3><p>GPS 위치에 따라 살포량(Rate)을 <strong>가변적으로</strong> 제어하는 기능이다. 처방 맵에 지정된 위치별 목표량을 실시간으로 반영한다.</p><p><strong>목적</strong>: 토양 조건(양분 상태, 수분 함량)에 맞는 정밀 시비·시약</p><table><thead><tr><th>구분</th><th>설명</th><th>제어 단위</th></tr></thead><tbody><tr><td>Section Control</td><td>구획별 ON/OFF</td><td>논리 값(켜짐/꺼짐)</td></tr><tr><td>Rate Control</td><td>살포량 가변 조절</td><td>연속 수치(L/ha, kg/ha)</td></tr></tbody></table><p>두 기능은 함께 사용할 수 있다. 예를 들어, 밭의 경계에서 외부 구획은 OFF(Section Control)하면서 내부 구획의 살포량은 위치별로 조절(Rate Control)할 수 있다.</p><hr><h2 id="_5-gps-연동과-위치-기반-제어" tabindex="-1"><a class="header-anchor" href="#_5-gps-연동과-위치-기반-제어"><span>5. GPS 연동과 위치 기반 제어</span></a></h2><p>TC는 GPS 위치 데이터를 이용해 현재 위치에 해당하는 처방 맵의 값을 조회한다.</p><h3 id="위치-관련-pgn" tabindex="-1"><a class="header-anchor" href="#위치-관련-pgn"><span>위치 관련 PGN</span></a></h3><p>ISOBUS에서 GPS 정보는 다음 PGN으로 전달된다.</p><table><thead><tr><th>PGN</th><th>이름</th><th>주요 데이터</th></tr></thead><tbody><tr><td><strong>65267</strong> (0xFF13)</td><td>Vehicle Position</td><td>위도(Latitude), 경도(Longitude)</td></tr><tr><td><strong>65256</strong> (0xFF08)</td><td>Vehicle Direction</td><td>방위각(Heading), 피치, 롤</td></tr><tr><td><strong>65265</strong> (0xFF11)</td><td>Wheel-based Vehicle Speed</td><td>차속(km/h)</td></tr></tbody></table><h3 id="위치-기반-제어-흐름" tabindex="-1"><a class="header-anchor" href="#위치-기반-제어-흐름"><span>위치 기반 제어 흐름</span></a></h3><pre class="mermaid">flowchart LR
    GNSS[&quot;GNSS 수신기&lt;br&gt;(NMEA 2000 / NMEA 0183)&quot;]
    PGN[&quot;PGN 65267&lt;br&gt;(위도/경도)&quot;]
    TC[&quot;TC-Server&quot;]
    MAP[&quot;처방 맵&lt;br&gt;(Prescription Map)&quot;]
    CMD[&quot;Value Command&lt;br&gt;(Setpoint 전달)&quot;]
    ECU[&quot;TC-Client&lt;br&gt;(작업기 ECU)&quot;]

    GNSS --&gt;|&quot;위치 데이터&quot;| PGN
    PGN --&gt; TC
    MAP --&gt;|&quot;위치별 목표값 조회&quot;| TC
    TC --&gt;|&quot;해당 위치 목표값&quot;| CMD
    CMD --&gt; ECU
</pre><p>처방 맵은 일반적으로 격자(Grid) 또는 폴리곤(Polygon) 형태로 밭을 구획하고, 각 구획에 목표 값을 지정해 놓다. TC는 현재 GPS 위치가 어느 구획에 속하는지 계산하고, 해당 구획의 목표 값을 TC-Client에 전달한다.</p><h3 id="nmea와-isobus" tabindex="-1"><a class="header-anchor" href="#nmea와-isobus"><span>NMEA와 ISOBUS</span></a></h3><p>GPS 수신기는 NMEA 0183(시리얼) 또는 NMEA 2000(CAN 기반) 프로토콜로 데이터를 제공한다. ISOBUS 네트워크에서는 NMEA 2000과 ISOBUS가 같은 CAN 버스를 공유하거나, 브리지를 통해 연결될 수 있다.</p><hr><blockquote><p><strong>핵심 정리</strong></p><ul><li>TC(Task Controller)는 ISO 11783-10에 정의된 정밀 농업 컴포넌트로, 처방 맵 기반 자동 제어와 작업 로그 기록을 담당한다.</li><li>TC-Server는 트랙터 측에서 처방 맵을 읽고 명령하며, TC-Client는 작업기 ECU로 명령을 실행한다.</li><li>Section Control은 구획별 ON/OFF로 중복 살포를 방지하고, Rate Control은 위치별 살포량을 가변 조절한다.</li><li>GPS 위치(PGN 65267)를 처방 맵과 대조하여 해당 위치의 Setpoint를 실시간으로 TC-Client에 전달한다.</li></ul></blockquote><hr><h2 id="다음-챕터" tabindex="-1"><a class="header-anchor" href="#다음-챕터"><span>다음 챕터</span></a></h2><ul><li>다음 : <a href="/study/isobus/19-tc-process-data">TC 프로세스 데이터</a></li></ul>`,49)]))}const d=e(l,[["render",a],["__file","18-tc-basics.html.vue"]]),c=JSON.parse('{"path":"/study/isobus/18-tc-basics.html","title":"Task Controller (TC) 기초","lang":"en-US","frontmatter":{"title":"Task Controller (TC) 기초","description":"정밀 농업의 핵심 컴포넌트인 Task Controller의 개념, 역할, Section/Rate Control, GPS 연동을 이해한다.","date":"2026-04-13T00:00:00.000Z","tags":["ISOBUS","ISO11783","TaskController","TC","PrecisionAgriculture","SectionControl","RateControl","GPS"],"prev":"/study/isobus/17-vt-commands","next":"/study/isobus/19-tc-process-data"},"headers":[{"level":1,"title":"Task Controller (TC) 기초","slug":"task-controller-tc-기초","link":"#task-controller-tc-기초","children":[{"level":2,"title":"1. TC란 무엇인가","slug":"_1-tc란-무엇인가","link":"#_1-tc란-무엇인가","children":[]},{"level":2,"title":"2. TC의 역할","slug":"_2-tc의-역할","link":"#_2-tc의-역할","children":[]},{"level":2,"title":"3. TC-Client vs TC-Server","slug":"_3-tc-client-vs-tc-server","link":"#_3-tc-client-vs-tc-server","children":[]},{"level":2,"title":"4. Section Control과 Rate Control","slug":"_4-section-control과-rate-control","link":"#_4-section-control과-rate-control","children":[{"level":3,"title":"Section Control","slug":"section-control","link":"#section-control","children":[]},{"level":3,"title":"Rate Control","slug":"rate-control","link":"#rate-control","children":[]}]},{"level":2,"title":"5. GPS 연동과 위치 기반 제어","slug":"_5-gps-연동과-위치-기반-제어","link":"#_5-gps-연동과-위치-기반-제어","children":[{"level":3,"title":"위치 관련 PGN","slug":"위치-관련-pgn","link":"#위치-관련-pgn","children":[]},{"level":3,"title":"위치 기반 제어 흐름","slug":"위치-기반-제어-흐름","link":"#위치-기반-제어-흐름","children":[]},{"level":3,"title":"NMEA와 ISOBUS","slug":"nmea와-isobus","link":"#nmea와-isobus","children":[]}]},{"level":2,"title":"다음 챕터","slug":"다음-챕터","link":"#다음-챕터","children":[]}]}],"git":{},"filePathRelative":"_study/isobus/18-tc-basics.md"}');export{d as comp,c as data};
