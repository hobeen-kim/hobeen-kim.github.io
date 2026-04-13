import{_ as n,c as d,e,o as a}from"./app-DktBU1vW.js";const s={};function r(i,t){return a(),d("div",null,t[0]||(t[0]=[e(`<h1 id="can-통신-입문" tabindex="-1"><a class="header-anchor" href="#can-통신-입문"><span>CAN 통신 입문</span></a></h1><div class="hint-container info"><p class="hint-container-title">학습 목표</p><ul><li>CAN의 탄생 배경과 ISO 11898 표준을 설명할 수 있다.</li><li>CAN이 사용되는 분야를 나열할 수 있다.</li><li>멀티마스터, 메시지 기반 브로드캐스트, 중재(Arbitration) 개념을 이해한다.</li><li>CAN과 다른 통신 방식의 차이를 비교할 수 있다.</li></ul></div><hr><h2 id="_1-can이란" tabindex="-1"><a class="header-anchor" href="#_1-can이란"><span>1. CAN이란</span></a></h2><p><strong>CAN(Controller Area Network)</strong>은 1986년 <strong>Bosch(보쉬)</strong>가 개발한 직렬 통신 프로토콜이다. 원래 자동차 내부의 여러 ECU를 적은 배선으로 연결하기 위해 설계되었다.</p><p>당시 자동차 전장 시스템이 복잡해지면서 배선 무게만 50~60kg에 달했다. Bosch는 이 문제를 해결하기 위해 2선 버스 하나로 모든 ECU를 연결하는 방식을 고안했다.</p><p>1991년 Mercedes-Benz S-Class에 처음 양산 적용되었고, 이후 <strong>ISO 11898</strong>로 국제 표준화되었다.</p><pre class="mermaid">timeline
    title CAN 기술 발전사
    1986 : Bosch가 CAN 프로토콜 발표
    1991 : Mercedes-Benz S-Class에 최초 양산 적용
    1993 : ISO 11898로 국제 표준화
    2003 : J1939 기반 ISOBUS(ISO 11783) 완성
    2012 : Bosch가 CAN FD 규격 발표
</pre><p><strong>CAN 표준 체계:</strong></p><table><thead><tr><th>표준</th><th>내용</th></tr></thead><tbody><tr><td>ISO 11898-1</td><td>데이터 링크 계층 (프레임 구조, 에러 처리)</td></tr><tr><td>ISO 11898-2</td><td>고속 물리 계층 (최대 1 Mbps)</td></tr><tr><td>ISO 11898-3</td><td>저속 내결함성 물리 계층 (최대 125 kbps)</td></tr><tr><td>ISO 11898-5</td><td>저전력 모드 (슬립/웨이크업)</td></tr></tbody></table><hr><h2 id="_2-can을-쓰는-곳" tabindex="-1"><a class="header-anchor" href="#_2-can을-쓰는-곳"><span>2. CAN을 쓰는 곳</span></a></h2><p>CAN은 자동차에서 시작했지만, 지금은 훨씬 넓은 분야에서 사용된다.</p><pre class="mermaid">mindmap
  root((CAN 적용 분야))
    자동차
      엔진 제어
      ABS 브레이크
      에어백 시스템
      전동 파워스티어링
      계기판
    농기계
      트랙터 ECU
      ISOBUS 작업기
      GPS 자동조향
      수확량 모니터
    산업기계
      PLC 제어
      로봇 관절 제어
      컨베이어 시스템
    의료장비
      수술 로봇
      영상 진단 장비
    선박
      엔진 모니터링
      항법 장비
    엘리베이터
      층별 제어기
      도어 제어
</pre><p>특히 <strong>ISOBUS(ISO 11783)</strong>는 CAN을 기반으로 농기계 전용으로 확장한 표준이다. 트랙터와 작업기(파종기, 방제기 등)가 브랜드가 달라도 서로 통신할 수 있다.</p><hr><h2 id="_3-can의-핵심-특징" tabindex="-1"><a class="header-anchor" href="#_3-can의-핵심-특징"><span>3. CAN의 핵심 특징</span></a></h2><h3 id="_3-1-멀티마스터-multi-master" tabindex="-1"><a class="header-anchor" href="#_3-1-멀티마스터-multi-master"><span>3.1 멀티마스터 (Multi-Master)</span></a></h3><p>기존 통신 방식은 마스터(명령하는 쪽)가 슬레이브(응답하는 쪽)에게 일방적으로 요청하는 구조가 많다. CAN에서는 <strong>어떤 노드든 원할 때 메시지를 전송</strong>할 수 있다.</p><p>엔진 ECU도 먼저 보낼 수 있고, 브레이크 ECU도 먼저 보낼 수 있다. 단, 동시에 두 노드가 전송을 시도하면 <strong>중재(Arbitration)</strong> 과정을 통해 우선순위가 높은 메시지가 먼저 전송된다.</p><h3 id="_3-2-메시지-기반-브로드캐스트" tabindex="-1"><a class="header-anchor" href="#_3-2-메시지-기반-브로드캐스트"><span>3.2 메시지 기반 브로드캐스트</span></a></h3><p>CAN에서는 &quot;누구에게 보낸다&quot;는 수신자 주소가 없다. 대신 <strong>메시지 ID</strong>로 내용의 종류를 나타낸다.</p><p>예를 들어 ID <code>0x0CF004B4</code>라면 &quot;엔진 상태 정보&quot;를 의미한다고 약속한다. 이 메시지가 버스에 올라오면 버스에 연결된 모든 노드가 받다. 각 노드는 자신이 필요한 ID만 골라서 처리한다.</p><pre class="mermaid">sequenceDiagram
    participant 엔진ECU
    participant 버스
    participant 계기판ECU
    participant 변속기ECU
    participant ABS_ECU

    엔진ECU-&gt;&gt;버스: ID=0x100, 데이터=RPM:2000
    버스-&gt;&gt;계기판ECU: ID=0x100, 데이터=RPM:2000
    버스-&gt;&gt;변속기ECU: ID=0x100, 데이터=RPM:2000
    버스-&gt;&gt;ABS_ECU: ID=0x100, 데이터=RPM:2000

    Note over 계기판ECU: ID 0x100 필요! → RPM 표시
    Note over 변속기ECU: ID 0x100 필요! → 기어 결정
    Note over ABS_ECU: ID 0x100 불필요 → 무시
</pre><h3 id="_3-3-우선순위-기반-중재-csma-cd-amp" tabindex="-1"><a class="header-anchor" href="#_3-3-우선순위-기반-중재-csma-cd-amp"><span>3.3 우선순위 기반 중재 (CSMA/CD+AMP)</span></a></h3><p>CAN은 <strong>CSMA/CD+AMP</strong> 방식을 사용한다.</p><ul><li><strong>CSMA (Carrier Sense Multiple Access)</strong>: 버스가 비어 있을 때만 전송 시작</li><li><strong>CD (Collision Detection)</strong>: 충돌 감지</li><li><strong>AMP (Arbitration on Message Priority)</strong>: 메시지 우선순위로 중재</li></ul><p>두 노드가 동시에 전송을 시작하면, <strong>ID 값이 낮을수록 우선순위가 높다</strong>. ID를 비트 단위로 비교해 나가면서 먼저 Recessive(1)를 보낸 노드가 자동으로 물러난다.</p><div class="language-text line-numbers-mode" data-highlighter="prismjs" data-ext="text" data-title="text"><pre><code><span class="line">노드A가 보내는 ID: 0 1 0 0 ...</span>
<span class="line">노드B가 보내는 ID: 0 1 1 0 ...</span>
<span class="line">                         ↑</span>
<span class="line">                   이 비트에서 충돌</span>
<span class="line">                   노드A(0=Dominant) 승리</span>
<span class="line">                   노드B는 재전송 대기</span>
<span class="line"></span></code></pre><div class="line-numbers" aria-hidden="true" style="counter-reset:line-number 0;"><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div><div class="line-number"></div></div></div><p>충돌이 발생해도 <strong>전송 중인 메시지는 손상되지 않고</strong> 우선순위가 높은 메시지가 그대로 전송된다. 이것이 CAN 중재의 핵심이다.</p><h3 id="_3-4-높은-신뢰성-—-에러-검출-및-복구" tabindex="-1"><a class="header-anchor" href="#_3-4-높은-신뢰성-—-에러-검출-및-복구"><span>3.4 높은 신뢰성 — 에러 검출 및 복구</span></a></h3><p>CAN은 5가지 에러 검출 메커니즘을 내장한다.</p><table><thead><tr><th>에러 종류</th><th>검출 방법</th></tr></thead><tbody><tr><td>비트 에러</td><td>전송하며 동시에 버스 읽기, 내가 보낸 값과 다르면 에러</td></tr><tr><td>스터프 에러</td><td>같은 비트가 5개 연속이면 에러 (비트 스터핑 규칙 위반)</td></tr><tr><td>CRC 에러</td><td>수신된 CRC가 계산값과 다르면 에러</td></tr><tr><td>형식 에러</td><td>프레임 형식이 규격과 다르면 에러</td></tr><tr><td>ACK 에러</td><td>수신자가 ACK를 보내지 않으면 에러</td></tr></tbody></table><p>에러가 감지되면 에러 프레임을 전송해 버스에 알리고, 자동으로 재전송한다. 노드가 과도하게 에러를 일으키면 <strong>Bus-Off 상태</strong>로 전환되어 버스 보호도 된다.</p><hr><h2 id="_4-can-vs-다른-통신-방식" tabindex="-1"><a class="header-anchor" href="#_4-can-vs-다른-통신-방식"><span>4. CAN vs 다른 통신 방식</span></a></h2><p>농기계와 자동차 분야에서 자주 언급되는 통신 방식들과 CAN을 비교한다.</p><table><thead><tr><th>항목</th><th>CAN</th><th>RS-485</th><th>LIN</th><th>FlexRay</th><th>Automotive Ethernet</th></tr></thead><tbody><tr><td>표준</td><td>ISO 11898</td><td>EIA-485</td><td>ISO 17987</td><td>ISO 17458</td><td>IEEE 802.3</td></tr><tr><td>최대 속도</td><td>1 Mbps</td><td>10 Mbps</td><td>20 kbps</td><td>10 Mbps</td><td>100 Mbps ~ 1 Gbps</td></tr><tr><td>토폴로지</td><td>선형 버스</td><td>선형 버스</td><td>단일 마스터 버스</td><td>이중 채널 버스</td><td>스타/링</td></tr><tr><td>배선 수</td><td>2선</td><td>2선</td><td>1선</td><td>4선</td><td>2선(UTP)</td></tr><tr><td>마스터 구조</td><td>멀티마스터</td><td>멀티마스터</td><td>단일마스터</td><td>멀티마스터</td><td>멀티마스터</td></tr><tr><td>실시간성</td><td>높음</td><td>중간</td><td>낮음</td><td>매우 높음</td><td>높음(TSN)</td></tr><tr><td>비용</td><td>낮음</td><td>낮음</td><td>매우 낮음</td><td>높음</td><td>중간</td></tr><tr><td>주요 용도</td><td>ECU 제어, ISOBUS</td><td>산업 자동화</td><td>시트·미러·조명</td><td>고안전 시스템</td><td>ADAS, 인포테인먼트</td></tr></tbody></table><p><strong>선택 기준 요약:</strong></p><ul><li><strong>단순하고 저비용</strong>: LIN (창문, 좌석 등 저속 기능)</li><li><strong>ECU 제어, 안정성</strong>: CAN (엔진, 브레이크, ISOBUS)</li><li><strong>고속 + 높은 안전성</strong>: FlexRay (전자식 파워트레인, X-by-wire)</li><li><strong>영상·대용량 데이터</strong>: Automotive Ethernet (카메라, 라이다)</li></ul><p>현재 자동차 한 대에는 CAN, LIN, Automotive Ethernet이 모두 함께 사용된다. 농기계에서는 CAN 기반의 ISOBUS가 핵심 표준이다.</p><hr><div class="hint-container tip"><p class="hint-container-title">핵심 정리</p><ul><li>CAN은 1986년 Bosch가 개발한 2선 직렬 통신 프로토콜로 ISO 11898로 표준화되었다.</li><li>자동차, 농기계, 산업기계, 의료장비 등 폭넓게 사용된다.</li><li>멀티마스터: 어떤 노드든 자유롭게 전송 가능.</li><li>메시지 기반 브로드캐스트: 수신자 주소 없이 ID로 메시지 종류를 식별.</li><li>중재(AMP): ID 값이 낮을수록 우선순위가 높고, 충돌 없이 고우선순위 메시지가 전송된다.</li><li>5가지 에러 검출 메커니즘으로 높은 신뢰성을 보장한다.</li></ul></div><h2 id="다음-챕터" tabindex="-1"><a class="header-anchor" href="#다음-챕터"><span>다음 챕터</span></a></h2><ul><li>다음 : <a href="/study/isobus/03-can-physical">CAN 물리 계층</a></li></ul>`,45)]))}const c=n(s,[["render",r],["__file","02-can-intro.html.vue"]]),o=JSON.parse('{"path":"/study/isobus/02-can-intro.html","title":"CAN 통신 입문","lang":"en-US","frontmatter":{"title":"CAN 통신 입문","description":"Bosch가 설계한 CAN의 탄생 배경, 핵심 특징, 그리고 다른 통신 방식과의 비교를 이해한다.","date":"2026-04-13T00:00:00.000Z","tags":["ISOBUS","CAN","ECU","통신프로토콜"],"prev":"/study/isobus/01-communication-basics","next":"/study/isobus/03-can-physical"},"headers":[{"level":1,"title":"CAN 통신 입문","slug":"can-통신-입문","link":"#can-통신-입문","children":[{"level":2,"title":"1. CAN이란","slug":"_1-can이란","link":"#_1-can이란","children":[]},{"level":2,"title":"2. CAN을 쓰는 곳","slug":"_2-can을-쓰는-곳","link":"#_2-can을-쓰는-곳","children":[]},{"level":2,"title":"3. CAN의 핵심 특징","slug":"_3-can의-핵심-특징","link":"#_3-can의-핵심-특징","children":[{"level":3,"title":"3.1 멀티마스터 (Multi-Master)","slug":"_3-1-멀티마스터-multi-master","link":"#_3-1-멀티마스터-multi-master","children":[]},{"level":3,"title":"3.2 메시지 기반 브로드캐스트","slug":"_3-2-메시지-기반-브로드캐스트","link":"#_3-2-메시지-기반-브로드캐스트","children":[]},{"level":3,"title":"3.3 우선순위 기반 중재 (CSMA/CD+AMP)","slug":"_3-3-우선순위-기반-중재-csma-cd-amp","link":"#_3-3-우선순위-기반-중재-csma-cd-amp","children":[]},{"level":3,"title":"3.4 높은 신뢰성 — 에러 검출 및 복구","slug":"_3-4-높은-신뢰성-—-에러-검출-및-복구","link":"#_3-4-높은-신뢰성-—-에러-검출-및-복구","children":[]}]},{"level":2,"title":"4. CAN vs 다른 통신 방식","slug":"_4-can-vs-다른-통신-방식","link":"#_4-can-vs-다른-통신-방식","children":[]},{"level":2,"title":"다음 챕터","slug":"다음-챕터","link":"#다음-챕터","children":[]}]}],"git":{},"filePathRelative":"_study/isobus/02-can-intro.md"}');export{c as comp,o as data};
