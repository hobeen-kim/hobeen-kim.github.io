import{_ as e,c as r,d as n,o as s}from"./app-CEg4EI9g.js";const l={};function d(i,t){return s(),r("div",null,t[0]||(t[0]=[n(`<h1 id="isobus-네트워크-관리" tabindex="-1"><a class="header-anchor" href="#isobus-네트워크-관리"><span>ISOBUS 네트워크 관리</span></a></h1><div class="hint-container info"><p class="hint-container-title">학습 목표</p><ul><li>ISOBUS의 주소 클레임 방식과 CF(Control Function) 개념을 설명할 수 있다.</li><li>Working Set Master와 Member의 관계를 도식으로 이해한다.</li><li>DM1~DM3 진단 메시지의 역할과 SPN+FMI 조합을 구분할 수 있다.</li><li>전원 ON부터 통신 완료까지의 시간 흐름을 설명할 수 있다.</li></ul></div><hr><h2 id="_1-주소-클레임-isobus-방식" tabindex="-1"><a class="header-anchor" href="#_1-주소-클레임-isobus-방식"><span>1. 주소 클레임 (ISOBUS 방식)</span></a></h2><p>ISOBUS의 주소 클레임은 J1939의 방식을 기반으로 하되, 농업 기계에 맞게 확장된 규칙을 적용한다.</p><h3 id="cf-control-function" tabindex="-1"><a class="header-anchor" href="#cf-control-function"><span>CF (Control Function)</span></a></h3><p>ISOBUS에서는 네트워크에 참여하는 모든 장치를 <strong>CF(Control Function)</strong>라고 부른다. 하나의 물리적 ECU가 여러 CF를 포함할 수도 있다. 각 CF는 독립적인 주소를 가진다.</p><h3 id="주소-범위" tabindex="-1"><a class="header-anchor" href="#주소-범위"><span>주소 범위</span></a></h3><table><thead><tr><th>주소 범위</th><th>용도</th></tr></thead><tbody><tr><td>0 ~ 127</td><td>고정 주소 (특정 기능에 예약)</td></tr><tr><td>128 ~ 247</td><td><strong>Self-Configurable 주소</strong> (동적 협상)</td></tr><tr><td>248 ~ 253</td><td>산업별 예약</td></tr><tr><td>254</td><td>Null Address (주소 미확정 상태)</td></tr><tr><td>255</td><td>Global Address (브로드캐스트)</td></tr></tbody></table><p>ISOBUS 작업기 ECU는 대부분 <strong>128~247</strong> 범위의 Self-Configurable 주소를 사용한다. 이 범위의 주소는 여러 장치가 동시에 원할 경우 NAME 값의 우선순위로 자동 협상된다.</p><h3 id="주소-클레임-흐름" tabindex="-1"><a class="header-anchor" href="#주소-클레임-흐름"><span>주소 클레임 흐름</span></a></h3><pre class="mermaid">sequenceDiagram
    participant ECU_A as ECU A&lt;br&gt;(NAME: 낮은 값)
    participant ECU_B as ECU B&lt;br&gt;(NAME: 높은 값)
    participant BUS as ISOBUS

    ECU_A-&gt;&gt;BUS: Request for Address Claimed&lt;br&gt;(주소 128 원함)
    ECU_B-&gt;&gt;BUS: Request for Address Claimed&lt;br&gt;(주소 128 원함)

    Note over ECU_A,ECU_B: 충돌 발생 — 두 ECU가 같은 주소 요청

    ECU_A-&gt;&gt;BUS: Address Claimed (128)&lt;br&gt;NAME = 낮은 값
    ECU_B-&gt;&gt;BUS: Address Claimed (128)&lt;br&gt;NAME = 높은 값

    Note over ECU_A,ECU_B: NAME 값 비교: 낮은 값이 우선권 획득

    ECU_A-&gt;&gt;BUS: Address Claimed (128) 유지&lt;br&gt;주소 128 확정
    ECU_B-&gt;&gt;BUS: Cannot Claim Address (128)&lt;br&gt;다른 주소(129)로 재시도
    ECU_B-&gt;&gt;BUS: Address Claimed (129) 확정
</pre><hr><h2 id="_2-working-set" tabindex="-1"><a class="header-anchor" href="#_2-working-set"><span>2. Working Set</span></a></h2><p>작업기(Implement)는 내부에 여러 ECU를 포함할 수 있다. 예를 들어 파종기(Seeder)는 메인 제어 ECU, 섹션 밸브 ECU, 속도 센서 ECU를 각각 가질 수 있다. 이 ECU들을 하나의 논리적 단위로 묶는 것이 <strong>Working Set</strong>이다.</p><h3 id="마스터-멤버-관계" tabindex="-1"><a class="header-anchor" href="#마스터-멤버-관계"><span>마스터-멤버 관계</span></a></h3><pre class="mermaid">graph TD
    subgraph Working_Set_파종기
        WSM[&quot;Working Set Master&lt;br&gt;파종기 메인 ECU&lt;br&gt;주소: 132&lt;br&gt;─────────────&lt;br&gt;VT·TC와 직접 통신&lt;br&gt;작업기 대표&quot;]

        M1[&quot;Working Set Member 1&lt;br&gt;섹션 밸브 ECU&lt;br&gt;주소: 133&lt;br&gt;─────────────&lt;br&gt;좌/우 섹션 개폐 제어&quot;]

        M2[&quot;Working Set Member 2&lt;br&gt;속도 센서 ECU&lt;br&gt;주소: 134&lt;br&gt;─────────────&lt;br&gt;지면 속도 측정 및 보고&quot;]

        M3[&quot;Working Set Member 3&lt;br&gt;비료 탱크 ECU&lt;br&gt;주소: 135&lt;br&gt;─────────────&lt;br&gt;잔량 센서, 경보&quot;]

        WSM -- &quot;내부 제어 명령&quot; --&gt; M1
        WSM -- &quot;센서 값 수신&quot; --&gt; M2
        WSM -- &quot;잔량 모니터링&quot; --&gt; M3
    end

    VT[&quot;VT&lt;br&gt;(트랙터 화면)&quot;] -- &quot;UI 데이터 요청&quot; --&gt; WSM
    TC[&quot;TC&lt;br&gt;(작업 컨트롤러)&quot;] -- &quot;섹션 명령&quot; --&gt; WSM
</pre><h3 id="working-set-선언-메시지-pgn-65070" tabindex="-1"><a class="header-anchor" href="#working-set-선언-메시지-pgn-65070"><span>Working Set 선언 메시지 (PGN 65070)</span></a></h3><p>WSM은 네트워크에 참여한 후 <strong>PGN 65070 (Working Set Master)</strong>를 브로드캐스트하여 자신이 마스터임을 선언한다. 이 메시지에는 Working Set에 속한 멤버 수가 포함된다.</p><p>멤버 ECU들은 <strong>PGN 65075 (Working Set Member)</strong>를 전송하여 자신이 특정 마스터에 속함을 알린다.</p><p>VT와 TC는 이 메시지를 수신하여 작업기의 구조를 파악하고, WSM을 통해서만 작업기와 통신한다.</p><hr><h2 id="_3-진단-메시지" tabindex="-1"><a class="header-anchor" href="#_3-진단-메시지"><span>3. 진단 메시지</span></a></h2><p>ISOBUS는 ISO 11783-12를 통해 표준화된 진단 메시지를 정의한다. J1939의 진단 메시지 체계를 그대로 사용한다.</p><h3 id="고장-코드-구조-spn-fmi" tabindex="-1"><a class="header-anchor" href="#고장-코드-구조-spn-fmi"><span>고장 코드 구조: SPN + FMI</span></a></h3><p>모든 고장은 <strong>SPN(Suspect Parameter Number)</strong>과 <strong>FMI(Failure Mode Identifier)</strong>의 조합으로 식별한다.</p><ul><li><strong>SPN</strong>: 어떤 파라미터에 문제가 생겼는지 (예: SPN 100 = 엔진 오일 압력)</li><li><strong>FMI</strong>: 어떤 종류의 고장인지 (예: FMI 1 = 데이터 낮음, FMI 3 = 전압 높음)</li></ul><h3 id="주요-진단-메시지" tabindex="-1"><a class="header-anchor" href="#주요-진단-메시지"><span>주요 진단 메시지</span></a></h3><table><thead><tr><th>메시지</th><th>PGN</th><th>이름</th><th>설명</th></tr></thead><tbody><tr><td>DM1</td><td>65226</td><td>Active Diagnostic Troubles</td><td>현재 발생 중인 활성 고장 코드 목록</td></tr><tr><td>DM2</td><td>65227</td><td>Previously Active Diagnostics</td><td>이전에 발생했다가 해소된 고장 코드</td></tr><tr><td>DM3</td><td>65228</td><td>Diagnostic Data Clear</td><td>저장된 고장 코드 초기화 요청</td></tr></tbody></table><pre class="mermaid">graph LR
    subgraph 진단_메시지_흐름
        FAULT[고장 발생&lt;br&gt;SPN+FMI 감지] --&gt; DM1[DM1 전송&lt;br&gt;활성 고장 코드]
        DM1 --&gt; VT_WARN[VT 화면에&lt;br&gt;경고 표시]
        FAULT_CLEAR[고장 해소] --&gt; DM2[DM2로 이동&lt;br&gt;이전 고장 기록]
        TECH[정비사 요청] --&gt; DM3[DM3 전송&lt;br&gt;고장 코드 초기화]
        DM3 --&gt; DM2_CLEAR[DM2 기록 삭제]
    end
</pre><h3 id="fmi-주요-값" tabindex="-1"><a class="header-anchor" href="#fmi-주요-값"><span>FMI 주요 값</span></a></h3><table><thead><tr><th>FMI</th><th>의미</th></tr></thead><tbody><tr><td>0</td><td>데이터 유효 범위 초과 (높음)</td></tr><tr><td>1</td><td>데이터 유효 범위 초과 (낮음)</td></tr><tr><td>2</td><td>데이터 불안정 / 간헐적</td></tr><tr><td>3</td><td>전압 높음 / 단락 (High)</td></tr><tr><td>4</td><td>전압 낮음 / 단락 (Low)</td></tr><tr><td>5</td><td>전류 낮음 / 단선</td></tr><tr><td>6</td><td>전류 높음 / 단락 (GND)</td></tr><tr><td>12</td><td>고장 모드 불명확</td></tr><tr><td>19</td><td>수신 네트워크 데이터 오류</td></tr></tbody></table><hr><h2 id="_4-네트워크-관리-타임라인" tabindex="-1"><a class="header-anchor" href="#_4-네트워크-관리-타임라인"><span>4. 네트워크 관리 타임라인</span></a></h2><p>전원을 켠 순간부터 ISOBUS 통신이 완전히 확립될 때까지의 시간 흐름이다.</p><pre class="mermaid">gantt
    title ISOBUS 네트워크 초기화 타임라인
    dateFormat  ss.SSS
    axisFormat  %S.%L s

    section 전원 / 하드웨어
    전원 ON / 버스 안정화      : 00.000, 50ms

    section 주소 클레임
    모든 ECU 주소 클레임 시작  : 00.050, 50ms
    주소 충돌 협상             : 00.100, 100ms
    주소 클레임 완료 (~250ms)  : milestone, 00.250, 0ms

    section Working Set
    WSM PGN 65070 브로드캐스트 : 00.250, 100ms
    Member PGN 65075 응답      : 00.350, 150ms
    Working Set 구성 완료 (~1s): milestone, 01.000, 0ms

    section VT 연결
    VT Status 수신             : 01.000, 200ms
    Object Pool 전송 시작      : 01.200, 300ms
    Object Pool 전송 완료      : milestone, 01.500, 0ms

    section 정상 동작
    TC Device Descriptor 교환  : 01.500, 200ms
    정상 동작 시작 (~2s)       : milestone, 02.000, 0ms
</pre><h3 id="타임라인-요약" tabindex="-1"><a class="header-anchor" href="#타임라인-요약"><span>타임라인 요약</span></a></h3><table><thead><tr><th>시점</th><th>이벤트</th></tr></thead><tbody><tr><td>0 ms</td><td>전원 ON, 버스 전압 안정화</td></tr><tr><td>~50 ms</td><td>각 ECU 주소 클레임 시작</td></tr><tr><td>~250 ms</td><td>모든 ECU 주소 확정 완료</td></tr><tr><td>~250 ms</td><td>WSM Working Set 선언 (PGN 65070)</td></tr><tr><td>~1,000 ms</td><td>Working Set 구성 완료</td></tr><tr><td>~1,000 ms</td><td>VT Status 수신 시작</td></tr><tr><td>~1,500 ms</td><td>Object Pool 전송 완료, 화면 표시 시작</td></tr><tr><td>~2,000 ms</td><td>TC Device Descriptor 완료, 전체 통신 확립</td></tr></tbody></table><blockquote><p><strong>실제 현장에서의 차이</strong>: Object Pool 크기, ECU 수, 버스 부하에 따라 타임라인은 달라진다. 복잡한 작업기의 경우 Object Pool 전송만 수 초가 걸릴 수 있다.</p></blockquote><hr><blockquote><p><strong>핵심 정리</strong></p><ul><li>ISOBUS에서 ECU는 CF(Control Function)라 불리며, Self-Configurable 주소(128~247)를 NAME 우선순위로 동적 협상한다.</li><li>Working Set은 작업기 내 여러 ECU를 하나의 논리 단위로 묶으며, WSM이 VT·TC와의 모든 통신을 대표한다.</li><li>DM1은 현재 활성 고장, DM2는 이전 고장 이력, DM3는 고장 코드 초기화 명령이다.</li><li>전원 ON 후 약 2초 안에 주소 클레임 → Working Set → VT 연결 → 정상 동작 순으로 초기화가 완료된다.</li></ul></blockquote><hr><h2 id="다음-챕터" tabindex="-1"><a class="header-anchor" href="#다음-챕터"><span>다음 챕터</span></a></h2><ul><li>다음 : <a href="/study/isobus/15-vt-basics">Virtual Terminal 기초</a></li></ul>`,44)]))}const o=e(l,[["render",d],["__file","14-isobus-network-mgmt.html.vue"]]),g=JSON.parse('{"path":"/study/isobus/14-isobus-network-mgmt.html","title":"ISOBUS 네트워크 관리","lang":"en-US","frontmatter":{"title":"ISOBUS 네트워크 관리","description":"ISOBUS의 주소 클레임 방식, Working Set 개념, 진단 메시지(DM), 네트워크 초기화 타임라인을 이해한다.","date":"2026-04-13T00:00:00.000Z","tags":["ISOBUS","ISO11783","AddressClaim","WorkingSet","Diagnostics","DM1"],"prev":"/study/isobus/13-isobus-architecture","next":null},"headers":[{"level":1,"title":"ISOBUS 네트워크 관리","slug":"isobus-네트워크-관리","link":"#isobus-네트워크-관리","children":[{"level":2,"title":"1. 주소 클레임 (ISOBUS 방식)","slug":"_1-주소-클레임-isobus-방식","link":"#_1-주소-클레임-isobus-방식","children":[{"level":3,"title":"CF (Control Function)","slug":"cf-control-function","link":"#cf-control-function","children":[]},{"level":3,"title":"주소 범위","slug":"주소-범위","link":"#주소-범위","children":[]},{"level":3,"title":"주소 클레임 흐름","slug":"주소-클레임-흐름","link":"#주소-클레임-흐름","children":[]}]},{"level":2,"title":"2. Working Set","slug":"_2-working-set","link":"#_2-working-set","children":[{"level":3,"title":"마스터-멤버 관계","slug":"마스터-멤버-관계","link":"#마스터-멤버-관계","children":[]},{"level":3,"title":"Working Set 선언 메시지 (PGN 65070)","slug":"working-set-선언-메시지-pgn-65070","link":"#working-set-선언-메시지-pgn-65070","children":[]}]},{"level":2,"title":"3. 진단 메시지","slug":"_3-진단-메시지","link":"#_3-진단-메시지","children":[{"level":3,"title":"고장 코드 구조: SPN + FMI","slug":"고장-코드-구조-spn-fmi","link":"#고장-코드-구조-spn-fmi","children":[]},{"level":3,"title":"주요 진단 메시지","slug":"주요-진단-메시지","link":"#주요-진단-메시지","children":[]},{"level":3,"title":"FMI 주요 값","slug":"fmi-주요-값","link":"#fmi-주요-값","children":[]}]},{"level":2,"title":"4. 네트워크 관리 타임라인","slug":"_4-네트워크-관리-타임라인","link":"#_4-네트워크-관리-타임라인","children":[{"level":3,"title":"타임라인 요약","slug":"타임라인-요약","link":"#타임라인-요약","children":[]}]},{"level":2,"title":"다음 챕터","slug":"다음-챕터","link":"#다음-챕터","children":[]}]}],"git":{},"filePathRelative":"_study/isobus/14-isobus-network-mgmt.md"}');export{o as comp,g as data};
